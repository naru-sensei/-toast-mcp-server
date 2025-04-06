"""
Client connection management for toast-mcp-server.

This module handles client connections, including connection establishment,
message handling, and connection termination.
"""

import asyncio
import logging
import json
from typing import Dict, Set, Any, Optional, Callable, Awaitable, List

from src.mcp.protocol import (
    MCPMessage, NotificationMessage, ResponseMessage, ErrorMessage,
    PingMessage, PongMessage, MessageType, parse_message
)
from src.mcp.validation import validate_message_format
from src.notification.toast import show_notification

logger = logging.getLogger(__name__)


class ClientConnection:
    """
    Represents a connection to a client.
    
    This class handles the communication with a single client, including
    receiving and sending messages.
    """
    
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, 
                 client_id: str, server: 'ConnectionManager'):
        """
        Initialize a new client connection.
        
        Args:
            reader: Stream reader for receiving data from the client
            writer: Stream writer for sending data to the client
            client_id: Unique identifier for the client
            server: Reference to the connection manager
        """
        self.reader = reader
        self.writer = writer
        self.client_id = client_id
        self.server = server
        self.connected = True
        self.addr = writer.get_extra_info('peername')
        logger.info(f"Client connected: {self.client_id} from {self.addr}")
    
    async def handle(self) -> None:
        """
        Handle the client connection.
        
        This method continuously reads messages from the client and processes them
        until the connection is closed.
        """
        try:
            while self.connected:
                data = await self.reader.readline()
                if not data:
                    break
                
                await self._process_message(data.decode().strip())
                
        except asyncio.CancelledError:
            logger.info(f"Connection handling cancelled for client: {self.client_id}")
        except Exception as e:
            logger.error(f"Error handling client {self.client_id}: {str(e)}")
        finally:
            await self.close()
    
    async def _process_message(self, data: str) -> None:
        """
        Process a message received from the client.
        
        Args:
            data: JSON string containing the message data
        """
        logger.debug(f"Received message from {self.client_id}: {data}")
        
        try:
            message_data = json.loads(data)
            is_valid, error, msg_type = validate_message_format(message_data)
            
            if not is_valid:
                await self.send_error(400, f"Invalid message format: {error}")
                return
            
            if msg_type == MessageType.NOTIFICATION:
                await self._handle_notification(message_data)
            elif msg_type == MessageType.PING:
                await self._handle_ping()
            else:
                await self.send_error(400, f"Unsupported message type: {msg_type.value}")
                
        except json.JSONDecodeError:
            await self.send_error(400, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message from {self.client_id}: {str(e)}")
            await self.send_error(500, "Internal server error")
    
    async def _handle_notification(self, message_data: Dict[str, Any]) -> None:
        """
        Handle a notification message.
        
        Args:
            message_data: Dictionary containing the notification message data
        """
        try:
            notification = NotificationMessage.from_dict(message_data)
            
            title = notification.data["title"]
            message = notification.data["message"]
            notification_type = notification.data.get("notification_type", "info")
            duration = notification.data.get("duration", 5)
            
            success = show_notification(title, message, notification_type, duration)
            
            if success:
                await self.send_response(True, "Notification displayed successfully")
            else:
                await self.send_response(False, "Failed to display notification")
                
        except Exception as e:
            logger.error(f"Error handling notification from {self.client_id}: {str(e)}")
            await self.send_error(500, f"Error handling notification: {str(e)}")
    
    async def _handle_ping(self) -> None:
        """Handle a ping message by sending a pong response."""
        try:
            pong = PongMessage()
            await self.send_message(pong)
            
        except Exception as e:
            logger.error(f"Error handling ping from {self.client_id}: {str(e)}")
            await self.send_error(500, f"Error handling ping: {str(e)}")
    
    async def send_message(self, message: MCPMessage) -> None:
        """
        Send a message to the client.
        
        Args:
            message: The message to send
        """
        try:
            json_str = message.to_json() + "\n"
            self.writer.write(json_str.encode())
            await self.writer.drain()
            
            logger.debug(f"Sent message to {self.client_id}: {message.msg_type.value}")
            
        except Exception as e:
            logger.error(f"Error sending message to {self.client_id}: {str(e)}")
            await self.close()
    
    async def send_response(self, success: bool, message: str = None, data: Dict[str, Any] = None) -> None:
        """
        Send a response message to the client.
        
        Args:
            success: Whether the operation was successful
            message: Optional message describing the result
            data: Optional additional data to include in the response
        """
        response = ResponseMessage(success, message, data)
        await self.send_message(response)
    
    async def send_error(self, error_code: int, error_message: str, details: Any = None) -> None:
        """
        Send an error message to the client.
        
        Args:
            error_code: Numeric error code
            error_message: Human-readable error message
            details: Optional additional error details
        """
        error = ErrorMessage(error_code, error_message, details)
        await self.send_message(error)
    
    async def close(self) -> None:
        """Close the client connection."""
        if not self.connected:
            return
        
        self.connected = False
        
        try:
            self.writer.close()
            await self.writer.wait_closed()
            
            self.server.remove_client(self.client_id)
            
            logger.info(f"Client disconnected: {self.client_id}")
            
        except Exception as e:
            logger.error(f"Error closing connection for {self.client_id}: {str(e)}")


class ConnectionManager:
    """
    Manages client connections to the server.
    
    This class handles the creation and management of client connections,
    including accepting new connections and broadcasting messages to clients.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        """
        Initialize the connection manager.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientConnection] = {}
        self.server = None
        self.next_client_id = 1
        logger.info(f"Connection manager initialized with host={host}, port={port}")
    
    async def start(self) -> None:
        """Start the server and begin accepting connections."""
        try:
            self.server = await asyncio.start_server(
                self._handle_new_connection, self.host, self.port
            )
            
            addr = self.server.sockets[0].getsockname()
            logger.info(f"Server started on {addr}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            raise
    
    async def _handle_new_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handle a new client connection.
        
        Args:
            reader: Stream reader for receiving data from the client
            writer: Stream writer for sending data to the client
        """
        client_id = f"client_{self.next_client_id}"
        self.next_client_id += 1
        
        client = ClientConnection(reader, writer, client_id, self)
        self.clients[client_id] = client
        
        asyncio.create_task(client.handle())
    
    def remove_client(self, client_id: str) -> None:
        """
        Remove a client from the connection manager.
        
        Args:
            client_id: ID of the client to remove
        """
        if client_id in self.clients:
            del self.clients[client_id]
            logger.debug(f"Removed client: {client_id}")
    
    async def broadcast(self, message: MCPMessage, exclude: Optional[str] = None) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
            exclude: Optional client ID to exclude from the broadcast
        """
        for client_id, client in list(self.clients.items()):
            if exclude and client_id == exclude:
                continue
            
            try:
                await client.send_message(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the server and close all client connections."""
        logger.info("Stopping server...")
        
        for client_id, client in list(self.clients.items()):
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client {client_id}: {str(e)}")
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Server stopped")


async def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """
    Run the MCP server.
    
    Args:
        host: Host address to bind to
        port: Port to listen on
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = ConnectionManager(host, port)
    await manager.start()
