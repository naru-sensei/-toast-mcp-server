"""
Platform detection utilities for toast-mcp-server.

This module provides utilities for detecting the current platform
and selecting the appropriate notification system.
"""

import logging
import platform
from typing import Dict, Any, Optional, List, Union, Callable

from src.mcp.protocol import NotificationType

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    """
    Check if the current platform is Windows.
    
    Returns:
        True if the current platform is Windows, False otherwise
    """
    return platform.system() == "Windows"


def is_macos() -> bool:
    """
    Check if the current platform is macOS.
    
    Returns:
        True if the current platform is macOS, False otherwise
    """
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """
    Check if the current platform is Linux.
    
    Returns:
        True if the current platform is Linux, False otherwise
    """
    return platform.system() == "Linux"


def get_platform_name() -> str:
    """
    Get the name of the current platform.
    
    Returns:
        Name of the current platform ("windows", "macos", "linux", or "unknown")
    """
    if is_windows():
        return "windows"
    elif is_macos():
        return "macos"
    elif is_linux():
        return "linux"
    else:
        return "unknown"
