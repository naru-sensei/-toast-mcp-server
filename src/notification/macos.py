"""
macOS Notification implementation for toast-mcp-server.

This module provides functionality to display macOS notifications
using the osascript command to interact with the macOS Notification Center.
"""

import logging
import subprocess
import platform
from typing import Dict, Any, Optional, List, Union

from src.mcp.protocol import NotificationType

logger = logging.getLogger(__name__)


class MacOSNotificationManager:
    """
    Manager for macOS Notifications.
    
    This class handles the creation and display of macOS notifications
    using the osascript command to interact with the Notification Center.
    """
    
    def __init__(self):
        """Initialize the macOS notification manager."""
        if not self._is_macos():
            logger.warning("MacOSNotificationManager initialized on non-macOS platform")
        logger.info("macOS notification manager initialized")
    
    def _is_macos(self) -> bool:
        """
        Check if the current platform is macOS.
        
        Returns:
            True if the current platform is macOS, False otherwise
        """
        return platform.system() == "Darwin"
    
    def show_notification(self,
                         title: str,
                         message: str,
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5,
                         sound: bool = True,
                         subtitle: Optional[str] = None) -> bool:
        """
        Show a macOS notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            notification_type: Type of notification (info, warning, error, success)
            duration: Duration parameter is ignored on macOS (included for API compatibility)
            sound: Whether to play a sound with the notification
            subtitle: Optional subtitle for the notification
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        if not self._is_macos():
            logger.error("Cannot show macOS notification on non-macOS platform")
            return False
        
        logger.debug(f"Showing notification: {title} ({notification_type.value})")
        
        try:
            script = self._build_notification_script(title, message, subtitle, sound)
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                return True
            else:
                logger.error(f"Failed to show notification: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to show notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error showing notification: {str(e)}")
            return False
    
    def _build_notification_script(self, 
                                  title: str, 
                                  message: str, 
                                  subtitle: Optional[str] = None,
                                  sound: bool = True) -> str:
        """
        Build the AppleScript command for displaying a notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            subtitle: Optional subtitle for the notification
            sound: Whether to play a sound with the notification
            
        Returns:
            AppleScript command string
        """
        title_escaped = title.replace('"', '\\"')
        message_escaped = message.replace('"', '\\"')
        
        script = f'display notification "{message_escaped}" with title "{title_escaped}"'
        
        if subtitle:
            subtitle_escaped = subtitle.replace('"', '\\"')
            script += f' subtitle "{subtitle_escaped}"'
        
        if sound:
            script += " sound name \"Ping\""
        
        return script


class MacOSNotificationFactory:
    """
    Factory for creating macOS notifications based on notification type.
    
    This class provides methods for creating and displaying different types
    of notifications with appropriate default settings.
    """
    
    def __init__(self):
        """Initialize the notification factory."""
        self.notification_manager = MacOSNotificationManager()
    
    def create_info_notification(self, title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """
        Create and show an information notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            subtitle: Optional subtitle for the notification
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            subtitle=subtitle
        )
    
    def create_warning_notification(self, title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """
        Create and show a warning notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            subtitle: Optional subtitle for the notification
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            subtitle=subtitle
        )
    
    def create_error_notification(self, title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """
        Create and show an error notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            subtitle: Optional subtitle for the notification
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ERROR,
            subtitle=subtitle
        )
    
    def create_success_notification(self, title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """
        Create and show a success notification.
        
        Args:
            title: Title of the notification
            message: Content of the notification
            subtitle: Optional subtitle for the notification
            
        Returns:
            True if the notification was successfully displayed, False otherwise
        """
        return self.notification_manager.show_notification(
            title=title,
            message=message,
            notification_type=NotificationType.SUCCESS,
            subtitle=subtitle
        )


macos_notification_factory = MacOSNotificationFactory()


def show_macos_notification(title: str, message: str, notification_type: str = "info", subtitle: Optional[str] = None) -> bool:
    """
    Show a macOS notification with the specified parameters.
    
    This is a convenience function for showing notifications without directly
    interacting with the MacOSNotificationFactory or MacOSNotificationManager classes.
    
    Args:
        title: Title of the notification
        message: Content of the notification
        notification_type: Type of notification ("info", "warning", "error", "success")
        subtitle: Optional subtitle for the notification
        
    Returns:
        True if the notification was successfully displayed, False otherwise
    """
    try:
        notification_type_enum = NotificationType(notification_type)
    except ValueError:
        logger.warning(f"Invalid notification type: {notification_type}, using INFO")
        notification_type_enum = NotificationType.INFO
    
    if notification_type_enum == NotificationType.INFO:
        return macos_notification_factory.create_info_notification(title, message, subtitle)
    elif notification_type_enum == NotificationType.WARNING:
        return macos_notification_factory.create_warning_notification(title, message, subtitle)
    elif notification_type_enum == NotificationType.ERROR:
        return macos_notification_factory.create_error_notification(title, message, subtitle)
    elif notification_type_enum == NotificationType.SUCCESS:
        return macos_notification_factory.create_success_notification(title, message, subtitle)
    
    return macos_notification_factory.create_info_notification(title, message, subtitle)
