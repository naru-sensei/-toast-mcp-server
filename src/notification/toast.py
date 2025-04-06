"""
Windows 10 Toast Notification implementation for toast-mcp-server.

This module provides functionality to display Windows 10 toast notifications
using the win10toast library.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from win10toast import ToastNotifier

from src.mcp.protocol import NotificationType

logger = logging.getLogger(__name__)


class ToastNotificationManager:
    """
    Manager for Windows 10 Toast Notifications.
    
    This class handles the creation and display of Windows 10 toast notifications
    using the win10toast library.
    """
    
    def __init__(self):
        """Initialize the toast notification manager."""
        self.toaster = ToastNotifier()
        logger.info("Toast notification manager initialized")
    
    def show_notification(self,
                         title: str,
                         message: str,
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5,
                         icon_path: Optional[str] = None,
                         threaded: bool = True) -> bool:
        """
        Show a Windows 10 toast notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            notification_type: Type of notification (info, warning, error, success)
            duration: Duration to display the notification in seconds
            icon_path: Path to the icon file to display with the notification
            threaded: Whether to show the notification in a separate thread
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        if not icon_path:
            icon_path = self._get_default_icon(notification_type)
        
        logger.debug(f"Showing notification: {title} ({notification_type.value})")
        
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                icon_path=icon_path,
                duration=duration,
                threaded=threaded
            )
            return True
        except Exception as e:
            logger.error(f"Failed to show notification: {str(e)}")
            return False
    
    def _get_default_icon(self, notification_type: NotificationType) -> str:
        """
        Get the default icon path for a notification type.
        
        Args:
            notification_type: Type of notification
            
        Returns:
            Path to the default icon for the notification type
        """
        icons = {
            NotificationType.INFO: "icons/info.ico",
            NotificationType.WARNING: "icons/warning.ico",
            NotificationType.ERROR: "icons/error.ico",
            NotificationType.SUCCESS: "icons/success.ico"
        }
        
        return icons.get(notification_type, "icons/default.ico")


class NotificationFactory:
    """
    Factory for creating notifications based on notification type.
    
    This class provides methods for creating and displaying different types
    of notifications with appropriate default settings.
    """
    
    def __init__(self):
        """Initialize the notification factory."""
        self.toast_manager = ToastNotificationManager()
    
    def create_info_notification(self, title: str, message: str, duration: int = 5) -> bool:
        """
        Create and show an information notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            duration: Duration to display the notification in seconds
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.toast_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            duration=duration
        )
    
    def create_warning_notification(self, title: str, message: str, duration: int = 7) -> bool:
        """
        Create and show a warning notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            duration: Duration to display the notification in seconds
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.toast_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            duration=duration
        )
    
    def create_error_notification(self, title: str, message: str, duration: int = 10) -> bool:
        """
        Create and show an error notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            duration: Duration to display the notification in seconds
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.toast_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ERROR,
            duration=duration
        )
    
    def create_success_notification(self, title: str, message: str, duration: int = 5) -> bool:
        """
        Create and show a success notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            duration: Duration to display the notification in seconds
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.toast_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.SUCCESS,
            duration=duration
        )


notification_factory = NotificationFactory()


def show_notification(title: str, message: str, notification_type: str = "info", duration: int = 5) -> bool:
    """
    Show a notification with the specified parameters.
    
    This is a convenience function for showing notifications without directly
    interacting with the NotificationFactory or ToastNotificationManager classes.
    
    Args:
        title: Title of the notification
        message: Content of the notification
        notification_type: Type of notification ("info", "warning", "error", "success")
        duration: Duration to display the notification in seconds
        
    Returns:
        True if the notification was successfully displayed, False otherwise
    """
    try:
        notification_type_enum = NotificationType(notification_type)
    except ValueError:
        logger.warning(f"Invalid notification type: {notification_type}, using INFO")
        notification_type_enum = NotificationType.INFO
    
    if notification_type_enum == NotificationType.INFO:
        return notification_factory.create_info_notification(title, message, duration)
    elif notification_type_enum == NotificationType.WARNING:
        return notification_factory.create_warning_notification(title, message, duration)
    elif notification_type_enum == NotificationType.ERROR:
        return notification_factory.create_error_notification(title, message, duration)
    elif notification_type_enum == NotificationType.SUCCESS:
        return notification_factory.create_success_notification(title, message, duration)
    
    return notification_factory.create_info_notification(title, message, duration)
