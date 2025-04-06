"""
Tests for the command processing system.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.server.commands import (
    Command, CommandProcessor, process_command_message,
    handle_show_notification, handle_list_commands,
    validate_show_notification, DEFAULT_COMMANDS
)
from src.mcp.protocol import (
    ResponseMessage, ErrorMessage
)


class TestCommand(unittest.TestCase):
    """Test cases for the Command class."""
    
    async def test_execute_command(self):
        """Test executing a command."""
        mock_handler = AsyncMock()
        mock_handler.return_value = (True, "Success", {"data": "value"})
        
        command = Command(
            name="test_command",
            handler=mock_handler,
            description="Test command"
        )
        
        success, message, data = await command.execute({}, "test_client")
        
        mock_handler.assert_called_once_with({}, "test_client")
        
        self.assertTrue(success)
        self.assertEqual(message, "Success")
        self.assertEqual(data, {"data": "value"})
    
    async def test_execute_command_with_validator(self):
        """Test executing a command with a validator."""
        mock_handler = AsyncMock()
        mock_handler.return_value = (True, "Success", {"data": "value"})
        
        mock_validator = MagicMock()
        mock_validator.return_value = (True, None)
        
        command = Command(
            name="test_command",
            handler=mock_handler,
            validator=mock_validator,
            description="Test command"
        )
        
        success, message, data = await command.execute({"param": "value"}, "test_client")
        
        mock_validator.assert_called_once_with({"param": "value"})
        
        mock_handler.assert_called_once_with({"param": "value"}, "test_client")
        
        self.assertTrue(success)
        self.assertEqual(message, "Success")
        self.assertEqual(data, {"data": "value"})
    
    async def test_execute_command_with_invalid_params(self):
        """Test executing a command with invalid parameters."""
        mock_handler = AsyncMock()
        
        mock_validator = MagicMock()
        mock_validator.return_value = (False, "Invalid parameter")
        
        command = Command(
            name="test_command",
            handler=mock_handler,
            validator=mock_validator,
            description="Test command"
        )
        
        success, message, data = await command.execute({}, "test_client")
        
        mock_validator.assert_called_once_with({})
        
        mock_handler.assert_not_called()
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid parameters: Invalid parameter")
        self.assertIsNone(data)
    
    async def test_execute_command_with_exception(self):
        """Test executing a command that raises an exception."""
        mock_handler = AsyncMock()
        mock_handler.side_effect = Exception("Test exception")
        
        command = Command(
            name="test_command",
            handler=mock_handler,
            description="Test command"
        )
        
        success, message, data = await command.execute({}, "test_client")
        
        mock_handler.assert_called_once_with({}, "test_client")
        
        self.assertFalse(success)
        self.assertEqual(message, "Error executing command: Test exception")
        self.assertIsNone(data)


class TestCommandProcessor(unittest.TestCase):
    """Test cases for the CommandProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = CommandProcessor()
    
    def test_register_command(self):
        """Test registering a command."""
        command = Command(
            name="test_command",
            handler=AsyncMock(),
            description="Test command"
        )
        
        self.processor.register_command(command)
        
        self.assertIn("test_command", self.processor.commands)
        self.assertEqual(self.processor.commands["test_command"], command)
    
    def test_register_commands(self):
        """Test registering multiple commands."""
        command1 = Command(
            name="command1",
            handler=AsyncMock(),
            description="Command 1"
        )
        
        command2 = Command(
            name="command2",
            handler=AsyncMock(),
            description="Command 2"
        )
        
        self.processor.register_commands([command1, command2])
        
        self.assertIn("command1", self.processor.commands)
        self.assertIn("command2", self.processor.commands)
        self.assertEqual(self.processor.commands["command1"], command1)
        self.assertEqual(self.processor.commands["command2"], command2)
    
    async def test_process_command(self):
        """Test processing a command."""
        mock_handler = AsyncMock()
        mock_handler.return_value = (True, "Success", {"data": "value"})
        
        command = Command(
            name="test_command",
            handler=mock_handler,
            description="Test command"
        )
        
        self.processor.register_command(command)
        
        success, message, data = await self.processor.process_command(
            "test_command", {"param": "value"}, "test_client"
        )
        
        mock_handler.assert_called_once_with({"param": "value"}, "test_client")
        
        self.assertTrue(success)
        self.assertEqual(message, "Success")
        self.assertEqual(data, {"data": "value"})
    
    async def test_process_unknown_command(self):
        """Test processing an unknown command."""
        success, message, data = await self.processor.process_command(
            "unknown_command", {}, "test_client"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Unknown command: unknown_command")
        self.assertIsNone(data)
    
    async def test_process_command_requiring_auth(self):
        """Test processing a command that requires authentication."""
        mock_handler = AsyncMock()
        
        command = Command(
            name="auth_command",
            handler=mock_handler,
            description="Auth command",
            requires_auth=True
        )
        
        self.processor.register_command(command)
        
        success, message, data = await self.processor.process_command(
            "auth_command", {}, "test_client"
        )
        
        mock_handler.assert_not_called()
        
        self.assertFalse(success)
        self.assertEqual(message, "Authentication required")
        self.assertIsNone(data)
        
        self.processor.authenticate_client("test_client")
        
        success, message, data = await self.processor.process_command(
            "auth_command", {}, "test_client"
        )
        
        mock_handler.assert_called_once_with({}, "test_client")
    
    def test_authenticate_deauthenticate_client(self):
        """Test authenticating and deauthenticating a client."""
        self.processor.authenticate_client("test_client")
        
        self.assertIn("test_client", self.processor.authenticated_clients)
        
        self.processor.authenticate_client("test_client")
        
        self.assertEqual(self.processor.authenticated_clients.count("test_client"), 1)
        
        self.processor.deauthenticate_client("test_client")
        
        self.assertNotIn("test_client", self.processor.authenticated_clients)
        
        self.processor.deauthenticate_client("non_existent_client")


class TestCommandHandlers(unittest.TestCase):
    """Test cases for the command handlers."""
    
    @patch('src.server.commands.show_notification')
    async def test_handle_show_notification(self, mock_show_notification):
        """Test the show_notification command handler."""
        mock_show_notification.return_value = True
        
        success, message, data = await handle_show_notification(
            {
                "title": "Test Title",
                "message": "Test Message",
                "type": "info",
                "duration": 5
            },
            "test_client"
        )
        
        mock_show_notification.assert_called_once_with(
            "Test Title", "Test Message", "info", 5
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Notification displayed successfully")
        self.assertIsNone(data)
        
        mock_show_notification.reset_mock()
        mock_show_notification.return_value = False
        
        success, message, data = await handle_show_notification(
            {
                "title": "Test Title",
                "message": "Test Message"
            },
            "test_client"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Failed to display notification")
        self.assertIsNone(data)
    
    async def test_handle_list_commands(self):
        """Test the list_commands command handler."""
        success, message, data = await handle_list_commands({}, "test_client")
        
        self.assertTrue(success)
        self.assertEqual(message, "Commands retrieved successfully")
        self.assertIsInstance(data, dict)
        self.assertIn("commands", data)
        self.assertIsInstance(data["commands"], list)
        self.assertTrue(len(data["commands"]) > 0)
    
    def test_validate_show_notification(self):
        """Test the show_notification validator."""
        is_valid, error = validate_show_notification({
            "title": "Test Title",
            "message": "Test Message",
            "type": "info",
            "duration": 5
        })
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        is_valid, error = validate_show_notification({
            "message": "Test Message"
        })
        
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required parameter: title")
        
        is_valid, error = validate_show_notification({
            "title": "Test Title"
        })
        
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required parameter: message")
        
        is_valid, error = validate_show_notification({
            "title": "Test Title",
            "message": "Test Message",
            "type": "invalid"
        })
        
        self.assertFalse(is_valid)
        self.assertEqual(error, "Invalid notification type")
        
        is_valid, error = validate_show_notification({
            "title": "Test Title",
            "message": "Test Message",
            "duration": "5"  # Should be an integer
        })
        
        self.assertFalse(is_valid)
        self.assertEqual(error, "Duration must be an integer")


@patch('src.server.commands.command_processor')
class TestProcessCommandMessage(unittest.TestCase):
    """Test cases for the process_command_message function."""
    
    async def test_process_command_message(self, mock_processor):
        """Test processing a command message."""
        mock_processor.process_command = AsyncMock()
        mock_processor.process_command.return_value = (True, "Success", {"data": "value"})
        
        message = await process_command_message(
            {
                "command": "test_command",
                "params": {"param": "value"}
            },
            "test_client"
        )
        
        mock_processor.process_command.assert_called_once_with(
            "test_command", {"param": "value"}, "test_client"
        )
        
        self.assertIsInstance(message, ResponseMessage)
        self.assertTrue(message.data["success"])
        self.assertEqual(message.data["message"], "Success")
        self.assertEqual(message.data["data"], {"data": "value"})
    
    async def test_process_command_message_failure(self, mock_processor):
        """Test processing a command message that fails."""
        mock_processor.process_command = AsyncMock()
        mock_processor.process_command.return_value = (False, "Failure", None)
        
        message = await process_command_message(
            {
                "command": "test_command",
                "params": {"param": "value"}
            },
            "test_client"
        )
        
        self.assertIsInstance(message, ErrorMessage)
        self.assertEqual(message.data["code"], 400)
        self.assertEqual(message.data["message"], "Failure")
    
    async def test_process_command_message_missing_command(self, mock_processor):
        """Test processing a command message with a missing command name."""
        message = await process_command_message(
            {
                "params": {"param": "value"}
            },
            "test_client"
        )
        
        mock_processor.process_command.assert_not_called()
        
        self.assertIsInstance(message, ErrorMessage)
        self.assertEqual(message.data["code"], 400)
        self.assertEqual(message.data["message"], "Missing command name")


class TestDefaultCommands(unittest.TestCase):
    """Test cases for the default commands."""
    
    def test_default_commands(self):
        """Test that default commands are defined."""
        self.assertIsInstance(DEFAULT_COMMANDS, list)
        
        self.assertTrue(len(DEFAULT_COMMANDS) > 0)
        
        for command in DEFAULT_COMMANDS:
            self.assertIsInstance(command, Command)


if __name__ == "__main__":
    unittest.main()
