"""
Avatar Management Interface

Management components for avatar configuration, monitoring, and administration.
"""

from .avatar_config_manager import AvatarConfigManager
from .knowledge_injector import KnowledgeInjector
from .avatar_monitor import AvatarMonitor

__all__ = [
    'AvatarConfigManager',
    'KnowledgeInjector',
    'AvatarMonitor'
]