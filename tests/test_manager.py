"""
Tests for the unified notification manager.
"""

import unittest
from unittest.mock import patch, MagicMock
import platform
from src.notification.manager import (
    NotificationManager, NotificationFactory, 
    show_notification, NotificationType
)
from src.notification.platform import is_windows, is_macos


class TestNotificationManager(unittest.TestCase):
    """Test cases for the NotificationManager class."""
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_init_windows(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test initializing the notification manager on Windows."""
        mock_get_platform.return_value = "windows"
        mock_is_windows.return_value = True
        mock_is_macos.return_value = False
        
        with patch('src.notification.manager.ToastNotificationManager') as mock_toast:
            manager = NotificationManager()
            
            mock_toast.assert_called_once()
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_init_macos(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test initializing the notification manager on macOS."""
        mock_get_platform.return_value = "macos"
        mock_is_windows.return_value = False
        mock_is_macos.return_value = True
        
        with patch('src.notification.manager.MacOSNotificationManager') as mock_macos:
            manager = NotificationManager()
            
            mock_macos.assert_called_once()
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_init_unsupported(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test initializing the notification manager on an unsupported platform."""
        mock_get_platform.return_value = "linux"
        mock_is_windows.return_value = False
        mock_is_macos.return_value = False
        
        manager = NotificationManager()
        
        self.assertIsNone(manager._notification_system)
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_show_notification_windows(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test showing a notification on Windows."""
        mock_get_platform.return_value = "windows"
        mock_is_windows.return_value = True
        mock_is_macos.return_value = False
        
        mock_system = MagicMock()
        mock_system.show_notification.return_value = True
        
        with patch('src.notification.manager.ToastNotificationManager', return_value=mock_system):
            manager = NotificationManager()
            
            result = manager.show_notification(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.INFO,
                duration=5,
                icon_path="test.ico"
            )
            
            self.assertTrue(result)
            mock_system.show_notification.assert_called_once_with(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.INFO,
                duration=5,
                icon_path="test.ico"
            )
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_show_notification_macos(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test showing a notification on macOS."""
        mock_get_platform.return_value = "macos"
        mock_is_windows.return_value = False
        mock_is_macos.return_value = True
        
        mock_system = MagicMock()
        mock_system.show_notification.return_value = True
        
        with patch('src.notification.manager.MacOSNotificationManager', return_value=mock_system):
            manager = NotificationManager()
            
            result = manager.show_notification(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.INFO,
                duration=5,
                subtitle="Test Subtitle",
                sound=True
            )
            
            self.assertTrue(result)
            mock_system.show_notification.assert_called_once_with(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.INFO,
                duration=5,
                subtitle="Test Subtitle",
                sound=True
            )
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_show_notification_unsupported(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test showing a notification on an unsupported platform."""
        mock_get_platform.return_value = "linux"
        mock_is_windows.return_value = False
        mock_is_macos.return_value = False
        
        manager = NotificationManager()
        
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO
        )
        
        self.assertFalse(result)
    
    @patch('src.notification.manager.get_platform_name')
    @patch('src.notification.manager.is_windows')
    @patch('src.notification.manager.is_macos')
    def test_show_notification_exception(self, mock_is_macos, mock_is_windows, mock_get_platform):
        """Test showing a notification that raises an exception."""
        mock_get_platform.return_value = "windows"
        mock_is_windows.return_value = True
        mock_is_macos.return_value = False
        
        mock_system = MagicMock()
        mock_system.show_notification.side_effect = Exception("Test exception")
        
        with patch('src.notification.manager.ToastNotificationManager', return_value=mock_system):
            manager = NotificationManager()
            
            result = manager.show_notification(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.INFO
            )
            
            self.assertFalse(result)


class TestNotificationFactory(unittest.TestCase):
    """Test cases for the NotificationFactory class."""
    
    @patch('src.notification.manager.NotificationManager')
    def test_notification_factory(self, mock_manager_class):
        """Test the notification factory."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.show_notification.return_value = True
        
        factory = NotificationFactory()
        
        result = factory.create_info_notification("Info Title", "Info Message", param="value")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Info Title",
            message="Info Message",
            notification_type=NotificationType.INFO,
            param="value"
        )
        
        result = factory.create_warning_notification("Warning Title", "Warning Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Warning Title",
            message="Warning Message",
            notification_type=NotificationType.WARNING
        )
        
        result = factory.create_error_notification("Error Title", "Error Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Error Title",
            message="Error Message",
            notification_type=NotificationType.ERROR
        )
        
        result = factory.create_success_notification("Success Title", "Success Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Success Title",
            message="Success Message",
            notification_type=NotificationType.SUCCESS
        )


@patch('src.notification.manager.notification_factory')
class TestShowNotification(unittest.TestCase):
    """Test cases for the show_notification helper function."""
    
    def test_show_notification(self, mock_factory):
        """Test the show_notification helper function."""
        mock_factory.create_info_notification.return_value = True
        mock_factory.create_warning_notification.return_value = True
        mock_factory.create_error_notification.return_value = True
        mock_factory.create_success_notification.return_value = True
        
        result = show_notification("Info Title", "Info Message", "info", param="value")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Info Title", "Info Message", param="value")
        
        result = show_notification("Warning Title", "Warning Message", "warning")
        self.assertTrue(result)
        mock_factory.create_warning_notification.assert_called_with("Warning Title", "Warning Message")
        
        result = show_notification("Error Title", "Error Message", "error")
        self.assertTrue(result)
        mock_factory.create_error_notification.assert_called_with("Error Title", "Error Message")
        
        result = show_notification("Success Title", "Success Message", "success")
        self.assertTrue(result)
        mock_factory.create_success_notification.assert_called_with("Success Title", "Success Message")
        
        result = show_notification("Invalid Title", "Invalid Message", "invalid")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Invalid Title", "Invalid Message")


if __name__ == "__main__":
    unittest.main()
