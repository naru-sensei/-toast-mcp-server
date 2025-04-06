"""
MCP (Model Context Protocol) implementation for toast-mcp-server.

This module defines the protocol specification and message handling for
communication between MCP clients and the notification server.
"""

import json
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enum defining the types of messages in the MCP protocol."""
    NOTIFICATION = "notification"
    RESPONSE = "response"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class NotificationType(Enum):
    """Enum defining the types of notifications supported."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class MCPMessage:
    """Base class for MCP protocol messages."""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any] = None):
        """
        Initialize a new MCP message.
        
        Args:
            msg_type: The type of message
            data: Optional data payload for the message
        """
        self.msg_type = msg_type
        self.data = data or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary representation."""
        return {
            "type": self.msg_type.value,
            "data": self.data
        }
    
    def to_json(self) -> str:
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            An MCPMessage instance
            
        Raises:
            ValueError: If the message type is invalid or required fields are missing
        """
        if "type" not in data:
            raise ValueError("Message missing required 'type' field")
        
        try:
            msg_type = MessageType(data["type"])
        except ValueError:
            raise ValueError(f"Invalid message type: {data['type']}")
        
        msg_data = data.get("data", {})
        
        if msg_type == MessageType.NOTIFICATION:
            return NotificationMessage.from_dict(data)
        elif msg_type == MessageType.RESPONSE:
            return ResponseMessage.from_dict(data)
        elif msg_type == MessageType.ERROR:
            return ErrorMessage.from_dict(data)
        elif msg_type == MessageType.PING:
            return PingMessage()
        elif msg_type == MessageType.PONG:
            return PongMessage()
        
        return cls(msg_type, msg_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """
        Create a message from a JSON string.
        
        Args:
            json_str: JSON string containing message data
            
        Returns:
            An MCPMessage instance
            
        Raises:
            ValueError: If the JSON is invalid or the message format is incorrect
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        
        return cls.from_dict(data)


class NotificationMessage(MCPMessage):
    """Message for sending notifications to the server."""
    
    def __init__(self, 
                 title: str, 
                 message: str, 
                 notification_type: NotificationType = NotificationType.INFO,
                 duration: int = 5,
                 client_id: str = None,
                 icon: str = None,
                 actions: List[Dict[str, str]] = None):
        """
        Initialize a new notification message.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            notification_type: Type of notification (info, warning, error, success)
            duration: Duration to display the notification in seconds
            client_id: Optional identifier for the client sending the notification
            icon: Optional icon to display with the notification
            actions: Optional list of actions that can be taken on the notification
        """
        data = {
            "title": title,
            "message": message,
            "notification_type": notification_type.value,
            "duration": duration
        }
        
        if client_id:
            data["client_id"] = client_id
            
        if icon:
            data["icon"] = icon
            
        if actions:
            data["actions"] = actions
            
        super().__init__(MessageType.NOTIFICATION, data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationMessage':
        """Create a NotificationMessage from a dictionary."""
        msg_data = data.get("data", {})
        
        if "title" not in msg_data or "message" not in msg_data:
            raise ValueError("Notification message missing required fields: title and message")
        
        try:
            notification_type = NotificationType(msg_data.get("notification_type", "info"))
        except ValueError:
            notification_type = NotificationType.INFO
            logger.warning(f"Invalid notification type: {msg_data.get('notification_type')}, using INFO")
        
        return cls(
            title=msg_data["title"],
            message=msg_data["message"],
            notification_type=notification_type,
            duration=msg_data.get("duration", 5),
            client_id=msg_data.get("client_id"),
            icon=msg_data.get("icon"),
            actions=msg_data.get("actions")
        )


class ResponseMessage(MCPMessage):
    """Message for server responses to clients."""
    
    def __init__(self, success: bool, message: str = None, data: Dict[str, Any] = None):
        """
        Initialize a new response message.
        
        Args:
            success: Whether the operation was successful
            message: Optional message describing the result
            data: Optional additional data to include in the response
        """
        response_data = {
            "success": success
        }
        
        if message:
            response_data["message"] = message
            
        if data:
            response_data["data"] = data
            
        super().__init__(MessageType.RESPONSE, response_data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseMessage':
        """Create a ResponseMessage from a dictionary."""
        msg_data = data.get("data", {})
        
        if "success" not in msg_data:
            raise ValueError("Response message missing required field: success")
        
        return cls(
            success=msg_data["success"],
            message=msg_data.get("message"),
            data=msg_data.get("data")
        )


class ErrorMessage(MCPMessage):
    """Message for error responses."""
    
    def __init__(self, error_code: int, error_message: str, details: Any = None):
        """
        Initialize a new error message.
        
        Args:
            error_code: Numeric error code
            error_message: Human-readable error message
            details: Optional additional error details
        """
        error_data = {
            "code": error_code,
            "message": error_message
        }
        
        if details:
            error_data["details"] = details
            
        super().__init__(MessageType.ERROR, error_data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorMessage':
        """Create an ErrorMessage from a dictionary."""
        msg_data = data.get("data", {})
        
        if "code" not in msg_data or "message" not in msg_data:
            raise ValueError("Error message missing required fields: code and message")
        
        return cls(
            error_code=msg_data["code"],
            error_message=msg_data["message"],
            details=msg_data.get("details")
        )


class PingMessage(MCPMessage):
    """Message for ping requests."""
    
    def __init__(self):
        """Initialize a new ping message."""
        super().__init__(MessageType.PING)


class PongMessage(MCPMessage):
    """Message for pong responses."""
    
    def __init__(self):
        """Initialize a new pong message."""
        super().__init__(MessageType.PONG)


def parse_message(data: Union[str, Dict[str, Any]]) -> MCPMessage:
    """
    Parse a message from either a JSON string or a dictionary.
    
    Args:
        data: JSON string or dictionary containing message data
        
    Returns:
        An MCPMessage instance
        
    Raises:
        ValueError: If the message format is invalid
    """
    if isinstance(data, str):
        return MCPMessage.from_json(data)
    elif isinstance(data, dict):
        return MCPMessage.from_dict(data)
    else:
        raise ValueError(f"Unsupported message format: {type(data)}")
