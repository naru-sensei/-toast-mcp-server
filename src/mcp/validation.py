"""
Validation utilities for MCP protocol messages.

This module provides functions for validating MCP messages and their contents
to ensure they conform to the protocol specification.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union

from .protocol import NotificationType, MessageType


def validate_notification(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a notification message.
    
    Args:
        data: The notification message data to validate
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    if "title" not in data:
        return False, "Missing required field: title"
    
    if "message" not in data:
        return False, "Missing required field: message"
    
    if not isinstance(data["title"], str):
        return False, "Title must be a string"
    
    if len(data["title"]) > 100:
        return False, "Title exceeds maximum length of 100 characters"
    
    if not isinstance(data["message"], str):
        return False, "Message must be a string"
    
    if len(data["message"]) > 1000:
        return False, "Message exceeds maximum length of 1000 characters"
    
    if "notification_type" in data:
        try:
            NotificationType(data["notification_type"])
        except ValueError:
            valid_types = [t.value for t in NotificationType]
            return False, f"Invalid notification type. Must be one of: {', '.join(valid_types)}"
    
    if "duration" in data:
        if not isinstance(data["duration"], int):
            return False, "Duration must be an integer"
        
        if data["duration"] < 1 or data["duration"] > 60:
            return False, "Duration must be between 1 and 60 seconds"
    
    if "client_id" in data:
        if not isinstance(data["client_id"], str):
            return False, "Client ID must be a string"
        
        if not re.match(r'^[a-zA-Z0-9_\-\.]{1,50}$', data["client_id"]):
            return False, "Client ID contains invalid characters or exceeds maximum length"
    
    if "icon" in data and not isinstance(data["icon"], str):
        return False, "Icon must be a string"
    
    if "actions" in data:
        if not isinstance(data["actions"], list):
            return False, "Actions must be a list"
        
        for i, action in enumerate(data["actions"]):
            if not isinstance(action, dict):
                return False, f"Action at index {i} must be a dictionary"
            
            if "id" not in action:
                return False, f"Action at index {i} missing required field: id"
            
            if "text" not in action:
                return False, f"Action at index {i} missing required field: text"
            
            if not isinstance(action["id"], str) or not isinstance(action["text"], str):
                return False, f"Action id and text must be strings"
    
    return True, None


def validate_message(message_type: MessageType, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a message based on its type.
    
    Args:
        message_type: The type of message to validate
        data: The message data to validate
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    if message_type == MessageType.NOTIFICATION:
        return validate_notification(data)
    
    elif message_type == MessageType.RESPONSE:
        if "success" not in data:
            return False, "Response message missing required field: success"
        
        if not isinstance(data["success"], bool):
            return False, "Success field must be a boolean"
        
        return True, None
    
    elif message_type == MessageType.ERROR:
        if "code" not in data:
            return False, "Error message missing required field: code"
        
        if "message" not in data:
            return False, "Error message missing required field: message"
        
        if not isinstance(data["code"], int):
            return False, "Error code must be an integer"
        
        if not isinstance(data["message"], str):
            return False, "Error message must be a string"
        
        return True, None
    
    elif message_type in (MessageType.PING, MessageType.PONG):
        return True, None
    
    return False, f"Unknown message type: {message_type}"


def validate_message_format(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[MessageType]]:
    """
    Validate the format of a message.
    
    Args:
        data: The message data to validate
        
    Returns:
        A tuple of (is_valid, error_message, message_type)
    """
    if not isinstance(data, dict):
        return False, "Message must be a dictionary", None
    
    if "type" not in data:
        return False, "Message missing required field: type", None
    
    try:
        message_type = MessageType(data["type"])
    except ValueError:
        valid_types = [t.value for t in MessageType]
        return False, f"Invalid message type. Must be one of: {', '.join(valid_types)}", None
    
    if "data" not in data:
        data["data"] = {}  # Add empty data for types that don't require it
    
    if not isinstance(data["data"], dict):
        return False, "Message data must be a dictionary", None
    
    is_valid, error_message = validate_message(message_type, data["data"])
    
    return is_valid, error_message, message_type
