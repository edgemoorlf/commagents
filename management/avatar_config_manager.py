"""
Avatar Configuration Manager

Manages avatar configurations, creation, and lifecycle operations.
Provides administrative interface for avatar management.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from pathlib import Path

from agents.avatar.base_avatar_agent import BaseAvatarAgent
from agents.avatar.avatar_knowledge_base import AvatarKnowledgeBase
from agents.avatar.avatar_personality import AvatarPersonality
from agents.avatar.avatar_api_client import AvatarProvider


@dataclass
class AvatarConfiguration:
    """Avatar configuration definition"""
    avatar_id: str
    name: str
    profile: str
    provider: str
    personality_config: Dict[str, Any]
    knowledge_config: Dict[str, Any]
    content_config: Dict[str, Any]
    api_config: Dict[str, Any]
    initial_knowledge: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    status: str = "inactive"  # inactive, active, error
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AvatarConfiguration':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class AvatarConfigManager:
    """
    Avatar Configuration Management System
    
    Features:
    - Avatar creation and configuration
    - Template management
    - Configuration validation
    - Avatar lifecycle management
    - Batch operations
    - Configuration persistence
    """
    
    def __init__(self, config_dir: Optional[str] = None, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration storage
        self.config_dir = Path(config_dir or "configs/avatars")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Avatar registry
        self.avatar_configs: Dict[str, AvatarConfiguration] = {}
        self.active_avatars: Dict[str, BaseAvatarAgent] = {}
        
        # Templates
        self.avatar_templates: Dict[str, Dict[str, Any]] = {}
        
        # Validation rules
        self.validation_rules: List[Callable[[Dict[str, Any]], bool]] = []
        
        # Load existing configurations
        self._load_configurations_task = None
        self._load_templates()
        self._setup_validation_rules()
    
    async def initialize(self):
        """Initialize the config manager (call this after creating the instance)"""
        if self._load_configurations_task is None:
            self._load_configurations_task = asyncio.create_task(self._load_configurations())
        await self._load_configurations_task
    
    async def _load_configurations(self):
        """Load existing avatar configurations"""
        try:
            for config_file in self.config_dir.glob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    avatar_config = AvatarConfiguration.from_dict(config_data)
                    self.avatar_configs[avatar_config.avatar_id] = avatar_config
                    self.logger.info(f"Loaded configuration for avatar {avatar_config.avatar_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load config {config_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.avatar_configs)} avatar configurations")
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
    
    def _load_templates(self):
        """Load avatar templates"""
        self.avatar_templates = {
            'conversational': {
                'name': 'Conversational Avatar',
                'profile': 'Friendly conversational assistant',
                'provider': 'local',
                'personality_config': {
                    'default_personality': {
                        'extraversion': 0.6,
                        'agreeableness': 0.7,
                        'conscientiousness': 0.5,
                        'neuroticism': -0.3,
                        'openness': 0.4
                    }
                },
                'content_config': {
                    'default_generation_mode': 'conversational',
                    'max_response_length': 300
                },
                'api_config': {
                    'primary_provider': 'local',
                    'endpoints': {'local': 'http://localhost:8000/speak'},
                    'default_timeout': 10
                }
            },
            'analytical': {
                'name': 'Analytical Avatar',
                'profile': 'Expert analytical assistant',
                'provider': 'local',
                'personality_config': {
                    'default_personality': {
                        'extraversion': 0.2,
                        'agreeableness': 0.4,
                        'conscientiousness': 0.8,
                        'neuroticism': -0.5,
                        'openness': 0.9
                    }
                },
                'content_config': {
                    'default_generation_mode': 'analytical',
                    'max_response_length': 500
                },
                'api_config': {
                    'primary_provider': 'local'
                }
            },
            'creative': {
                'name': 'Creative Avatar',
                'profile': 'Creative and imaginative assistant',
                'provider': 'local',
                'personality_config': {
                    'default_personality': {
                        'extraversion': 0.7,
                        'agreeableness': 0.6,
                        'conscientiousness': 0.3,
                        'neuroticism': 0.1,
                        'openness': 1.0
                    }
                },
                'content_config': {
                    'default_generation_mode': 'creative',
                    'max_response_length': 400
                },
                'api_config': {
                    'primary_provider': 'local'
                }
            }
        }
    
    def _setup_validation_rules(self):
        """Setup configuration validation rules"""
        def validate_required_fields(config: Dict[str, Any]) -> bool:
            required_fields = ['avatar_id', 'name', 'profile']
            return all(field in config for field in required_fields)
        
        def validate_avatar_id_format(config: Dict[str, Any]) -> bool:
            avatar_id = config.get('avatar_id', '')
            return (isinstance(avatar_id, str) and 
                   len(avatar_id) >= 3 and 
                   avatar_id.replace('_', '').replace('-', '').isalnum())
        
        def validate_personality_config(config: Dict[str, Any]) -> bool:
            personality_config = config.get('personality_config', {})
            if 'default_personality' in personality_config:
                traits = personality_config['default_personality']
                for trait_value in traits.values():
                    if not isinstance(trait_value, (int, float)) or not -1.0 <= trait_value <= 1.0:
                        return False
            return True
        
        self.validation_rules = [
            validate_required_fields,
            validate_avatar_id_format,
            validate_personality_config
        ]
    
    async def create_avatar(self, avatar_id: str, template: str = "conversational",
                          custom_config: Optional[Dict[str, Any]] = None,
                          initial_knowledge: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Create new avatar from template"""
        
        if avatar_id in self.avatar_configs:
            self.logger.error(f"Avatar {avatar_id} already exists")
            return False
        
        if template not in self.avatar_templates:
            self.logger.error(f"Template {template} not found")
            return False
        
        try:
            # Start with template
            template_config = self.avatar_templates[template].copy()
            
            # Apply custom configuration
            if custom_config:
                template_config.update(custom_config)
            
            # Create configuration
            avatar_config = AvatarConfiguration(
                avatar_id=avatar_id,
                name=template_config.get('name', f'Avatar {avatar_id}'),
                profile=template_config.get('profile', 'Avatar Agent'),
                provider=template_config.get('provider', 'local'),
                personality_config=template_config.get('personality_config', {}),
                knowledge_config=template_config.get('knowledge_config', {}),
                content_config=template_config.get('content_config', {}),
                api_config=template_config.get('api_config', {}),
                initial_knowledge=initial_knowledge or [],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status='inactive',
                metadata=template_config.get('metadata')
            )
            
            # Validate configuration
            if not await self.validate_configuration(avatar_config.to_dict()):
                return False
            
            # Save configuration
            self.avatar_configs[avatar_id] = avatar_config
            await self._save_configuration(avatar_config)
            
            self.logger.info(f"Created avatar {avatar_id} from template {template}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create avatar {avatar_id}: {e}")
            return False
    
    async def update_avatar_config(self, avatar_id: str, 
                                 updates: Dict[str, Any]) -> bool:
        """Update avatar configuration"""
        
        if avatar_id not in self.avatar_configs:
            self.logger.error(f"Avatar {avatar_id} not found")
            return False
        
        try:
            config = self.avatar_configs[avatar_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.now()
            
            # Validate updated configuration
            if not await self.validate_configuration(config.to_dict()):
                return False
            
            # Save configuration
            await self._save_configuration(config)
            
            # Update active avatar if running
            if avatar_id in self.active_avatars:
                await self._update_active_avatar(avatar_id, updates)
            
            self.logger.info(f"Updated configuration for avatar {avatar_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update avatar {avatar_id}: {e}")
            return False
    
    async def start_avatar(self, avatar_id: str) -> bool:
        """Start/activate an avatar"""
        
        if avatar_id not in self.avatar_configs:
            self.logger.error(f"Avatar {avatar_id} configuration not found")
            return False
        
        if avatar_id in self.active_avatars:
            self.logger.warning(f"Avatar {avatar_id} is already active")
            return True
        
        try:
            config = self.avatar_configs[avatar_id]
            
            # Create avatar instance
            avatar_agent = BaseAvatarAgent(
                avatar_id=avatar_id,
                name=config.name,
                profile=config.profile,
                config={
                    'personality': config.personality_config,
                    'knowledge': config.knowledge_config,
                    'content_generation': config.content_config,
                    'api_client': config.api_config,
                    'initial_knowledge': config.initial_knowledge
                }
            )
            
            # Initialize avatar
            await avatar_agent.initialize()
            
            # Store active avatar
            self.active_avatars[avatar_id] = avatar_agent
            config.status = 'active'
            config.updated_at = datetime.now()
            
            await self._save_configuration(config)
            
            self.logger.info(f"Started avatar {avatar_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start avatar {avatar_id}: {e}")
            if avatar_id in self.avatar_configs:
                self.avatar_configs[avatar_id].status = 'error'
            return False
    
    async def stop_avatar(self, avatar_id: str) -> bool:
        """Stop/deactivate an avatar"""
        
        if avatar_id not in self.active_avatars:
            self.logger.warning(f"Avatar {avatar_id} is not active")
            return True
        
        try:
            avatar_agent = self.active_avatars[avatar_id]
            
            # Cleanup avatar
            await avatar_agent.cleanup()
            
            # Remove from active avatars
            del self.active_avatars[avatar_id]
            
            # Update configuration
            if avatar_id in self.avatar_configs:
                self.avatar_configs[avatar_id].status = 'inactive'
                self.avatar_configs[avatar_id].updated_at = datetime.now()
                await self._save_configuration(self.avatar_configs[avatar_id])
            
            self.logger.info(f"Stopped avatar {avatar_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop avatar {avatar_id}: {e}")
            return False
    
    async def delete_avatar(self, avatar_id: str) -> bool:
        """Delete avatar configuration and data"""
        
        # Stop avatar if active
        if avatar_id in self.active_avatars:
            await self.stop_avatar(avatar_id)
        
        if avatar_id not in self.avatar_configs:
            self.logger.warning(f"Avatar {avatar_id} configuration not found")
            return True
        
        try:
            # Remove configuration file
            config_file = self.config_dir / f"{avatar_id}.json"
            if config_file.exists():
                config_file.unlink()
            
            # Remove from memory
            del self.avatar_configs[avatar_id]
            
            self.logger.info(f"Deleted avatar {avatar_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete avatar {avatar_id}: {e}")
            return False
    
    async def get_avatar(self, avatar_id: str) -> Optional[BaseAvatarAgent]:
        """Get active avatar instance"""
        return self.active_avatars.get(avatar_id)
    
    async def list_avatars(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List avatar configurations"""
        avatars = []
        
        for avatar_config in self.avatar_configs.values():
            if status_filter and avatar_config.status != status_filter:
                continue
            
            avatar_info = avatar_config.to_dict()
            
            # Add runtime information for active avatars
            if avatar_config.avatar_id in self.active_avatars:
                active_avatar = self.active_avatars[avatar_config.avatar_id]
                avatar_info['runtime_status'] = active_avatar.get_avatar_status()
            
            avatars.append(avatar_info)
        
        return avatars
    
    async def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate avatar configuration"""
        for rule in self.validation_rules:
            if not rule(config):
                return False
        return True
    
    async def _save_configuration(self, config: AvatarConfiguration):
        """Save avatar configuration to file"""
        config_file = self.config_dir / f"{config.avatar_id}.json"
        
        with open(config_file, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
    
    async def _update_active_avatar(self, avatar_id: str, updates: Dict[str, Any]):
        """Update active avatar with configuration changes"""
        if avatar_id not in self.active_avatars:
            return
        
        avatar = self.active_avatars[avatar_id]
        
        # Update avatar configuration
        if 'personality_config' in updates:
            avatar.personality.import_personality({
                'traits': updates['personality_config'].get('default_personality', {}),
                'custom_traits': updates['personality_config'].get('custom_traits', {})
            })
        
        if 'api_config' in updates:
            avatar.api_client.config.update(updates['api_config'])
        
        # Note: Other configuration updates may require avatar restart
    
    async def batch_operation(self, operation: str, avatar_ids: List[str],
                            **kwargs) -> Dict[str, bool]:
        """Perform batch operation on multiple avatars"""
        results = {}
        
        for avatar_id in avatar_ids:
            try:
                if operation == 'start':
                    results[avatar_id] = await self.start_avatar(avatar_id)
                elif operation == 'stop':
                    results[avatar_id] = await self.stop_avatar(avatar_id)
                elif operation == 'delete':
                    results[avatar_id] = await self.delete_avatar(avatar_id)
                elif operation == 'update':
                    updates = kwargs.get('updates', {})
                    results[avatar_id] = await self.update_avatar_config(avatar_id, updates)
                else:
                    results[avatar_id] = False
                    
            except Exception as e:
                self.logger.error(f"Batch operation {operation} failed for {avatar_id}: {e}")
                results[avatar_id] = False
        
        return results
    
    def get_templates(self) -> List[str]:
        """Get available avatar templates"""
        return list(self.avatar_templates.keys())
    
    def get_template_config(self, template: str) -> Optional[Dict[str, Any]]:
        """Get template configuration"""
        return self.avatar_templates.get(template)
    
    def add_template(self, name: str, config: Dict[str, Any]) -> bool:
        """Add new avatar template"""
        try:
            # Validate template config
            if not isinstance(config, dict):
                return False
            
            self.avatar_templates[name] = config
            self.logger.info(f"Added template: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add template {name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get avatar management statistics"""
        status_counts = {}
        for config in self.avatar_configs.values():
            status_counts[config.status] = status_counts.get(config.status, 0) + 1
        
        return {
            'total_avatars': len(self.avatar_configs),
            'active_avatars': len(self.active_avatars),
            'status_distribution': status_counts,
            'available_templates': len(self.avatar_templates),
            'config_directory': str(self.config_dir)
        }