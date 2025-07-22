"""
Base Avatar Agent

Core avatar agent that integrates knowledge base, personality, content generation,
and API communication to create a complete avatar system.
"""
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio

from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.logs import logger

from core.base_agent import BaseAgent, BaseAction
from .avatar_knowledge_base import AvatarKnowledgeBase
from .avatar_personality import AvatarPersonality
from .avatar_content_generator import AvatarContentGenerator
from .avatar_api_client import AvatarApiClient, AvatarProvider


class AvatarAction(BaseAction):
    """Base action class for avatar-specific actions"""
    
    def __init__(self, name: str = "", avatar_agent: Optional['BaseAvatarAgent'] = None,
                 context: Optional[Dict] = None):
        super().__init__(name=name, context=context)
        self.avatar_agent = avatar_agent
    
    async def _execute(self, *args, **kwargs) -> Any:
        """Default execution - delegates to avatar agent"""
        if self.avatar_agent:
            return await self.avatar_agent._handle_action(self, *args, **kwargs)
        else:
            raise NotImplementedError("Avatar action requires avatar_agent reference")


class GenerateAvatarResponse(AvatarAction):
    """Action for generating avatar responses"""
    
    def __init__(self, avatar_agent: Optional['BaseAvatarAgent'] = None):
        super().__init__(name="GenerateAvatarResponse", avatar_agent=avatar_agent)
    
    async def _execute(self, prompt: str, mode: str = "conversational",
                     context: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Generate avatar response"""
        return await self.avatar_agent.generate_response(prompt, mode, context)


class SpeakAction(AvatarAction):
    """Action for making avatar speak"""
    
    def __init__(self, avatar_agent: Optional['BaseAvatarAgent'] = None):
        super().__init__(name="SpeakAction", avatar_agent=avatar_agent)
    
    async def _execute(self, text: str, emotion: str = "neutral", 
                     language: str = "en", **kwargs) -> Dict[str, Any]:
        """Make avatar speak"""
        return await self.avatar_agent.speak(text, emotion, language)


class UpdateKnowledgeAction(AvatarAction):
    """Action for updating avatar knowledge"""
    
    def __init__(self, avatar_agent: Optional['BaseAvatarAgent'] = None):
        super().__init__(name="UpdateKnowledgeAction", avatar_agent=avatar_agent)
    
    async def _execute(self, content: str, category: str, 
                     tags: Optional[List[str]] = None, **kwargs) -> str:
        """Update avatar knowledge"""
        return await self.avatar_agent.add_knowledge(content, category, tags)


class BaseAvatarAgent(BaseAgent):
    """
    Base Avatar Agent - Comprehensive avatar system
    
    Integrates all avatar components:
    - Knowledge management
    - Personality system  
    - Content generation
    - API communication
    - Real-time interaction
    """
    
    def __init__(self, avatar_id: str, name: str = "", profile: str = "Avatar Agent",
                 config: Optional[Dict] = None):
        super().__init__(name=name or f"Avatar_{avatar_id}", profile=profile, config=config)
        
        self.avatar_id = avatar_id
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{avatar_id}")
        
        # Component configuration
        self.knowledge_config = self.config.get('knowledge', {})
        self.personality_config = self.config.get('personality', {})
        self.content_config = self.config.get('content_generation', {})
        self.api_config = self.config.get('api_client', {})
        
        # Initialize components
        self.knowledge_base = AvatarKnowledgeBase(avatar_id, self.knowledge_config)
        self.personality = AvatarPersonality(avatar_id, self.personality_config)
        self.content_generator = AvatarContentGenerator(
            avatar_id, self.knowledge_base, self.personality, self.content_config
        )
        self.api_client = AvatarApiClient(avatar_id, self.api_config)
        
        # Avatar state
        self.is_active = False
        self.last_interaction = None
        self.conversation_context: List[Dict[str, Any]] = []
        self.current_session_id = None
        
        # Performance metrics
        self.interaction_metrics = {
            'total_interactions': 0,
            'successful_responses': 0,
            'failed_responses': 0,
            'average_response_time': 0.0,
            'last_24h_interactions': 0
        }
        
        # Set up actions
        self.set_actions([
            GenerateAvatarResponse(self),
            SpeakAction(self),
            UpdateKnowledgeAction(self)
        ])
        
        # Watch for messages
        self._watch([Message])
        
        self.logger.info(f"Avatar {avatar_id} initialized with all components")
    
    async def initialize(self) -> None:
        """Initialize avatar and all components"""
        await super().initialize()
        
        # Initialize personality with default knowledge
        await self._load_initial_knowledge()
        
        # Set initial emotional state
        self.personality.set_emotion('friendly', 0.6, "Avatar initialization")
        
        self.is_active = True
        self.logger.info(f"Avatar {self.avatar_id} is now active and ready")
    
    async def _load_initial_knowledge(self):
        """Load initial knowledge base"""
        initial_knowledge = self.config.get('initial_knowledge', [])
        
        for knowledge_item in initial_knowledge:
            await self.knowledge_base.add_knowledge(
                content=knowledge_item['content'],
                category=knowledge_item.get('category', 'general'),
                tags=knowledge_item.get('tags', []),
                priority=knowledge_item.get('priority', 1)
            )
        
        # Add personality-based knowledge
        personality_desc = self.personality.get_avatar_description()
        await self.knowledge_base.add_knowledge(
            content=f"My personality: {personality_desc}",
            category="personality",
            tags=["self", "personality"],
            priority=3
        )
    
    async def _execute_action(self) -> Message:
        """Execute avatar-specific action based on latest message"""
        if not self.rc.memory:
            return Message(content="No messages to process", role=self.profile)
        
        latest_message = self.get_memories()[-1]
        
        try:
            # Parse message and determine action
            action_result = await self._process_message_content(latest_message)
            
            # Update conversation context
            self.conversation_context.append({
                'timestamp': datetime.now().isoformat(),
                'input_message': latest_message.content,
                'response': action_result,
                'emotion': self.personality.current_emotion.dominant_emotion
            })
            
            # Keep context manageable
            if len(self.conversation_context) > 50:
                self.conversation_context = self.conversation_context[-50:]
            
            # Update metrics
            self.interaction_metrics['total_interactions'] += 1
            self.interaction_metrics['successful_responses'] += 1
            self.last_interaction = datetime.now()
            
            return Message(
                content=action_result.get('response', str(action_result)),
                role=self.profile,
                cause_by=type(self._get_action())
            )
            
        except Exception as e:
            self.interaction_metrics['failed_responses'] += 1
            self.logger.error(f"Action execution failed: {e}")
            
            # Generate fallback response
            fallback = await self._generate_fallback_response(str(e))
            return Message(content=fallback, role=self.profile)
    
    async def _process_message_content(self, message: Message) -> Dict[str, Any]:
        """Process message content and determine appropriate response"""
        content = message.content
        
        # Extract context from message
        context = {
            'sender': message.role,
            'timestamp': datetime.now().isoformat(),
            'conversation_length': len(self.conversation_context),
            'recent_context': self.conversation_context[-5:] if self.conversation_context else []
        }
        
        # Determine generation mode based on content
        mode = self._determine_generation_mode(content)
        
        # Update personality emotion based on content
        await self._update_emotion_from_content(content)
        
        # Generate response
        response_result = await self.content_generator.generate_response(
            prompt=content,
            mode=mode,
            context=context,
            use_knowledge=True,
            use_personality=True
        )
        
        return response_result
    
    def _determine_generation_mode(self, content: str) -> str:
        """Determine appropriate generation mode from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['analyze', 'explain', 'how', 'why', 'what']):
            return 'analytical'
        elif any(word in content_lower for word in ['create', 'imagine', 'story', 'creative']):
            return 'creative'
        elif any(word in content_lower for word in ['help', 'support', 'problem', 'issue']):
            return 'supportive'  
        elif any(word in content_lower for word in ['learn', 'teach', 'understand', 'explain']):
            return 'educational'
        elif any(word in content_lower for word in ['fun', 'joke', 'play', 'game']):
            return 'playful'
        elif '?' in content:
            return 'conversational'
        else:
            return 'conversational'
    
    async def _update_emotion_from_content(self, content: str):
        """Update avatar emotion based on message content"""
        content_lower = content.lower()
        
        # Simple emotion detection
        if any(word in content_lower for word in ['happy', 'great', 'awesome', 'wonderful']):
            self.personality.set_emotion('happy', 0.7, "positive message received")
        elif any(word in content_lower for word in ['sad', 'problem', 'issue', 'wrong']):
            self.personality.set_emotion('empathetic', 0.6, "concern detected")
        elif any(word in content_lower for word in ['exciting', 'amazing', 'incredible']):
            self.personality.set_emotion('excited', 0.8, "exciting content")
        elif any(word in content_lower for word in ['complex', 'analyze', 'technical']):
            self.personality.set_emotion('analytical', 0.7, "analytical content")
        elif '?' in content:
            self.personality.set_emotion('curious', 0.5, "question received")
    
    async def _generate_fallback_response(self, error_msg: str) -> str:
        """Generate fallback response when normal processing fails"""
        fallback_responses = [
            "I'm having a bit of trouble processing that right now. Could you rephrase?",
            "Let me think about that differently. Can you provide more context?",
            "I want to give you a good response. Could you clarify what you're looking for?",
            "I'm working through that. In the meantime, is there something else I can help with?"
        ]
        
        # Select based on personality
        if self.personality.get_trait_value('agreeableness') > 0:
            return fallback_responses[0]
        elif self.personality.get_trait_value('conscientiousness') > 0:
            return fallback_responses[2]
        else:
            return fallback_responses[1]
    
    async def _handle_action(self, action: AvatarAction, *args, **kwargs) -> Any:
        """Handle action execution"""
        if isinstance(action, GenerateAvatarResponse):
            return await self.generate_response(*args, **kwargs)
        elif isinstance(action, SpeakAction):
            return await self.speak(*args, **kwargs)
        elif isinstance(action, UpdateKnowledgeAction):
            return await self.add_knowledge(*args, **kwargs)
        else:
            raise NotImplementedError(f"Action {type(action)} not implemented")
    
    # Public API methods
    
    async def generate_response(self, prompt: str, mode: str = "conversational",
                              context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate avatar response"""
        return await self.content_generator.generate_response(prompt, mode, context)
    
    async def speak(self, text: str, emotion: str = "neutral", 
                   language: str = "en") -> Dict[str, Any]:
        """Make avatar speak"""
        async with self.api_client:
            return await self.api_client.speak(text, emotion, language)
    
    async def add_knowledge(self, content: str, category: str,
                          tags: Optional[List[str]] = None,
                          priority: int = 1) -> str:
        """Add knowledge to avatar"""
        return await self.knowledge_base.add_knowledge(
            content, category, tags, priority
        )
    
    async def update_personality(self, trait_name: str, value: float,
                               reason: str = "") -> bool:
        """Update personality trait"""
        return self.personality.update_trait(trait_name, value, reason)
    
    async def set_emotion(self, emotion: str, intensity: float = 0.7,
                         context: Optional[str] = None):
        """Set avatar emotion"""
        self.personality.set_emotion(emotion, intensity, context)
    
    async def start_conversation_session(self, session_id: str):
        """Start new conversation session"""
        self.current_session_id = session_id
        self.conversation_context = []
        self.personality.set_emotion('friendly', 0.6, f"Starting session {session_id}")
        self.logger.info(f"Started conversation session: {session_id}")
    
    async def end_conversation_session(self):
        """End current conversation session"""
        if self.current_session_id:
            session_id = self.current_session_id
            self.current_session_id = None
            
            # Archive conversation context if needed
            if len(self.conversation_context) > 0:
                await self.knowledge_base.add_knowledge(
                    content=f"Conversation session {session_id} summary: {len(self.conversation_context)} interactions",
                    category="conversation_history",
                    tags=["session", "history"],
                    ttl_hours=24 * 7  # Keep for a week
                )
            
            self.conversation_context = []
            self.personality.set_emotion('neutral', 0.5, f"Ended session {session_id}")
            self.logger.info(f"Ended conversation session: {session_id}")
    
    def get_avatar_status(self) -> Dict[str, Any]:
        """Get comprehensive avatar status"""
        return {
            'avatar_id': self.avatar_id,
            'name': self.name,
            'is_active': self.is_active,
            'current_session': self.current_session_id,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'conversation_length': len(self.conversation_context),
            'current_emotion': self.personality.current_emotion.dominant_emotion,
            'emotion_intensity': self.personality.current_emotion.intensity,
            'knowledge_stats': self.knowledge_base.get_stats(),
            'personality_stats': self.personality.get_stats(),
            'content_stats': self.content_generator.get_stats(),
            'api_stats': self.api_client.get_stats(),
            'interaction_metrics': self.interaction_metrics,
            'agent_metrics': self.metrics
        }
    
    async def export_avatar_data(self) -> Dict[str, Any]:
        """Export complete avatar data"""
        return {
            'avatar_id': self.avatar_id,
            'config': self.config,
            'knowledge_base': await self.knowledge_base.export_knowledge(),
            'personality': self.personality.export_personality(),
            'conversation_context': self.conversation_context,
            'interaction_metrics': self.interaction_metrics,
            'content_history': await self.content_generator.export_history(limit=100),
            'export_timestamp': datetime.now().isoformat()
        }
    
    async def import_avatar_data(self, avatar_data: Dict[str, Any]) -> bool:
        """Import avatar data"""
        try:
            # Import knowledge
            if 'knowledge_base' in avatar_data:
                await self.knowledge_base.import_knowledge(avatar_data['knowledge_base'])
            
            # Import personality
            if 'personality' in avatar_data:
                self.personality.import_personality(avatar_data['personality'])
            
            # Import conversation context
            if 'conversation_context' in avatar_data:
                self.conversation_context = avatar_data['conversation_context']
            
            # Import metrics
            if 'interaction_metrics' in avatar_data:
                self.interaction_metrics.update(avatar_data['interaction_metrics'])
            
            self.logger.info("Avatar data imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import avatar data: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup avatar resources"""
        await super().cleanup()
        
        # Close components
        if hasattr(self.knowledge_base, 'close'):
            await self.knowledge_base.close()
        
        if hasattr(self.api_client, 'close'):
            await self.api_client.close()
        
        self.is_active = False
        self.logger.info(f"Avatar {self.avatar_id} cleanup completed")