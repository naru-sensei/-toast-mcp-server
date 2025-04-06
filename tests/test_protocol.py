"""
Tests for the MCP protocol implementation.
"""

import unittest
import json
from src.mcp.protocol import (
    MCPMessage, NotificationMessage, ResponseMessage, ErrorMessage,
    PingMessage, PongMessage, MessageType, NotificationType, parse_message
)
from src.mcp.validation import validate_message_format, validate_notification


class TestMCPProtocol(unittest.TestCase):
    """Test cases for the MCP protocol implementation."""
    
    def test_notification_message_creation(self):
        """Test creating a notification message."""
        notification = NotificationMessage(
            title="Test Notification",
            message="This is a test notification",
            notification_type=NotificationType.INFO,
            duration=10,
            client_id="test-client",
            icon="info-icon",
            actions=[{"id": "action1", "text": "Click Me"}]
        )
        
        self.assertEqual(notification.msg_type, MessageType.NOTIFICATION)
        self.assertEqual(notification.data["title"], "Test Notification")
        self.assertEqual(notification.data["message"], "This is a test notification")
        self.assertEqual(notification.data["notification_type"], "info")
        self.assertEqual(notification.data["duration"], 10)
        self.assertEqual(notification.data["client_id"], "test-client")
        self.assertEqual(notification.data["icon"], "info-icon")
        self.assertEqual(len(notification.data["actions"]), 1)
        self.assertEqual(notification.data["actions"][0]["id"], "action1")
    
    def test_notification_message_serialization(self):
        """Test serializing a notification message to JSON."""
        notification = NotificationMessage(
            title="Test Notification",
            message="This is a test notification"
        )
        
        json_str = notification.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["type"], "notification")
        self.assertEqual(data["data"]["title"], "Test Notification")
        self.assertEqual(data["data"]["message"], "This is a test notification")
        self.assertEqual(data["data"]["notification_type"], "info")  # Default type
    
    def test_notification_message_deserialization(self):
        """Test deserializing a notification message from JSON."""
        json_str = json.dumps({
            "type": "notification",
            "data": {
                "title": "Test Notification",
                "message": "This is a test notification",
                "notification_type": "warning",
                "duration": 15
            }
        })
        
        message = MCPMessage.from_json(json_str)
        
        self.assertIsInstance(message, NotificationMessage)
        self.assertEqual(message.data["title"], "Test Notification")
        self.assertEqual(message.data["message"], "This is a test notification")
        self.assertEqual(message.data["notification_type"], "warning")
        self.assertEqual(message.data["duration"], 15)
    
    def test_response_message(self):
        """Test creating and serializing a response message."""
        response = ResponseMessage(
            success=True,
            message="Operation completed successfully",
            data={"id": 123}
        )
        
        self.assertEqual(response.msg_type, MessageType.RESPONSE)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Operation completed successfully")
        self.assertEqual(response.data["data"]["id"], 123)
        
        json_str = response.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["type"], "response")
        self.assertTrue(data["data"]["success"])
    
    def test_error_message(self):
        """Test creating and serializing an error message."""
        error = ErrorMessage(
            error_code=404,
            error_message="Resource not found",
            details={"resource_id": "abc123"}
        )
        
        self.assertEqual(error.msg_type, MessageType.ERROR)
        self.assertEqual(error.data["code"], 404)
        self.assertEqual(error.data["message"], "Resource not found")
        self.assertEqual(error.data["details"]["resource_id"], "abc123")
        
        json_str = error.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["type"], "error")
        self.assertEqual(data["data"]["code"], 404)
    
    def test_ping_pong_messages(self):
        """Test creating ping and pong messages."""
        ping = PingMessage()
        pong = PongMessage()
        
        self.assertEqual(ping.msg_type, MessageType.PING)
        self.assertEqual(pong.msg_type, MessageType.PONG)
        
        ping_json = ping.to_json()
        pong_json = pong.to_json()
        
        ping_data = json.loads(ping_json)
        pong_data = json.loads(pong_json)
        
        self.assertEqual(ping_data["type"], "ping")
        self.assertEqual(pong_data["type"], "pong")
    
    def test_parse_message(self):
        """Test parsing messages from different formats."""
        json_str = json.dumps({
            "type": "notification",
            "data": {
                "title": "Test",
                "message": "Test message"
            }
        })
        
        message1 = parse_message(json_str)
        self.assertIsInstance(message1, NotificationMessage)
        
        dict_data = {
            "type": "response",
            "data": {
                "success": True
            }
        }
        
        message2 = parse_message(dict_data)
        self.assertIsInstance(message2, ResponseMessage)
    
    def test_validation(self):
        """Test message validation."""
        valid_notification = {
            "type": "notification",
            "data": {
                "title": "Valid Title",
                "message": "Valid message content",
                "notification_type": "info",
                "duration": 5
            }
        }
        
        is_valid, error, msg_type = validate_message_format(valid_notification)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(msg_type, MessageType.NOTIFICATION)
        
        invalid_notification = {
            "type": "notification",
            "data": {
                "message": "Message without title"
            }
        }
        
        is_valid, error, msg_type = validate_message_format(invalid_notification)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field: title", error)
        
        valid_data = {
            "title": "Test",
            "message": "Test message",
            "duration": 10
        }
        
        is_valid, error = validate_notification(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        invalid_data = {
            "title": "Test",
            "message": "Test message",
            "duration": 100  # Too long
        }
        
        is_valid, error = validate_notification(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("Duration must be between 1 and 60 seconds", error)


if __name__ == "__main__":
    unittest.main()
