"""
Tests for the macOS Notification implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
import platform
import subprocess
from src.notification.macos import (
    MacOSNotificationManager, MacOSNotificationFactory, 
    show_macos_notification, NotificationType
)


class TestMacOSNotification(unittest.TestCase):
    """Test cases for the macOS Notification implementation."""
    
    @patch('src.notification.macos.platform.system')
    def test_is_macos(self, mock_system):
        """Test platform detection."""
        mock_system.return_value = "Darwin"
        manager = MacOSNotificationManager()
        self.assertTrue(manager._is_macos())
        
        mock_system.return_value = "Linux"
        manager = MacOSNotificationManager()
        self.assertFalse(manager._is_macos())
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification(self, mock_run, mock_system):
        """Test showing a notification."""
        mock_system.return_value = "Darwin"
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "osascript")
        self.assertEqual(args[0][1], "-e")
        self.assertIn("display notification", args[0][2])
        self.assertIn("Test Message", args[0][2])
        self.assertIn("Test Title", args[0][2])
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification_with_subtitle(self, mock_run, mock_system):
        """Test showing a notification with a subtitle."""
        mock_system.return_value = "Darwin"
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            subtitle="Test Subtitle",
            notification_type=NotificationType.INFO
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        args, kwargs = mock_run.call_args
        self.assertIn("subtitle", args[0][2])
        self.assertIn("Test Subtitle", args[0][2])
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification_without_sound(self, mock_run, mock_system):
        """Test showing a notification without sound."""
        mock_system.return_value = "Darwin"
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            sound=False,
            notification_type=NotificationType.INFO
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        args, kwargs = mock_run.call_args
        self.assertNotIn("sound name", args[0][2])
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification_on_non_macos(self, mock_run, mock_system):
        """Test showing a notification on a non-macOS platform."""
        mock_system.return_value = "Linux"
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO
        )
        
        self.assertFalse(result)
        mock_run.assert_not_called()
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification_with_subprocess_error(self, mock_run, mock_system):
        """Test showing a notification with a subprocess error."""
        mock_system.return_value = "Darwin"
        mock_run.side_effect = subprocess.SubprocessError("Test error")
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO
        )
        
        self.assertFalse(result)
    
    @patch('src.notification.macos.platform.system')
    @patch('src.notification.macos.subprocess.run')
    def test_show_notification_with_return_code_error(self, mock_run, mock_system):
        """Test showing a notification with a return code error."""
        mock_system.return_value = "Darwin"
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Test error"
        mock_run.return_value = mock_process
        
        manager = MacOSNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO
        )
        
        self.assertFalse(result)
    
    @patch('src.notification.macos.MacOSNotificationManager')
    def test_notification_factory(self, mock_manager_class):
        """Test the notification factory."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.show_notification.return_value = True
        
        factory = MacOSNotificationFactory()
        
        result = factory.create_info_notification("Info Title", "Info Message", "Info Subtitle")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Info Title",
            message="Info Message",
            notification_type=NotificationType.INFO,
            subtitle="Info Subtitle"
        )
        
        result = factory.create_warning_notification("Warning Title", "Warning Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Warning Title",
            message="Warning Message",
            notification_type=NotificationType.WARNING,
            subtitle=None
        )
        
        result = factory.create_error_notification("Error Title", "Error Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Error Title",
            message="Error Message",
            notification_type=NotificationType.ERROR,
            subtitle=None
        )
        
        result = factory.create_success_notification("Success Title", "Success Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Success Title",
            message="Success Message",
            notification_type=NotificationType.SUCCESS,
            subtitle=None
        )
    
    @patch('src.notification.macos.macos_notification_factory')
    def test_show_macos_notification_helper(self, mock_factory):
        """Test the show_macos_notification helper function."""
        mock_factory.create_info_notification.return_value = True
        mock_factory.create_warning_notification.return_value = True
        mock_factory.create_error_notification.return_value = True
        mock_factory.create_success_notification.return_value = True
        
        result = show_macos_notification("Info Title", "Info Message", "info", "Info Subtitle")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Info Title", "Info Message", "Info Subtitle")
        
        result = show_macos_notification("Warning Title", "Warning Message", "warning")
        self.assertTrue(result)
        mock_factory.create_warning_notification.assert_called_with("Warning Title", "Warning Message", None)
        
        result = show_macos_notification("Error Title", "Error Message", "error")
        self.assertTrue(result)
        mock_factory.create_error_notification.assert_called_with("Error Title", "Error Message", None)
        
        result = show_macos_notification("Success Title", "Success Message", "success")
        self.assertTrue(result)
        mock_factory.create_success_notification.assert_called_with("Success Title", "Success Message", None)
        
        result = show_macos_notification("Invalid Title", "Invalid Message", "invalid")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Invalid Title", "Invalid Message", None)


if __name__ == "__main__":
    unittest.main()
