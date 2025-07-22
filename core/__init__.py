"""
Core package for AI Avatar Platform infrastructure
"""
from .platform_manager import PlatformManager
from .config_manager import ConfigManager
from .base_agent import BaseAgent, BaseAction

__all__ = [
    "PlatformManager",
    "ConfigManager", 
    "BaseAgent",
    "BaseAction"
]