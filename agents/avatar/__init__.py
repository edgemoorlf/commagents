"""
Avatar Manufacturing Workshop

This module contains the core components for creating, managing, and operating
AI avatars within the platform.
"""

from .base_avatar_agent import BaseAvatarAgent, AvatarAction
from .avatar_knowledge_base import AvatarKnowledgeBase
from .avatar_personality import AvatarPersonality
from .avatar_content_generator import AvatarContentGenerator
from .avatar_api_client import AvatarApiClient

__all__ = [
    'BaseAvatarAgent',
    'AvatarAction',
    'AvatarKnowledgeBase',
    'AvatarPersonality', 
    'AvatarContentGenerator',
    'AvatarApiClient'
]