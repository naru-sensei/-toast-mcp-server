"""
Unified notification manager for toast-mcp-server.

This module provides a unified interface for displaying notifications
on different platforms, automatically selecting the appropriate
notification system based on the current platform.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from src.mcp.protocol import NotificationType
from src.notification.platform import is_windows, is_macos, get_platform_name

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Unified notification manager for multiple platforms.
    
    This class provides a unified interface for displaying notifications
    on different platforms, automatically selecting the appropriate
    notification system based on the current platform.
    """
    
    def __init__(self):
        """Initialize the notification manager."""
        self._platform = get_platform_name()
        self._notification_system = self._get_notification_system()
        logger.info(f"Notification manager initialized for platform: {self._platform}")
    
    def _get_notification_system(self):
        """
        Get the appropriate notification system for the current platform.
        
        Returns:
            Notification system for the current platform
        """
        if is_windows():
            from src.notification.toast import ToastNotificationManager
            return ToastNotificationManager()
        elif is_macos():
            from src.notification.macos import MacOSNotificationManager
            return MacOSNotificationManager()
        else:
            logger.warning(f"No notification system available for platform: {self._platform}")
            return None
    
    def show_notification(self,
                         title: str,
                         message: str,
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5,
                         **kwargs) -> bool:
        """
        Show a notification on the current platform.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            notification_type: Type of notification (info, warning, error, success)
            duration: Duration to display the notification in seconds (ignored on some platforms)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        if not self._notification_system:
            logger.error(f"Cannot show notification on unsupported platform: {self._platform}")
            return False
        
        logger.debug(f"Showing notification on {self._platform}: {title} ({notification_type.value})")
        
        try:
            if is_windows():
                return self._notification_system.show_notification(
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    duration=duration,
                    **kwargs
                )
            elif is_macos():
                subtitle = kwargs.get("subtitle")
                sound = kwargs.get("sound", True)
                
                return self._notification_system.show_notification(
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    duration=duration,
                    subtitle=subtitle,
                    sound=sound
                )
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to show notification: {str(e)}")
            return False


class NotificationFactory:
    """
    Factory for creating notifications based on notification type.
    
    This class provides methods for creating and displaying different types
    of notifications with appropriate default settings.
    """
    
    def __init__(self):
        """Initialize the notification factory."""
        self.notification_manager = NotificationManager()
    
    def create_info_notification(self, title: str, message: str, **kwargs) -> bool:
        """
        Create and show an information notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            **kwargs: Additional platform-specific parameters
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            **kwargs
        )
    
    def create_warning_notification(self, title: str, message: str, **kwargs) -> bool:
        """
        Create and show a warning notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            **kwargs: Additional platform-specific parameters
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            **kwargs
        )
    
    def create_error_notification(self, title: str, message: str, **kwargs) -> bool:
        """
        Create and show an error notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            **kwargs: Additional platform-specific parameters
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ERROR,
            **kwargs
        )
    
    def create_success_notification(self, title: str, message: str, **kwargs) -> bool:
        """
        Create and show a success notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            **kwargs: Additional platform-specific parameters
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.SUCCESS,
            **kwargs
        )


notification_factory = NotificationFactory()


def show_notification(title: str, message: str, notification_type: str = "info", **kwargs) -> bool:
    """
    Show a notification with the specified parameters.
    
    This is a convenience function for showing notifications without directly
    interacting with the NotificationFactory or platform-specific notification classes.
    
    Args:
        title: Title of the notification
        message: Content of the notification
        notification_type: Type of notification ("info", "warning", "error", "success")
        **kwargs: Additional platform-specific parameters
        
    Returns:
        True if the notification was successfully displayed, False otherwise
    """
    try:
        notification_type_enum = NotificationType(notification_type)
    except ValueError:
        logger.warning(f"Invalid notification type: {notification_type}, using INFO")
        notification_type_enum = NotificationType.INFO
    
    if notification_type_enum == NotificationType.INFO:
        return notification_factory.create_info_notification(title, message, **kwargs)
    elif notification_type_enum == NotificationType.WARNING:
        return notification_factory.create_warning_notification(title, message, **kwargs)
    elif notification_type_enum == NotificationType.ERROR:
        return notification_factory.create_error_notification(title, message, **kwargs)
    elif notification_type_enum == NotificationType.SUCCESS:
        return notification_factory.create_success_notification(title, message, **kwargs)
    
    return notification_factory.create_info_notification(title, message, **kwargs)
