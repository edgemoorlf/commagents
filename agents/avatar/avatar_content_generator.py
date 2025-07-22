"""
Avatar Content Generator

Generates full avatar responses from simple prompts using LLM integration,
personality context, and knowledge base information.
"""
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.logs import logger

from .avatar_knowledge_base import AvatarKnowledgeBase
from .avatar_personality import AvatarPersonality


class AvatarContentAction(Action):
    """Action for generating avatar content"""
    
    def __init__(self, name: str = "AvatarContentGeneration", 
                 knowledge_base: Optional[AvatarKnowledgeBase] = None,
                 personality: Optional[AvatarPersonality] = None,
                 context: Optional[Dict] = None):
        super().__init__(name=name, context=context)
        self.knowledge_base = knowledge_base
        self.personality = personality
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def run(self, prompt: str, generation_mode: str = "conversational",
                  context: Optional[Dict[str, Any]] = None) -> str:
        """Generate avatar content from prompt"""
        
        # Build comprehensive prompt with context
        enhanced_prompt = await self._build_enhanced_prompt(
            prompt, generation_mode, context
        )
        
        # Generate content using LLM
        response = await self._aask(enhanced_prompt)
        
        self.logger.info(f"Generated content for prompt: {prompt[:50]}...")
        return response
    
    async def _build_enhanced_prompt(self, prompt: str, mode: str, 
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """Build enhanced prompt with personality and knowledge context"""
        
        prompt_parts = []
        
        # Add personality context
        if self.personality:
            personality_desc = self.personality.get_avatar_description()
            emotional_context = self.personality.get_emotional_context()
            personality_context = self.personality.get_personality_context()
            
            prompt_parts.append(f"Personality: {personality_desc}")
            
            if emotional_context['dominant_emotion'] != 'neutral':
                emotion = emotional_context['dominant_emotion']
                intensity = emotional_context['emotion_intensity']
                prompt_parts.append(f"Current emotion: {emotion} (intensity: {intensity:.1f})")
        
        # Add relevant knowledge
        if self.knowledge_base and context:
            knowledge_summary = await self.knowledge_base.get_context_summary(context)
            if knowledge_summary != "No specific contextual knowledge available.":
                prompt_parts.append(f"Relevant knowledge: {knowledge_summary}")
        
        # Add generation mode instructions
        mode_instructions = self._get_mode_instructions(mode)
        if mode_instructions:
            prompt_parts.append(mode_instructions)
        
        # Combine with original prompt
        if prompt_parts:
            context_section = "\n".join(prompt_parts)
            enhanced_prompt = f"{context_section}\n\nUser input: {prompt}\n\nResponse:"
        else:
            enhanced_prompt = f"User input: {prompt}\n\nResponse:"
        
        return enhanced_prompt
    
    def _get_mode_instructions(self, mode: str) -> str:
        """Get mode-specific generation instructions"""
        instructions = {
            "conversational": "Respond in a natural, conversational tone. Be engaging and personable.",
            "analytical": "Provide a detailed, analytical response. Focus on facts and logical reasoning.",
            "creative": "Be creative and imaginative in your response. Use vivid language and metaphors.",
            "educational": "Explain concepts clearly and provide educational value. Use examples when helpful.",
            "supportive": "Be empathetic and supportive. Focus on understanding and helping the user.",
            "professional": "Maintain a professional tone. Be clear, concise, and authoritative.",
            "playful": "Be playful and fun. Use humor and casual language when appropriate."
        }
        return instructions.get(mode, "")


class AvatarContentGenerator:
    """
    Main content generation system for avatars
    
    Features:
    - Single-phrase to complete response generation
    - Personality-aware content creation
    - Knowledge-enhanced responses
    - Multiple generation modes
    - Response quality tracking
    """
    
    def __init__(self, avatar_id: str, 
                 knowledge_base: Optional[AvatarKnowledgeBase] = None,
                 personality: Optional[AvatarPersonality] = None,
                 config: Optional[Dict] = None):
        self.avatar_id = avatar_id
        self.knowledge_base = knowledge_base
        self.personality = personality
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{avatar_id}")
        
        # Content generation action
        self.content_action = AvatarContentAction(
            knowledge_base=knowledge_base,
            personality=personality
        )
        
        # Response tracking
        self.generation_history: List[Dict[str, Any]] = []
        self.quality_metrics = {
            'total_generations': 0,
            'average_length': 0,
            'mode_distribution': {},
            'recent_ratings': []
        }
        
        # Generation settings
        self.default_mode = self.config.get('default_generation_mode', 'conversational')
        self.max_length = self.config.get('max_response_length', 500)
        self.min_length = self.config.get('min_response_length', 20)
    
    async def generate_response(self, prompt: str,
                              mode: Optional[str] = None,
                              context: Optional[Dict[str, Any]] = None,
                              use_knowledge: bool = True,
                              use_personality: bool = True) -> Dict[str, Any]:
        """
        Generate a complete avatar response from a simple prompt
        
        Args:
            prompt: Input prompt or phrase
            mode: Generation mode (conversational, analytical, creative, etc.)
            context: Additional context for generation
            use_knowledge: Whether to use knowledge base
            use_personality: Whether to apply personality context
            
        Returns:
            Dictionary with response and metadata
        """
        
        start_time = datetime.now()
        generation_mode = mode or self.default_mode
        
        try:
            # Prepare context
            full_context = context or {}
            
            # Add avatar-specific context
            full_context.update({
                'avatar_id': self.avatar_id,
                'generation_mode': generation_mode,
                'timestamp': start_time.isoformat()
            })
            
            # Update personality emotion if context suggests it
            if use_personality and self.personality and context:
                await self._update_emotion_from_context(context)
            
            # Generate content
            response = await self.content_action.run(
                prompt=prompt,
                generation_mode=generation_mode,
                context=full_context if use_knowledge else None
            )
            
            # Post-process response
            processed_response = await self._post_process_response(
                response, generation_mode
            )
            
            # Calculate metrics
            duration = (datetime.now() - start_time).total_seconds()
            response_length = len(processed_response)
            
            # Record generation
            generation_record = {
                'id': f"{self.avatar_id}_{int(start_time.timestamp())}",
                'prompt': prompt,
                'response': processed_response,
                'mode': generation_mode,
                'context': full_context,
                'duration_seconds': duration,
                'response_length': response_length,
                'timestamp': start_time.isoformat(),
                'used_knowledge': use_knowledge,
                'used_personality': use_personality
            }
            
            self.generation_history.append(generation_record)
            await self._update_metrics(generation_record)
            
            # Update personality based on interaction
            if use_personality and self.personality:
                interaction_data = {
                    'type': generation_mode,
                    'feedback_score': 0.0,  # Will be updated when feedback is received
                    'prompt_length': len(prompt),
                    'response_length': response_length
                }
                self.personality.evolve_personality(interaction_data)
            
            # Prepare result
            result = {
                'response': processed_response,
                'metadata': {
                    'generation_id': generation_record['id'],
                    'mode': generation_mode,
                    'duration_seconds': duration,
                    'response_length': response_length,
                    'personality_applied': use_personality,
                    'knowledge_applied': use_knowledge,
                    'emotion_state': (
                        self.personality.get_emotional_context() 
                        if use_personality and self.personality else None
                    )
                }
            }
            
            self.logger.info(f"Generated response for '{prompt[:30]}...' in {duration:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            
            # Return fallback response
            fallback_response = await self._generate_fallback_response(prompt)
            return {
                'response': fallback_response,
                'metadata': {
                    'generation_id': f"fallback_{int(start_time.timestamp())}",
                    'mode': 'fallback',
                    'error': str(e),
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                }
            }
    
    async def _update_emotion_from_context(self, context: Dict[str, Any]):
        """Update avatar emotion based on context"""
        if not self.personality:
            return
            
        # Simple emotion detection from context
        emotion_indicators = {
            'happy': ['celebration', 'success', 'achievement', 'good_news'],
            'excited': ['opportunity', 'new', 'amazing', 'incredible'],
            'sad': ['problem', 'failure', 'loss', 'disappointment'],
            'analytical': ['analysis', 'data', 'research', 'technical'],
            'serious': ['important', 'urgent', 'critical', 'official'],
            'confused': ['unclear', 'confusing', 'complex', 'uncertain']
        }
        
        context_text = str(context).lower()
        
        for emotion, indicators in emotion_indicators.items():
            if any(indicator in context_text for indicator in indicators):
                current_intensity = self.personality.current_emotion.intensity
                new_intensity = min(1.0, current_intensity + 0.2)
                self.personality.set_emotion(emotion, new_intensity, str(context))
                break
    
    async def _post_process_response(self, response: str, mode: str) -> str:
        """Post-process generated response"""
        processed = response.strip()
        
        # Length constraints
        if len(processed) > self.max_length:
            # Truncate at sentence boundary if possible
            sentences = processed.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= self.max_length:
                    truncated += sentence + '. '
                else:
                    break
            processed = truncated.strip()
            if not processed.endswith('.'):
                processed += "..."
        
        elif len(processed) < self.min_length:
            # Add more context or explanation
            if mode == 'conversational':
                processed += " I'd be happy to discuss this further if you'd like more details."
            elif mode == 'analytical':
                processed += " This analysis could be expanded with additional data points."
        
        # Mode-specific adjustments
        if mode == 'creative' and not any(char in processed for char in '!?'):
            processed += "!"
        elif mode == 'professional' and processed.endswith('!'):
            processed = processed[:-1] + '.'
        
        return processed
    
    async def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when main generation fails"""
        fallbacks = [
            f"I understand you're asking about '{prompt[:50]}...'. Let me help you with that.",
            "I'm processing your request. Could you provide a bit more context?",
            "That's an interesting point. I'd like to give you a thoughtful response.",
            "I'm here to help. Let me think about the best way to address your question."
        ]
        
        # Select based on prompt characteristics
        if '?' in prompt:
            return fallbacks[1]
        elif len(prompt) > 100:
            return fallbacks[2]
        else:
            return fallbacks[0]
    
    async def _update_metrics(self, generation_record: Dict[str, Any]):
        """Update quality metrics"""
        self.quality_metrics['total_generations'] += 1
        
        # Update average length
        total_length = (
            self.quality_metrics['average_length'] * 
            (self.quality_metrics['total_generations'] - 1) +
            generation_record['response_length']
        )
        self.quality_metrics['average_length'] = (
            total_length / self.quality_metrics['total_generations']
        )
        
        # Update mode distribution
        mode = generation_record['mode']
        self.quality_metrics['mode_distribution'][mode] = (
            self.quality_metrics['mode_distribution'].get(mode, 0) + 1
        )
    
    async def rate_response(self, generation_id: str, rating: float, 
                          feedback: Optional[str] = None) -> bool:
        """Rate a generated response for quality tracking"""
        
        # Find the generation record
        generation_record = None
        for record in self.generation_history:
            if record['id'] == generation_id:
                generation_record = record
                break
        
        if not generation_record:
            return False
        
        # Add rating to record
        generation_record['rating'] = rating
        generation_record['feedback'] = feedback
        generation_record['rated_at'] = datetime.now().isoformat()
        
        # Update metrics
        self.quality_metrics['recent_ratings'].append(rating)
        if len(self.quality_metrics['recent_ratings']) > 100:
            self.quality_metrics['recent_ratings'] = (
                self.quality_metrics['recent_ratings'][-100:]
            )
        
        # Update personality evolution with feedback
        if self.personality:
            interaction_data = {
                'type': generation_record['mode'],
                'feedback_score': rating,
                'prompt_length': len(generation_record['prompt']),
                'response_length': generation_record['response_length']
            }
            self.personality.evolve_personality(interaction_data)
        
        self.logger.info(f"Rated response {generation_id}: {rating}")
        return True
    
    async def get_generation_modes(self) -> List[str]:
        """Get available generation modes"""
        return [
            'conversational',
            'analytical', 
            'creative',
            'educational',
            'supportive',
            'professional',
            'playful'
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get content generation statistics"""
        recent_ratings = self.quality_metrics['recent_ratings']
        avg_rating = sum(recent_ratings) / len(recent_ratings) if recent_ratings else 0.0
        
        return {
            'total_generations': self.quality_metrics['total_generations'],
            'average_response_length': self.quality_metrics['average_length'],
            'mode_distribution': self.quality_metrics['mode_distribution'],
            'average_rating': avg_rating,
            'recent_generations': len([
                r for r in self.generation_history 
                if (datetime.now() - datetime.fromisoformat(r['timestamp'])).days < 1
            ]),
            'history_size': len(self.generation_history)
        }
    
    async def export_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Export generation history"""
        history = self.generation_history
        if limit:
            history = history[-limit:]
        return history
    
    async def clear_history(self, older_than_days: Optional[int] = None) -> int:
        """Clear generation history"""
        if older_than_days is None:
            cleared_count = len(self.generation_history)
            self.generation_history.clear()
        else:
            cutoff_date = datetime.now().timestamp() - (older_than_days * 24 * 3600)
            original_count = len(self.generation_history)
            
            self.generation_history = [
                record for record in self.generation_history
                if datetime.fromisoformat(record['timestamp']).timestamp() > cutoff_date
            ]
            
            cleared_count = original_count - len(self.generation_history)
        
        self.logger.info(f"Cleared {cleared_count} generation records")
        return cleared_count