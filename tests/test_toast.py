"""
Tests for the Windows 10 Toast Notification implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.notification.toast import (
    ToastNotificationManager, NotificationFactory, 
    show_notification, NotificationType
)


class TestToastNotification(unittest.TestCase):
    """Test cases for the Windows 10 Toast Notification implementation."""
    
    @patch('src.notification.toast.ToastNotifier')
    def test_toast_notification_manager_init(self, mock_toaster):
        """Test initializing the toast notification manager."""
        manager = ToastNotificationManager()
        self.assertIsNotNone(manager.toaster)
    
    @patch('src.notification.toast.ToastNotifier')
    def test_show_notification(self, mock_toaster):
        """Test showing a notification."""
        mock_instance = MagicMock()
        mock_toaster.return_value = mock_instance
        
        manager = ToastNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message",
            notification_type=NotificationType.INFO,
            duration=5
        )
        
        mock_instance.show_toast.assert_called_once()
        self.assertTrue(result)
        
        args, kwargs = mock_instance.show_toast.call_args
        self.assertEqual(kwargs["title"], "Test Title")
        self.assertEqual(kwargs["msg"], "Test Message")
        self.assertEqual(kwargs["duration"], 5)
        self.assertTrue(kwargs["threaded"])
    
    @patch('src.notification.toast.ToastNotifier')
    def test_show_notification_with_exception(self, mock_toaster):
        """Test showing a notification with an exception."""
        mock_instance = MagicMock()
        mock_instance.show_toast.side_effect = Exception("Test exception")
        mock_toaster.return_value = mock_instance
        
        manager = ToastNotificationManager()
        result = manager.show_notification(
            title="Test Title",
            message="Test Message"
        )
        
        self.assertFalse(result)
    
    @patch('src.notification.toast.ToastNotificationManager')
    def test_notification_factory(self, mock_manager_class):
        """Test the notification factory."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.show_notification.return_value = True
        
        factory = NotificationFactory()
        
        result = factory.create_info_notification("Info Title", "Info Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Info Title",
            message="Info Message",
            notification_type=NotificationType.INFO,
            duration=5
        )
        
        result = factory.create_warning_notification("Warning Title", "Warning Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Warning Title",
            message="Warning Message",
            notification_type=NotificationType.WARNING,
            duration=7
        )
        
        result = factory.create_error_notification("Error Title", "Error Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Error Title",
            message="Error Message",
            notification_type=NotificationType.ERROR,
            duration=10
        )
        
        result = factory.create_success_notification("Success Title", "Success Message")
        self.assertTrue(result)
        mock_manager.show_notification.assert_called_with(
            title="Success Title",
            message="Success Message",
            notification_type=NotificationType.SUCCESS,
            duration=5
        )
    
    @patch('src.notification.toast.notification_factory')
    def test_show_notification_helper(self, mock_factory):
        """Test the show_notification helper function."""
        mock_factory.create_info_notification.return_value = True
        mock_factory.create_warning_notification.return_value = True
        mock_factory.create_error_notification.return_value = True
        mock_factory.create_success_notification.return_value = True
        
        result = show_notification("Info Title", "Info Message", "info")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Info Title", "Info Message", 5)
        
        result = show_notification("Warning Title", "Warning Message", "warning")
        self.assertTrue(result)
        mock_factory.create_warning_notification.assert_called_with("Warning Title", "Warning Message", 5)
        
        result = show_notification("Error Title", "Error Message", "error")
        self.assertTrue(result)
        mock_factory.create_error_notification.assert_called_with("Error Title", "Error Message", 5)
        
        result = show_notification("Success Title", "Success Message", "success")
        self.assertTrue(result)
        mock_factory.create_success_notification.assert_called_with("Success Title", "Success Message", 5)
        
        result = show_notification("Invalid Title", "Invalid Message", "invalid")
        self.assertTrue(result)
        mock_factory.create_info_notification.assert_called_with("Invalid Title", "Invalid Message", 5)


if __name__ == "__main__":
    unittest.main()
