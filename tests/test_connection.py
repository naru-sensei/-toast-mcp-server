"""
Tests for the client connection management implementation.
"""

import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from src.server.connection import (
    ClientConnection, ConnectionManager, run_server
)
from src.mcp.protocol import (
    MCPMessage, NotificationMessage, ResponseMessage, ErrorMessage,
    PingMessage, PongMessage, MessageType, NotificationType
)


class TestClientConnection(unittest.TestCase):
    """Test cases for the ClientConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = AsyncMock(spec=asyncio.StreamReader)
        self.writer = AsyncMock(spec=asyncio.StreamWriter)
        self.server = MagicMock(spec=ConnectionManager)
        
        self.writer.get_extra_info.return_value = ('127.0.0.1', 12345)
        
        self.client = ClientConnection(
            self.reader, self.writer, "test_client", self.server
        )
    
    @patch('src.server.connection.logger')
    async def test_handle_connection(self, mock_logger):
        """Test handling a client connection."""
        self.reader.readline.side_effect = [
            b'{"type": "ping", "data": {}}\n',
            b''
        ]
        
        await self.client.handle()
        
        self.reader.readline.assert_called()
        
        self.assertFalse(self.client.connected)
        self.server.remove_client.assert_called_once_with("test_client")
        self.writer.close.assert_called_once()
        self.writer.wait_closed.assert_called_once()
    
    @patch('src.server.connection.logger')
    async def test_process_message_ping(self, mock_logger):
        """Test processing a ping message."""
        await self.client._process_message('{"type": "ping", "data": {}}')
        
        self.writer.write.assert_called_once()
        written_data = self.writer.write.call_args[0][0].decode()
        self.assertIn('"type": "pong"', written_data)
    
    @patch('src.server.connection.show_notification')
    @patch('src.server.connection.logger')
    async def test_process_message_notification(self, mock_logger, mock_show_notification):
        """Test processing a notification message."""
        mock_show_notification.return_value = True
        
        await self.client._process_message(
            '{"type": "notification", "data": {"title": "Test", "message": "Test message"}}'
        )
        
        mock_show_notification.assert_called_once_with(
            "Test", "Test message", "info", 5
        )
        
        self.writer.write.assert_called_once()
        written_data = self.writer.write.call_args[0][0].decode()
        self.assertIn('"type": "response"', written_data)
        self.assertIn('"success": true', written_data)
    
    @patch('src.server.connection.logger')
    async def test_process_message_invalid_json(self, mock_logger):
        """Test processing an invalid JSON message."""
        await self.client._process_message('invalid json')
        
        self.writer.write.assert_called_once()
        written_data = self.writer.write.call_args[0][0].decode()
        self.assertIn('"type": "error"', written_data)
        self.assertIn('"code": 400', written_data)
    
    @patch('src.server.connection.logger')
    async def test_send_message(self, mock_logger):
        """Test sending a message to the client."""
        message = PingMessage()
        
        await self.client.send_message(message)
        
        self.writer.write.assert_called_once()
        self.writer.drain.assert_called_once()
        
        written_data = self.writer.write.call_args[0][0].decode()
        self.assertIn('"type": "ping"', written_data)
    
    @patch('src.server.connection.logger')
    async def test_close(self, mock_logger):
        """Test closing the client connection."""
        await self.client.close()
        
        self.assertFalse(self.client.connected)
        self.server.remove_client.assert_called_once_with("test_client")
        self.writer.close.assert_called_once()
        self.writer.wait_closed.assert_called_once()
        
        self.server.remove_client.reset_mock()
        self.writer.close.reset_mock()
        self.writer.wait_closed.reset_mock()
        
        await self.client.close()
        
        self.server.remove_client.assert_not_called()
        self.writer.close.assert_not_called()
        self.writer.wait_closed.assert_not_called()


class TestConnectionManager(unittest.TestCase):
    """Test cases for the ConnectionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ConnectionManager("127.0.0.1", 8765)
    
    @patch('src.server.connection.asyncio.start_server')
    @patch('src.server.connection.logger')
    async def test_start_server(self, mock_logger, mock_start_server):
        """Test starting the server."""
        mock_server = AsyncMock()
        mock_server.sockets = [MagicMock()]
        mock_server.sockets[0].getsockname.return_value = ('127.0.0.1', 8765)
        mock_start_server.return_value = mock_server
        
        task = asyncio.create_task(self.manager.start())
        
        await asyncio.sleep(0.1)
        
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        mock_start_server.assert_called_once_with(
            self.manager._handle_new_connection, "127.0.0.1", 8765
        )
    
    @patch('src.server.connection.ClientConnection')
    @patch('src.server.connection.asyncio.create_task')
    @patch('src.server.connection.logger')
    async def test_handle_new_connection(self, mock_logger, mock_create_task, mock_client_connection):
        """Test handling a new connection."""
        reader = AsyncMock(spec=asyncio.StreamReader)
        writer = AsyncMock(spec=asyncio.StreamWriter)
        mock_client = MagicMock()
        mock_client_connection.return_value = mock_client
        
        await self.manager._handle_new_connection(reader, writer)
        
        mock_client_connection.assert_called_once_with(
            reader, writer, "client_1", self.manager
        )
        
        self.assertEqual(len(self.manager.clients), 1)
        self.assertEqual(self.manager.clients["client_1"], mock_client)
        
        mock_create_task.assert_called_once_with(mock_client.handle())
    
    @patch('src.server.connection.logger')
    def test_remove_client(self, mock_logger):
        """Test removing a client."""
        self.manager.clients["test_client"] = MagicMock()
        
        self.manager.remove_client("test_client")
        
        self.assertEqual(len(self.manager.clients), 0)
        
        self.manager.remove_client("non_existent_client")
    
    @patch('src.server.connection.logger')
    async def test_broadcast(self, mock_logger):
        """Test broadcasting a message to all clients."""
        client1 = MagicMock()
        client1.send_message = AsyncMock()
        client2 = MagicMock()
        client2.send_message = AsyncMock()
        
        self.manager.clients["client1"] = client1
        self.manager.clients["client2"] = client2
        
        message = PingMessage()
        
        await self.manager.broadcast(message)
        
        client1.send_message.assert_called_once_with(message)
        client2.send_message.assert_called_once_with(message)
        
        client1.send_message.reset_mock()
        client2.send_message.reset_mock()
        
        await self.manager.broadcast(message, exclude="client1")
        
        client1.send_message.assert_not_called()
        client2.send_message.assert_called_once_with(message)
    
    @patch('src.server.connection.logger')
    async def test_stop(self, mock_logger):
        """Test stopping the server."""
        client1 = MagicMock()
        client1.close = AsyncMock()
        client2 = MagicMock()
        client2.close = AsyncMock()
        
        self.manager.clients["client1"] = client1
        self.manager.clients["client2"] = client2
        
        self.manager.server = MagicMock()
        self.manager.server.wait_closed = AsyncMock()
        
        await self.manager.stop()
        
        client1.close.assert_called_once()
        client2.close.assert_called_once()
        
        self.manager.server.close.assert_called_once()
        self.manager.server.wait_closed.assert_called_once()


@patch('src.server.connection.ConnectionManager')
@patch('src.server.connection.logging')
async def test_run_server(mock_logging, mock_manager_class):
    """Test running the server."""
    mock_manager = AsyncMock()
    mock_manager_class.return_value = mock_manager
    
    await run_server("127.0.0.1", 8765)
    
    mock_logging.basicConfig.assert_called_once()
    
    mock_manager_class.assert_called_once_with("127.0.0.1", 8765)
    mock_manager.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
