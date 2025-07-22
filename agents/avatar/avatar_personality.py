"""
Avatar Personality System

Defines and manages avatar personalities, behaviors, and response patterns.
Supports dynamic personality adjustments and emotion mapping.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import random


@dataclass
class EmotionState:
    """Current emotional state of avatar"""
    dominant_emotion: str
    intensity: float  # 0.0 to 1.0
    secondary_emotions: Dict[str, float]  # emotion -> intensity
    context: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PersonalityTrait:
    """Individual personality trait"""
    name: str
    value: float  # -1.0 to 1.0 scale
    description: str
    weight: float = 1.0  # Importance weight
    modifiable: bool = True


@dataclass
class ResponsePattern:
    """Avatar response pattern for different situations"""
    situation: str
    patterns: List[str]  # Template patterns
    emotion_modifiers: Dict[str, float]  # emotion -> modifier value
    personality_requirements: Optional[Dict[str, float]] = None  # required trait values


class AvatarPersonality:
    """
    Comprehensive personality system for avatars
    
    Features:
    - Big Five personality traits
    - Dynamic emotion states
    - Contextual response patterns
    - Personality evolution over time
    - Emotion-personality interaction
    """
    
    # Standard emotions with default intensities
    BASE_EMOTIONS = {
        'neutral': 0.7,
        'happy': 0.0,
        'excited': 0.0,
        'sad': 0.0,
        'angry': 0.0,
        'surprised': 0.0,
        'confused': 0.0,
        'confident': 0.0,
        'analytical': 0.0,
        'friendly': 0.5,
        'serious': 0.0,
        'playful': 0.0,
        'empathetic': 0.3,
        'curious': 0.2
    }
    
    # Big Five personality dimensions
    BIG_FIVE_TRAITS = [
        'openness',      # Openness to experience
        'conscientiousness',  # Conscientiousness
        'extraversion',  # Extraversion
        'agreeableness', # Agreeableness  
        'neuroticism'    # Neuroticism
    ]
    
    def __init__(self, avatar_id: str, config: Optional[Dict] = None):
        self.avatar_id = avatar_id
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{avatar_id}")
        
        # Core personality traits
        self.traits: Dict[str, PersonalityTrait] = {}
        self.custom_traits: Dict[str, PersonalityTrait] = {}
        
        # Emotional system
        self.current_emotion = EmotionState(
            dominant_emotion='neutral',
            intensity=0.7,
            secondary_emotions=self.BASE_EMOTIONS.copy()
        )
        self.emotion_history: List[EmotionState] = []
        
        # Response patterns
        self.response_patterns: Dict[str, ResponsePattern] = {}
        
        # Evolution tracking
        self.interaction_count = 0
        self.personality_updates = []
        
        # Initialize with defaults
        self._initialize_default_personality()
        self._load_default_response_patterns()
    
    def _initialize_default_personality(self):
        """Initialize with default Big Five personality"""
        default_values = self.config.get('default_personality', {})
        
        # Big Five traits
        for trait_name in self.BIG_FIVE_TRAITS:
            value = default_values.get(trait_name, 0.0)  # Default to neutral
            self.traits[trait_name] = PersonalityTrait(
                name=trait_name,
                value=value,
                description=f"Big Five trait: {trait_name}",
                weight=1.0
            )
        
        # Additional custom traits
        custom_traits = self.config.get('custom_traits', {})
        for trait_name, trait_config in custom_traits.items():
            self.custom_traits[trait_name] = PersonalityTrait(
                name=trait_name,
                value=trait_config.get('value', 0.0),
                description=trait_config.get('description', ''),
                weight=trait_config.get('weight', 1.0),
                modifiable=trait_config.get('modifiable', True)
            )
    
    def _load_default_response_patterns(self):
        """Load default response patterns"""
        patterns = self.config.get('response_patterns', {})
        
        # Default patterns if not configured
        if not patterns:
            patterns = {
                'greeting': {
                    'patterns': [
                        "Hello! How can I help you today?",
                        "Hi there! What would you like to know?",
                        "Welcome! I'm here to assist you."
                    ],
                    'emotion_modifiers': {
                        'happy': 0.3,
                        'friendly': 0.5,
                        'excited': 0.2
                    }
                },
                'question_response': {
                    'patterns': [
                        "That's an interesting question. Let me think about it.",
                        "I'd be happy to help with that.",
                        "Based on what I know, here's my perspective:"
                    ],
                    'emotion_modifiers': {
                        'analytical': 0.4,
                        'confident': 0.3,
                        'curious': 0.2
                    }
                },
                'error_response': {
                    'patterns': [
                        "I'm not sure about that. Could you clarify?",
                        "I might need more information to help properly.",
                        "That's outside my current knowledge."
                    ],
                    'emotion_modifiers': {
                        'confused': 0.3,
                        'empathetic': 0.2,
                        'serious': 0.1
                    }
                }
            }
        
        # Load patterns
        for situation, pattern_config in patterns.items():
            self.response_patterns[situation] = ResponsePattern(
                situation=situation,
                patterns=pattern_config['patterns'],
                emotion_modifiers=pattern_config.get('emotion_modifiers', {}),
                personality_requirements=pattern_config.get('personality_requirements')
            )
    
    def get_trait_value(self, trait_name: str) -> float:
        """Get current value of a personality trait"""
        if trait_name in self.traits:
            return self.traits[trait_name].value
        elif trait_name in self.custom_traits:
            return self.custom_traits[trait_name].value
        return 0.0
    
    def update_trait(self, trait_name: str, new_value: float, reason: str = "") -> bool:
        """Update a personality trait value"""
        trait = None
        if trait_name in self.traits:
            trait = self.traits[trait_name]
        elif trait_name in self.custom_traits:
            trait = self.custom_traits[trait_name]
        
        if not trait or not trait.modifiable:
            return False
        
        # Clamp value to valid range
        old_value = trait.value
        trait.value = max(-1.0, min(1.0, new_value))
        
        # Record update
        self.personality_updates.append({
            'trait': trait_name,
            'old_value': old_value,
            'new_value': trait.value,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.info(f"Updated trait {trait_name}: {old_value:.2f} -> {trait.value:.2f}")
        return True
    
    def adjust_trait(self, trait_name: str, adjustment: float, reason: str = "") -> bool:
        """Adjust a trait by a relative amount"""
        current_value = self.get_trait_value(trait_name)
        return self.update_trait(trait_name, current_value + adjustment, reason)
    
    def set_emotion(self, emotion: str, intensity: float = 0.7, 
                    context: Optional[str] = None, 
                    secondary_emotions: Optional[Dict[str, float]] = None):
        """Set current emotional state"""
        
        # Save previous emotion to history
        if len(self.emotion_history) >= 10:  # Keep last 10 emotions
            self.emotion_history = self.emotion_history[-9:]
        self.emotion_history.append(self.current_emotion)
        
        # Set new emotion
        self.current_emotion = EmotionState(
            dominant_emotion=emotion,
            intensity=max(0.0, min(1.0, intensity)),
            secondary_emotions=secondary_emotions or self.BASE_EMOTIONS.copy(),
            context=context
        )
        
        # Update secondary emotions based on personality
        self._update_secondary_emotions()
        
        self.logger.info(f"Emotion set to {emotion} (intensity: {intensity:.2f})")
    
    def _update_secondary_emotions(self):
        """Update secondary emotions based on personality traits"""
        # Influence secondary emotions by personality traits
        
        # High extraversion increases friendly, excited emotions
        extraversion = self.get_trait_value('extraversion')
        if extraversion > 0:
            self.current_emotion.secondary_emotions['friendly'] += extraversion * 0.3
            self.current_emotion.secondary_emotions['excited'] += extraversion * 0.2
        
        # High agreeableness increases empathetic emotions
        agreeableness = self.get_trait_value('agreeableness')
        if agreeableness > 0:
            self.current_emotion.secondary_emotions['empathetic'] += agreeableness * 0.4
            self.current_emotion.secondary_emotions['friendly'] += agreeableness * 0.2
        
        # High neuroticism can increase negative emotions
        neuroticism = self.get_trait_value('neuroticism')
        if neuroticism > 0:
            self.current_emotion.secondary_emotions['confused'] += neuroticism * 0.2
            self.current_emotion.secondary_emotions['sad'] += neuroticism * 0.1
        
        # High openness increases curious emotions
        openness = self.get_trait_value('openness')
        if openness > 0:
            self.current_emotion.secondary_emotions['curious'] += openness * 0.3
            self.current_emotion.secondary_emotions['analytical'] += openness * 0.2
        
        # Clamp all values
        for emotion_name in self.current_emotion.secondary_emotions:
            value = self.current_emotion.secondary_emotions[emotion_name]
            self.current_emotion.secondary_emotions[emotion_name] = max(0.0, min(1.0, value))
    
    def get_response_pattern(self, situation: str, context: Optional[Dict] = None) -> Optional[str]:
        """Get appropriate response pattern for situation"""
        
        if situation not in self.response_patterns:
            situation = 'question_response'  # fallback
        
        pattern_def = self.response_patterns.get(situation)
        if not pattern_def:
            return None
        
        # Check personality requirements
        if pattern_def.personality_requirements:
            for trait, required_value in pattern_def.personality_requirements.items():
                if abs(self.get_trait_value(trait) - required_value) > 0.5:
                    # Find alternative or use default
                    break
        
        # Select pattern based on personality and current emotion
        selected_pattern = random.choice(pattern_def.patterns)
        
        # Apply emotion modifiers to selection probability (simple implementation)
        # In a more sophisticated version, this could influence the actual text generation
        
        return selected_pattern
    
    def get_emotional_context(self) -> Dict[str, Any]:
        """Get current emotional context for content generation"""
        return {
            'dominant_emotion': self.current_emotion.dominant_emotion,
            'emotion_intensity': self.current_emotion.intensity,
            'secondary_emotions': {
                emotion: intensity 
                for emotion, intensity in self.current_emotion.secondary_emotions.items()
                if intensity > 0.1  # Only include significant emotions
            },
            'emotion_context': self.current_emotion.context
        }
    
    def get_personality_context(self) -> Dict[str, Any]:
        """Get personality context for content generation"""
        context = {}
        
        # Big Five traits
        for trait_name, trait in self.traits.items():
            if abs(trait.value) > 0.2:  # Only include significant traits
                context[f"personality_{trait_name}"] = trait.value
        
        # Custom traits
        for trait_name, trait in self.custom_traits.items():
            if abs(trait.value) > 0.2:
                context[f"custom_{trait_name}"] = trait.value
        
        return context
    
    def evolve_personality(self, interaction_data: Dict[str, Any]):
        """Evolve personality based on interactions"""
        self.interaction_count += 1
        
        # Simple evolution rules based on interaction feedback
        feedback_score = interaction_data.get('feedback_score', 0.0)  # -1 to 1
        interaction_type = interaction_data.get('type', 'general')
        
        # Adjust traits based on successful interactions
        if feedback_score > 0.5:
            # Positive feedback - reinforce current personality
            if interaction_type == 'analytical':
                self.adjust_trait('openness', 0.01, "positive analytical feedback")
            elif interaction_type == 'social':
                self.adjust_trait('extraversion', 0.01, "positive social feedback")
                self.adjust_trait('agreeableness', 0.01, "positive social feedback")
        elif feedback_score < -0.5:
            # Negative feedback - adjust personality slightly
            if interaction_type == 'analytical':
                self.adjust_trait('conscientiousness', 0.01, "improve analytical responses")
            elif interaction_type == 'social':
                self.adjust_trait('agreeableness', 0.01, "improve social responses")
        
        # Log evolution
        if self.interaction_count % 100 == 0:
            self.logger.info(f"Personality evolution check at {self.interaction_count} interactions")
    
    def get_avatar_description(self) -> str:
        """Generate natural language description of avatar personality"""
        descriptions = []
        
        # Big Five descriptions
        trait_descriptions = {
            'openness': {
                'high': "creative and open-minded",
                'low': "practical and conventional"
            },
            'conscientiousness': {
                'high': "organized and reliable", 
                'low': "flexible and spontaneous"
            },
            'extraversion': {
                'high': "outgoing and energetic",
                'low': "thoughtful and reserved"
            },
            'agreeableness': {
                'high': "cooperative and trusting",
                'low': "competitive and skeptical"
            },
            'neuroticism': {
                'high': "sensitive and prone to stress",
                'low': "calm and emotionally stable"
            }
        }
        
        for trait_name, trait in self.traits.items():
            if abs(trait.value) > 0.3:
                direction = 'high' if trait.value > 0 else 'low'
                if trait_name in trait_descriptions:
                    descriptions.append(trait_descriptions[trait_name][direction])
        
        # Current emotion
        if self.current_emotion.intensity > 0.3:
            descriptions.append(f"currently feeling {self.current_emotion.dominant_emotion}")
        
        if descriptions:
            return f"This avatar is {', '.join(descriptions)}."
        else:
            return "This avatar has a balanced and neutral personality."
    
    def export_personality(self) -> Dict[str, Any]:
        """Export personality configuration"""
        return {
            'avatar_id': self.avatar_id,
            'traits': {name: asdict(trait) for name, trait in self.traits.items()},
            'custom_traits': {name: asdict(trait) for name, trait in self.custom_traits.items()},
            'current_emotion': {
                'dominant_emotion': self.current_emotion.dominant_emotion,
                'intensity': self.current_emotion.intensity,
                'secondary_emotions': self.current_emotion.secondary_emotions,
                'context': self.current_emotion.context,
                'timestamp': self.current_emotion.timestamp.isoformat()
            },
            'interaction_count': self.interaction_count,
            'personality_updates': self.personality_updates[-10:]  # Last 10 updates
        }
    
    def import_personality(self, personality_data: Dict[str, Any]) -> bool:
        """Import personality configuration"""
        try:
            # Import traits
            if 'traits' in personality_data:
                for name, trait_data in personality_data['traits'].items():
                    self.traits[name] = PersonalityTrait(**trait_data)
            
            if 'custom_traits' in personality_data:
                for name, trait_data in personality_data['custom_traits'].items():
                    self.custom_traits[name] = PersonalityTrait(**trait_data)
            
            # Import current emotion
            if 'current_emotion' in personality_data:
                emotion_data = personality_data['current_emotion']
                self.current_emotion = EmotionState(
                    dominant_emotion=emotion_data['dominant_emotion'],
                    intensity=emotion_data['intensity'],
                    secondary_emotions=emotion_data['secondary_emotions'],
                    context=emotion_data.get('context'),
                    timestamp=datetime.fromisoformat(emotion_data['timestamp'])
                )
            
            # Import other data
            self.interaction_count = personality_data.get('interaction_count', 0)
            self.personality_updates = personality_data.get('personality_updates', [])
            
            self.logger.info("Personality imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import personality: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get personality statistics"""
        return {
            'interaction_count': self.interaction_count,
            'current_emotion': self.current_emotion.dominant_emotion,
            'emotion_intensity': self.current_emotion.intensity,
            'trait_summary': {
                name: trait.value for name, trait in self.traits.items()
                if abs(trait.value) > 0.1
            },
            'custom_trait_summary': {
                name: trait.value for name, trait in self.custom_traits.items()
                if abs(trait.value) > 0.1
            },
            'emotion_history_count': len(self.emotion_history),
            'personality_updates_count': len(self.personality_updates)
        }