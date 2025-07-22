"""
Avatar API Client

Handles communication with external avatar service providers.
Supports multiple providers with unified interface and retry logic.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import json


class AvatarProvider(Enum):
    """Supported avatar providers"""
    DUIX = "duix"
    SENSE_AVATAR = "sense_avatar"
    AKOOL = "akool"
    LOCAL = "local"
    MOCK = "mock"


class AvatarApiError(Exception):
    """Avatar API related errors"""
    pass


class AvatarApiClient:
    """
    Unified client for multiple avatar service providers
    
    Features:
    - Multi-provider support
    - Retry logic with exponential backoff
    - Health monitoring
    - Rate limiting
    - Response caching
    - Emotion and gesture mapping
    """
    
    def __init__(self, avatar_id: str, config: Optional[Dict] = None):
        self.avatar_id = avatar_id
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{avatar_id}")
        
        # Provider configuration
        self.primary_provider = AvatarProvider(
            self.config.get('primary_provider', 'local')
        )
        self.fallback_providers = [
            AvatarProvider(p) for p in self.config.get('fallback_providers', [])
        ]
        
        # API configuration
        self.endpoints = self.config.get('endpoints', {})
        self.api_keys = self.config.get('api_keys', {})
        self.timeouts = self.config.get('timeouts', {})
        
        # Request configuration
        self.default_timeout = self.config.get('default_timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        
        # Rate limiting
        self.rate_limits = self.config.get('rate_limits', {})
        self.request_history: Dict[str, List[datetime]] = {}
        
        # Health monitoring
        self.provider_health: Dict[AvatarProvider, Dict[str, Any]] = {}
        self._init_provider_health()
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Response cache (simple in-memory cache)
        self.cache_enabled = self.config.get('enable_cache', True)
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)  # 5 minutes
        self.response_cache: Dict[str, Dict[str, Any]] = {}
    
    def _init_provider_health(self):
        """Initialize provider health tracking"""
        for provider in [self.primary_provider] + self.fallback_providers:
            self.provider_health[provider] = {
                'status': 'unknown',
                'last_check': None,
                'response_time': 0.0,
                'error_count': 0,
                'success_count': 0,
                'last_error': None
            }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def speak(self, text: str, emotion: str = "neutral", 
                   language: str = "en", voice_id: Optional[str] = None,
                   gesture: Optional[str] = None) -> Dict[str, Any]:
        """
        Make avatar speak with given text and emotion
        
        Args:
            text: Text to speak
            emotion: Emotion to express (happy, sad, excited, etc.)
            language: Language code (en, zh, es, etc.) 
            voice_id: Specific voice ID to use
            gesture: Gesture to perform while speaking
            
        Returns:
            Response with status and any avatar response data
        """
        
        request_data = {
            'text': text,
            'emotion': emotion,
            'language': language,
            'avatar_id': self.avatar_id
        }
        
        if voice_id:
            request_data['voice_id'] = voice_id
        if gesture:
            request_data['gesture'] = gesture
        
        # Try providers in order
        providers_to_try = [self.primary_provider] + self.fallback_providers
        last_error = None
        
        for provider in providers_to_try:
            if not await self._is_provider_healthy(provider):
                continue
                
            try:
                response = await self._call_provider_speak(provider, request_data)
                await self._update_provider_health(provider, True, response.get('response_time', 0))
                return response
                
            except Exception as e:
                last_error = e
                await self._update_provider_health(provider, False, 0, str(e))
                self.logger.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        # All providers failed
        error_msg = f"All avatar providers failed. Last error: {last_error}"
        self.logger.error(error_msg)
        raise AvatarApiError(error_msg)
    
    async def _call_provider_speak(self, provider: AvatarProvider, 
                                 request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call specific provider's speak API"""
        
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key('speak', provider, request_data)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        # Check rate limits
        await self._check_rate_limit(provider)
        
        start_time = datetime.now()
        
        try:
            if provider == AvatarProvider.DUIX:
                response = await self._call_duix_speak(request_data)
            elif provider == AvatarProvider.SENSE_AVATAR:
                response = await self._call_sense_avatar_speak(request_data)
            elif provider == AvatarProvider.AKOOL:
                response = await self._call_akool_speak(request_data)
            elif provider == AvatarProvider.LOCAL:
                response = await self._call_local_speak(request_data)
            elif provider == AvatarProvider.MOCK:
                response = await self._call_mock_speak(request_data)
            else:
                raise AvatarApiError(f"Unsupported provider: {provider.value}")
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            response['response_time'] = response_time
            response['provider'] = provider.value
            response['timestamp'] = start_time.isoformat()
            
            # Cache response
            if self.cache_enabled and response.get('status') == 'success':
                cache_key = self._get_cache_key('speak', provider, request_data)
                self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'error': str(e),
                'provider': provider.value,
                'response_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': start_time.isoformat()
            }
            raise AvatarApiError(f"Provider {provider.value} API call failed: {e}")
    
    async def _call_duix_speak(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call DUIX avatar API"""
        endpoint = self.endpoints.get('duix', 'https://api.duix.com/v1/avatar/speak')
        headers = {
            'Authorization': f"Bearer {self.api_keys.get('duix', '')}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'avatar_id': request_data['avatar_id'],
            'text': request_data['text'],
            'emotion': self._map_emotion_duix(request_data['emotion']),
            'language': request_data['language']
        }
        
        await self._ensure_session()
        
        async with self.session.post(endpoint, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'status': 'success',
                    'data': result,
                    'avatar_url': result.get('avatar_url'),
                    'audio_url': result.get('audio_url')
                }
            else:
                error_text = await response.text()
                raise AvatarApiError(f"DUIX API error {response.status}: {error_text}")
    
    async def _call_sense_avatar_speak(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call SenseAvatar API"""
        endpoint = self.endpoints.get('sense_avatar', 'https://api.senseavatar.com/v1/speak')
        headers = {
            'X-API-Key': self.api_keys.get('sense_avatar', ''),
            'Content-Type': 'application/json'
        }
        
        payload = {
            'avatar': request_data['avatar_id'],
            'text': request_data['text'],
            'emotion': self._map_emotion_sense_avatar(request_data['emotion']),
            'lang': request_data['language']
        }
        
        await self._ensure_session()
        
        async with self.session.post(endpoint, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'status': 'success',
                    'data': result,
                    'video_url': result.get('video_url'),
                    'task_id': result.get('task_id')
                }
            else:
                error_text = await response.text()
                raise AvatarApiError(f"SenseAvatar API error {response.status}: {error_text}")
    
    async def _call_akool_speak(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Akool avatar API"""
        endpoint = self.endpoints.get('akool', 'https://api.akool.com/v1/avatar/speak')
        headers = {
            'Authorization': f"Bearer {self.api_keys.get('akool', '')}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'avatar_id': request_data['avatar_id'],
            'input_text': request_data['text'],
            'emotion': self._map_emotion_akool(request_data['emotion']),
            'language': request_data['language']
        }
        
        await self._ensure_session()
        
        async with self.session.post(endpoint, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'status': 'success',
                    'data': result,
                    'video_id': result.get('video_id'),
                    'generation_id': result.get('generation_id')
                }
            else:
                error_text = await response.text()
                raise AvatarApiError(f"Akool API error {response.status}: {error_text}")
    
    async def _call_local_speak(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call local avatar service"""
        endpoint = self.endpoints.get('local', 'http://localhost:8000/speak')
        
        payload = {
            'text': request_data['text'],
            'emotion': request_data['emotion'],
            'language': request_data['language']
        }
        
        await self._ensure_session()
        
        try:
            async with self.session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'status': 'success',
                        'data': result,
                        'message': 'Local avatar service processed request'
                    }
                else:
                    error_text = await response.text()
                    raise AvatarApiError(f"Local service error {response.status}: {error_text}")
        except aiohttp.ClientConnectorError:
            raise AvatarApiError("Local avatar service not available")
    
    async def _call_mock_speak(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock avatar API for testing"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            'status': 'success',
            'data': {
                'text': request_data['text'],
                'emotion': request_data['emotion'],
                'language': request_data['language'],
                'avatar_id': request_data['avatar_id']
            },
            'message': 'Mock avatar service - request processed successfully',
            'mock_video_url': f"https://mock.avatar.com/video/{self.avatar_id}"
        }
    
    def _map_emotion_duix(self, emotion: str) -> str:
        """Map standard emotion to DUIX emotion format"""
        emotion_map = {
            'neutral': 'neutral',
            'happy': 'joy',
            'sad': 'sadness',
            'angry': 'anger',
            'surprised': 'surprise',
            'excited': 'excitement',
            'confused': 'confusion',
            'serious': 'serious',
            'analytical': 'thoughtful',
            'friendly': 'friendly',
            'playful': 'playful'
        }
        return emotion_map.get(emotion, 'neutral')
    
    def _map_emotion_sense_avatar(self, emotion: str) -> str:
        """Map standard emotion to SenseAvatar emotion format"""
        emotion_map = {
            'neutral': 'normal',
            'happy': 'happy',
            'sad': 'sad', 
            'angry': 'angry',
            'surprised': 'surprised',
            'excited': 'energetic',
            'serious': 'formal',
            'friendly': 'gentle'
        }
        return emotion_map.get(emotion, 'normal')
    
    def _map_emotion_akool(self, emotion: str) -> str:
        """Map standard emotion to Akool emotion format"""
        emotion_map = {
            'neutral': 'neutral',
            'happy': 'happy',
            'sad': 'sad',
            'excited': 'excited',
            'serious': 'professional',
            'friendly': 'warm'
        }
        return emotion_map.get(emotion, 'neutral')
    
    async def _check_rate_limit(self, provider: AvatarProvider):
        """Check and enforce rate limits"""
        provider_key = provider.value
        rate_limit = self.rate_limits.get(provider_key)
        
        if not rate_limit:
            return  # No rate limit configured
        
        requests_per_minute = rate_limit.get('requests_per_minute', 60)
        
        # Clean old requests
        now = datetime.now()
        if provider_key not in self.request_history:
            self.request_history[provider_key] = []
        
        self.request_history[provider_key] = [
            req_time for req_time in self.request_history[provider_key]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check if we're at the limit
        if len(self.request_history[provider_key]) >= requests_per_minute:
            sleep_time = 60 - (now - self.request_history[provider_key][0]).total_seconds()
            if sleep_time > 0:
                self.logger.warning(f"Rate limit hit for {provider_key}, sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
        
        # Record this request
        self.request_history[provider_key].append(now)
    
    async def _is_provider_healthy(self, provider: AvatarProvider) -> bool:
        """Check if provider is healthy"""
        health = self.provider_health[provider]
        
        # If we haven't checked recently, assume healthy
        if not health['last_check']:
            return True
        
        # If too many recent errors, consider unhealthy
        error_rate = health['error_count'] / max(1, health['success_count'] + health['error_count'])
        if error_rate > 0.5 and health['error_count'] > 3:
            return False
        
        return health['status'] != 'error'
    
    async def _update_provider_health(self, provider: AvatarProvider, 
                                    success: bool, response_time: float,
                                    error_msg: Optional[str] = None):
        """Update provider health status"""
        health = self.provider_health[provider]
        
        health['last_check'] = datetime.now().isoformat()
        health['response_time'] = response_time
        
        if success:
            health['success_count'] += 1
            health['status'] = 'healthy'
            health['last_error'] = None
        else:
            health['error_count'] += 1
            health['status'] = 'error'
            health['last_error'] = error_msg
    
    def _get_cache_key(self, operation: str, provider: AvatarProvider, 
                      request_data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        # Create a deterministic key from request data
        cache_data = {
            'operation': operation,
            'provider': provider.value,
            'avatar_id': self.avatar_id,
            'text': request_data.get('text', ''),
            'emotion': request_data.get('emotion', ''),
            'language': request_data.get('language', '')
        }
        return json.dumps(cache_data, sort_keys=True)
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache if valid"""
        if cache_key not in self.response_cache:
            return None
        
        cached_item = self.response_cache[cache_key]
        cache_time = datetime.fromisoformat(cached_item['cached_at'])
        
        if datetime.now() - cache_time > timedelta(seconds=self.cache_ttl):
            del self.response_cache[cache_key]
            return None
        
        return cached_item['response']
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response"""
        self.response_cache[cache_key] = {
            'response': response,
            'cached_at': datetime.now().isoformat()
        }
        
        # Simple cache size management
        if len(self.response_cache) > 1000:
            # Remove oldest 100 entries
            sorted_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]['cached_at']
            )
            for key in sorted_keys[:100]:
                del self.response_cache[key]
    
    async def health_check(self, provider: Optional[AvatarProvider] = None) -> Dict[str, Any]:
        """Perform health check on providers"""
        providers_to_check = [provider] if provider else [self.primary_provider] + self.fallback_providers
        
        health_results = {}
        
        for p in providers_to_check:
            try:
                # Simple health check - mock request
                test_data = {
                    'text': 'Health check',
                    'emotion': 'neutral',
                    'language': 'en',
                    'avatar_id': self.avatar_id
                }
                
                start_time = datetime.now()
                await self._call_provider_speak(p, test_data)
                response_time = (datetime.now() - start_time).total_seconds()
                
                health_results[p.value] = {
                    'status': 'healthy',
                    'response_time': response_time,
                    'timestamp': start_time.isoformat()
                }
                
            except Exception as e:
                health_results[p.value] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return health_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'avatar_id': self.avatar_id,
            'primary_provider': self.primary_provider.value,
            'fallback_providers': [p.value for p in self.fallback_providers],
            'provider_health': {
                p.value: health for p, health in self.provider_health.items()
            },
            'cache_size': len(self.response_cache),
            'request_history_size': sum(len(history) for history in self.request_history.values())
        }
    
    async def clear_cache(self):
        """Clear response cache"""
        cache_size = len(self.response_cache)
        self.response_cache.clear()
        self.logger.info(f"Cleared {cache_size} cached responses")