"""
Command processing system for toast-mcp-server.

This module handles the processing of commands received from clients,
including command registration, validation, and execution.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List, Union, Tuple

from src.mcp.protocol import (
    MCPMessage, ResponseMessage, ErrorMessage, MessageType
)
from src.notification.toast import show_notification

logger = logging.getLogger(__name__)


CommandHandler = Callable[[Dict[str, Any], str], Awaitable[Tuple[bool, str, Optional[Dict[str, Any]]]]]
CommandValidator = Callable[[Dict[str, Any]], Tuple[bool, Optional[str]]]


class Command:
    """
    Represents a command that can be executed by the server.
    
    Commands are registered with the CommandProcessor and can be executed
    when received from clients.
    """
    
    def __init__(self, 
                 name: str, 
                 handler: CommandHandler, 
                 validator: Optional[CommandValidator] = None,
                 description: str = "",
                 requires_auth: bool = False):
        """
        Initialize a new command.
        
        Args:
            name: Name of the command
            handler: Function to handle the command execution
            validator: Optional function to validate command parameters
            description: Description of the command
            requires_auth: Whether the command requires authentication
        """
        self.name = name
        self.handler = handler
        self.validator = validator
        self.description = description
        self.requires_auth = requires_auth
    
    async def execute(self, params: Dict[str, Any], client_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Execute the command.
        
        Args:
            params: Parameters for the command
            client_id: ID of the client executing the command
            
        Returns:
            Tuple of (success, message, data)
        """
        if self.validator:
            is_valid, error = self.validator(params)
            if not is_valid:
                return False, f"Invalid parameters: {error}", None
        
        try:
            return await self.handler(params, client_id)
        except Exception as e:
            logger.error(f"Error executing command {self.name}: {str(e)}")
            return False, f"Error executing command: {str(e)}", None


class CommandProcessor:
    """
    Processes commands received from clients.
    
    This class manages the registration and execution of commands,
    as well as the handling of command responses.
    """
    
    def __init__(self):
        """Initialize the command processor."""
        self.commands: Dict[str, Command] = {}
        self.authenticated_clients: List[str] = []
        logger.info("Command processor initialized")
    
    def register_command(self, command: Command) -> None:
        """
        Register a command with the processor.
        
        Args:
            command: The command to register
        """
        self.commands[command.name] = command
        logger.debug(f"Registered command: {command.name}")
    
    def register_commands(self, commands: List[Command]) -> None:
        """
        Register multiple commands with the processor.
        
        Args:
            commands: List of commands to register
        """
        for command in commands:
            self.register_command(command)
    
    async def process_command(self, 
                             command_name: str, 
                             params: Dict[str, Any], 
                             client_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process a command.
        
        Args:
            command_name: Name of the command to execute
            params: Parameters for the command
            client_id: ID of the client executing the command
            
        Returns:
            Tuple of (success, message, data)
        """
        if command_name not in self.commands:
            return False, f"Unknown command: {command_name}", None
        
        command = self.commands[command_name]
        
        if command.requires_auth and client_id not in self.authenticated_clients:
            return False, "Authentication required", None
        
        return await command.execute(params, client_id)
    
    def authenticate_client(self, client_id: str) -> None:
        """
        Mark a client as authenticated.
        
        Args:
            client_id: ID of the client to authenticate
        """
        if client_id not in self.authenticated_clients:
            self.authenticated_clients.append(client_id)
            logger.debug(f"Client authenticated: {client_id}")
    
    def deauthenticate_client(self, client_id: str) -> None:
        """
        Remove a client's authentication.
        
        Args:
            client_id: ID of the client to deauthenticate
        """
        if client_id in self.authenticated_clients:
            self.authenticated_clients.remove(client_id)
            logger.debug(f"Client deauthenticated: {client_id}")



async def handle_show_notification(params: Dict[str, Any], client_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Handle the 'show_notification' command.
    
    Args:
        params: Parameters for the command
        client_id: ID of the client executing the command
        
    Returns:
        Tuple of (success, message, data)
    """
    title = params.get("title", "")
    message = params.get("message", "")
    notification_type = params.get("type", "info")
    duration = params.get("duration", 5)
    
    success = show_notification(title, message, notification_type, duration)
    
    if success:
        return True, "Notification displayed successfully", None
    else:
        return False, "Failed to display notification", None


async def handle_list_commands(params: Dict[str, Any], client_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Handle the 'list_commands' command.
    
    Args:
        params: Parameters for the command
        client_id: ID of the client executing the command
        
    Returns:
        Tuple of (success, message, data)
    """
    commands = [
        {"name": "show_notification", "description": "Display a Windows 10 toast notification"},
        {"name": "list_commands", "description": "List available commands"}
    ]
    
    return True, "Commands retrieved successfully", {"commands": commands}


def validate_show_notification(params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate parameters for the 'show_notification' command.
    
    Args:
        params: Parameters to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if "title" not in params:
        return False, "Missing required parameter: title"
    
    if "message" not in params:
        return False, "Missing required parameter: message"
    
    if not isinstance(params.get("title"), str):
        return False, "Title must be a string"
    
    if not isinstance(params.get("message"), str):
        return False, "Message must be a string"
    
    if "type" in params and params["type"] not in ["info", "warning", "error", "success"]:
        return False, "Invalid notification type"
    
    if "duration" in params and not isinstance(params["duration"], int):
        return False, "Duration must be an integer"
    
    return True, None


DEFAULT_COMMANDS = [
    Command(
        name="show_notification",
        handler=handle_show_notification,
        validator=validate_show_notification,
        description="Display a Windows 10 toast notification"
    ),
    Command(
        name="list_commands",
        handler=handle_list_commands,
        description="List available commands"
    )
]


command_processor = CommandProcessor()

command_processor.register_commands(DEFAULT_COMMANDS)


async def process_command_message(message_data: Dict[str, Any], client_id: str) -> MCPMessage:
    """
    Process a command message and return a response.
    
    Args:
        message_data: Dictionary containing the command message data
        client_id: ID of the client sending the command
        
    Returns:
        Response message to send back to the client
    """
    command_name = message_data.get("command")
    params = message_data.get("params", {})
    
    if not command_name:
        return ErrorMessage(400, "Missing command name")
    
    success, message, data = await command_processor.process_command(command_name, params, client_id)
    
    if success:
        return ResponseMessage(True, message, data)
    else:
        return ErrorMessage(400, message)
