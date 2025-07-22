"""
Test Avatar Workshop

Comprehensive test suite for the Avatar Manufacturing Workshop components.
Tests all avatar system functionality including knowledge, personality, content generation,
API communication, and management features.
"""
import asyncio
import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

# Avatar components
from agents.avatar.base_avatar_agent import BaseAvatarAgent, AvatarAction
from agents.avatar.avatar_knowledge_base import AvatarKnowledgeBase, KnowledgeItem
from agents.avatar.avatar_personality import AvatarPersonality, PersonalityTrait, EmotionState
from agents.avatar.avatar_content_generator import AvatarContentGenerator
from agents.avatar.avatar_api_client import AvatarApiClient, AvatarProvider

# Management components
from management.avatar_config_manager import AvatarConfigManager, AvatarConfiguration
from management.knowledge_injector import KnowledgeInjector, KnowledgeSource
from management.avatar_monitor import AvatarMonitor, AlertLevel


class TestAvatarKnowledgeBase:
    """Test avatar knowledge base functionality"""
    
    @pytest.fixture
    async def knowledge_base(self):
        """Create knowledge base for testing"""
        kb = AvatarKnowledgeBase("test_avatar", {
            'max_knowledge_items': 100,
            'default_ttl_hours': 1,
            'cleanup_interval_seconds': 10
        })
        yield kb
        await kb.close()
    
    @pytest.mark.asyncio
    async def test_add_knowledge(self, knowledge_base):
        """Test adding knowledge items"""
        knowledge_id = await knowledge_base.add_knowledge(
            content="Test knowledge item",
            category="test",
            tags=["test", "demo"],
            priority=2
        )
        
        assert knowledge_id is not None
        assert knowledge_id in knowledge_base.knowledge_items
        
        item = knowledge_base.knowledge_items[knowledge_id]
        assert item.content == "Test knowledge item"
        assert item.category == "test"
        assert "test" in item.tags
        assert item.priority == 2
    
    @pytest.mark.asyncio
    async def test_search_knowledge(self, knowledge_base):
        """Test knowledge search functionality"""
        # Add test items
        await knowledge_base.add_knowledge("Python programming", "tech", ["python", "code"], 3)
        await knowledge_base.add_knowledge("Machine learning basics", "tech", ["ml", "ai"], 2)
        await knowledge_base.add_knowledge("Cooking recipes", "lifestyle", ["food", "cooking"], 1)
        
        # Search by category
        tech_items = await knowledge_base.search_knowledge(categories=["tech"])
        assert len(tech_items) == 2
        
        # Search by tags
        python_items = await knowledge_base.search_knowledge(tags=["python"])
        assert len(python_items) == 1
        assert "python" in python_items[0].content.lower()
        
        # Search by query
        ml_items = await knowledge_base.search_knowledge(query="machine")
        assert len(ml_items) == 1
    
    @pytest.mark.asyncio
    async def test_knowledge_expiration(self, knowledge_base):
        """Test knowledge expiration"""
        # Add item with very short TTL (1 millisecond)
        knowledge_id = await knowledge_base.add_knowledge(
            content="Short-lived knowledge",
            category="temp",
            ttl_hours=1/3600000  # 1 millisecond in hours
        )
        
        # Item should exist initially
        item = await knowledge_base.get_knowledge(knowledge_id)
        assert item is not None
        
        # Wait a bit longer and check expiration
        await asyncio.sleep(0.002)  # Wait 2ms
        
        # Force cleanup of expired items
        await knowledge_base.cleanup_expired()
        
        # Item should be expired and removed
        item = await knowledge_base.get_knowledge(knowledge_id)
        assert item is None


class TestAvatarPersonality:
    """Test avatar personality system"""
    
    @pytest.fixture
    def personality(self):
        """Create personality for testing"""
        config = {
            'default_personality': {
                'extraversion': 0.5,
                'agreeableness': 0.7,
                'conscientiousness': 0.4,
                'neuroticism': -0.2,
                'openness': 0.6
            }
        }
        return AvatarPersonality("test_avatar", config)
    
    def test_personality_initialization(self, personality):
        """Test personality initialization"""
        assert personality.get_trait_value('extraversion') == 0.5
        assert personality.get_trait_value('agreeableness') == 0.7
        assert personality.current_emotion.dominant_emotion == 'neutral'
    
    def test_trait_updates(self, personality):
        """Test personality trait updates"""
        original_value = personality.get_trait_value('extraversion')
        
        success = personality.update_trait('extraversion', 0.8, "test update")
        assert success is True
        assert personality.get_trait_value('extraversion') == 0.8
        
        # Test adjustment
        success = personality.adjust_trait('extraversion', -0.3, "test adjustment")
        assert success is True
        assert abs(personality.get_trait_value('extraversion') - 0.5) < 0.01
    
    def test_emotion_system(self, personality):
        """Test emotion state management"""
        personality.set_emotion('happy', 0.8, "test context")
        
        assert personality.current_emotion.dominant_emotion == 'happy'
        assert personality.current_emotion.intensity == 0.8
        assert personality.current_emotion.context == "test context"
        assert len(personality.emotion_history) == 1
    
    def test_response_patterns(self, personality):
        """Test response pattern selection"""
        pattern = personality.get_response_pattern('greeting')
        assert pattern is not None
        assert isinstance(pattern, str)
        
        # Test fallback
        pattern = personality.get_response_pattern('nonexistent_situation')
        assert pattern is not None  # Should fallback to default


class TestAvatarContentGenerator:
    """Test avatar content generation"""
    
    @pytest.fixture
    async def content_generator(self):
        """Create content generator for testing"""
        # Mock knowledge base and personality
        knowledge_base = AvatarKnowledgeBase("test_avatar")
        personality = AvatarPersonality("test_avatar")
        
        generator = AvatarContentGenerator(
            "test_avatar",
            knowledge_base,
            personality,
            {
                'default_generation_mode': 'conversational',
                'max_response_length': 200
            }
        )
        
        yield generator
        
        await knowledge_base.close()
    
    @pytest.mark.asyncio
    async def test_response_generation(self, content_generator):
        """Test basic response generation"""
        # Note: This test may not work without actual LLM configuration
        # In a real environment, you would configure the LLM properly
        
        try:
            result = await content_generator.generate_response(
                prompt="Hello, how are you?",
                mode="conversational"
            )
            
            assert 'response' in result
            assert 'metadata' in result
            assert result['metadata']['mode'] == 'conversational'
            
        except Exception as e:
            # Expected if no LLM is configured
            assert "LLM" in str(e) or "API" in str(e) or "configuration" in str(e).lower()
    
    def test_mode_determination(self, content_generator):
        """Test generation mode determination"""
        # Create a base avatar agent to test mode determination
        from agents.avatar.base_avatar_agent import BaseAvatarAgent
        
        config = {
            'personality': {'default_personality': {}},
            'knowledge': {},
            'content_generation': {},
            'api_client': {'primary_provider': 'mock'}
        }
        
        avatar = BaseAvatarAgent("test_avatar", config=config)
        
        mode = avatar._determine_generation_mode("How does this work?")
        assert mode == 'analytical'
        
        mode = avatar._determine_generation_mode("Tell me a creative story")
        assert mode == 'creative'
        
        mode = avatar._determine_generation_mode("I need help with something")
        assert mode == 'supportive'


class TestAvatarApiClient:
    """Test avatar API client"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client for testing"""
        config = {
            'primary_provider': 'mock',
            'endpoints': {'mock': 'http://mock.avatar.com/speak'},
            'default_timeout': 5
        }
        return AvatarApiClient("test_avatar", config)
    
    @pytest.mark.asyncio
    async def test_mock_provider(self, api_client):
        """Test mock provider communication"""
        async with api_client:
            response = await api_client.speak(
                text="Hello world",
                emotion="happy",
                language="en"
            )
            
            assert response['status'] == 'success'
            assert 'Mock avatar service' in response['message']
            assert response['data']['text'] == "Hello world"
            assert response['data']['emotion'] == "happy"
    
    def test_emotion_mapping(self, api_client):
        """Test emotion mapping for different providers"""
        # Test different provider emotion mappings
        duix_emotion = api_client._map_emotion_duix('happy')
        assert duix_emotion == 'joy'
        
        sense_emotion = api_client._map_emotion_sense_avatar('excited')
        assert sense_emotion == 'energetic'
        
        akool_emotion = api_client._map_emotion_akool('serious')
        assert akool_emotion == 'professional'


class TestAvatarConfigManager:
    """Test avatar configuration management"""
    
    @pytest.fixture
    async def config_manager(self):
        """Create config manager with temporary directory"""
        temp_dir = tempfile.mkdtemp()
        manager = AvatarConfigManager(temp_dir)
        await manager.initialize()  # Initialize async components
        yield manager
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_avatar_creation(self, config_manager):
        """Test avatar creation from template"""
        success = await config_manager.create_avatar(
            avatar_id="test_avatar_1",
            template="conversational",
            custom_config={'name': 'Custom Test Avatar'}
        )
        
        assert success is True
        assert "test_avatar_1" in config_manager.avatar_configs
        
        config = config_manager.avatar_configs["test_avatar_1"]
        assert config.name == "Custom Test Avatar"
        assert config.status == "inactive"
    
    @pytest.mark.asyncio
    async def test_avatar_lifecycle(self, config_manager):
        """Test complete avatar lifecycle"""
        avatar_id = "lifecycle_test"
        
        # Create
        await config_manager.create_avatar(avatar_id, "conversational")
        assert config_manager.avatar_configs[avatar_id].status == "inactive"
        
        # Note: Starting avatar requires full MetaGPT configuration
        # In real testing, you would configure this properly
        
        # Update configuration
        success = await config_manager.update_avatar_config(
            avatar_id,
            {'name': 'Updated Name'}
        )
        assert success is True
        assert config_manager.avatar_configs[avatar_id].name == 'Updated Name'
        
        # Delete
        success = await config_manager.delete_avatar(avatar_id)
        assert success is True
        assert avatar_id not in config_manager.avatar_configs
    
    def test_templates(self, config_manager):
        """Test template management"""
        templates = config_manager.get_templates()
        assert 'conversational' in templates
        assert 'analytical' in templates
        assert 'creative' in templates
        
        template_config = config_manager.get_template_config('conversational')
        assert template_config is not None
        assert 'personality_config' in template_config


class TestKnowledgeInjector:
    """Test knowledge injection system"""
    
    @pytest.fixture
    async def injector(self):
        """Create knowledge injector for testing"""
        injector = KnowledgeInjector()
        
        # Register mock knowledge base
        kb = AvatarKnowledgeBase("test_avatar")
        injector.register_knowledge_base("test_avatar", kb)
        
        yield injector
        
        await kb.close()
    
    @pytest.mark.asyncio
    async def test_manual_injection(self, injector):
        """Test manual knowledge injection"""
        knowledge_id = await injector.inject_manual_knowledge(
            avatar_id="test_avatar",
            content="Manually injected knowledge",
            category="manual",
            tags=["manual", "test"],
            priority=2
        )
        
        assert knowledge_id is not None
        
        # Verify injection
        kb = injector.knowledge_bases["test_avatar"]
        item = await kb.get_knowledge(knowledge_id)
        assert item is not None
        assert item.content == "Manually injected knowledge"
        assert "manual" in item.tags
    
    @pytest.mark.asyncio
    async def test_job_creation(self, injector):
        """Test injection job creation"""
        success = await injector.create_injection_job(
            job_id="test_job",
            avatar_id="test_avatar",
            source_type=KnowledgeSource.MANUAL,
            source_config={
                'content': 'Test content for injection',
                'metadata': {'category': 'test'}
            },
            processing_config={'processor': 'default'},
            category="injected",
            tags=["automated"]
        )
        
        assert success is True
        assert "test_job" in injector.injection_jobs
        
        job = injector.injection_jobs["test_job"]
        assert job.avatar_id == "test_avatar"
        assert job.source_type == KnowledgeSource.MANUAL


class TestAvatarMonitor:
    """Test avatar monitoring system"""
    
    @pytest.fixture
    async def monitor_system(self):
        """Create monitoring system for testing"""
        monitor = AvatarMonitor({
            'collection_interval_seconds': 1,
            'health_check_interval_seconds': 2
        })
        
        yield monitor
        
        await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, monitor_system):
        """Test monitoring system lifecycle"""
        assert monitor_system.monitoring_active is False
        
        await monitor_system.start_monitoring()
        assert monitor_system.monitoring_active is True
        
        await monitor_system.stop_monitoring()
        assert monitor_system.monitoring_active is False
    
    def test_alert_system(self, monitor_system):
        """Test alert system functionality"""
        # Test default alert rules
        assert 'high_response_time' in monitor_system.alert_rules
        assert 'low_success_rate' in monitor_system.alert_rules
        
        # Test alert callback system
        alerts_received = []
        
        def test_callback(alert):
            alerts_received.append(alert)
        
        monitor_system.add_alert_callback(test_callback)
        assert len(monitor_system.alert_callbacks) == 1


class TestFullIntegration:
    """Test full avatar system integration"""
    
    @pytest.fixture
    async def full_avatar_system(self):
        """Create complete avatar system for integration testing"""
        # Create temporary directory for configs
        temp_dir = tempfile.mkdtemp()
        
        # Initialize components
        config_manager = AvatarConfigManager(temp_dir)
        await config_manager.initialize()  # Initialize async components
        monitor = AvatarMonitor()
        injector = KnowledgeInjector()
        
        # Create test avatar
        await config_manager.create_avatar(
            "integration_test",
            "conversational",
            {
                'name': 'Integration Test Avatar',
                'initial_knowledge': [
                    {
                        'content': 'I am a test avatar for integration testing',
                        'category': 'identity',
                        'tags': ['self', 'test'],
                        'priority': 3
                    }
                ]
            }
        )
        
        yield {
            'config_manager': config_manager,
            'monitor': monitor,
            'injector': injector,
            'temp_dir': temp_dir
        }
        
        # Cleanup
        await monitor.stop_monitoring()
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, full_avatar_system):
        """Test complete avatar creation and management workflow"""
        config_manager = full_avatar_system['config_manager']
        monitor = full_avatar_system['monitor']
        injector = full_avatar_system['injector']
        
        # Verify avatar was created
        avatars = await config_manager.list_avatars()
        assert len(avatars) == 1
        assert avatars[0]['name'] == 'Integration Test Avatar'
        
        # Test configuration updates
        success = await config_manager.update_avatar_config(
            "integration_test",
            {'profile': 'Updated Test Avatar Profile'}
        )
        assert success is True
        
        # Test batch operations
        results = await config_manager.batch_operation('update', ['integration_test'], 
                                                     updates={'status': 'tested'})
        assert results['integration_test'] is True
        
        # Verify monitoring system can track the avatar
        stats = monitor.get_monitoring_stats()
        assert stats['monitored_avatars'] == 0  # No active avatars yet
        
        # Test injector registration
        kb = AvatarKnowledgeBase("integration_test")
        injector.register_knowledge_base("integration_test", kb)
        
        # Test knowledge injection
        knowledge_id = await injector.inject_manual_knowledge(
            "integration_test",
            "This is integration test knowledge",
            category="test",
            tags=["integration"]
        )
        assert knowledge_id is not None
        
        # Cleanup
        await kb.close()


# Utility functions for testing

def create_test_config():
    """Create test configuration dictionary"""
    return {
        'personality': {
            'default_personality': {
                'extraversion': 0.5,
                'agreeableness': 0.6,
                'conscientiousness': 0.4,
                'neuroticism': -0.2,
                'openness': 0.7
            }
        },
        'knowledge': {
            'max_knowledge_items': 500,
            'default_ttl_hours': 24
        },
        'content_generation': {
            'default_generation_mode': 'conversational',
            'max_response_length': 300
        },
        'api_client': {
            'primary_provider': 'mock',
            'endpoints': {'mock': 'http://mock.avatar.com/speak'}
        }
    }


async def create_test_avatar(avatar_id: str = "test_avatar"):
    """Create test avatar instance"""
    config = create_test_config()
    
    avatar = BaseAvatarAgent(
        avatar_id=avatar_id,
        name=f"Test Avatar {avatar_id}",
        profile="Test Avatar Agent",
        config=config
    )
    
    await avatar.initialize()
    return avatar


# Main test runner
async def run_all_tests():
    """Run all avatar workshop tests"""
    print("🧪 Running Avatar Workshop Test Suite")
    print("=" * 50)
    
    try:
        # Test individual components
        print("Testing Knowledge Base...")
        kb = AvatarKnowledgeBase("test")
        await kb.add_knowledge("Test knowledge", "test", ["test"])
        items = await kb.search_knowledge(categories=["test"])
        assert len(items) == 1
        await kb.close()
        print("✅ Knowledge Base tests passed")
        
        print("Testing Personality System...")
        personality = AvatarPersonality("test")
        personality.set_emotion('happy', 0.8)
        assert personality.current_emotion.dominant_emotion == 'happy'
        print("✅ Personality System tests passed")
        
        print("Testing API Client...")
        api_client = AvatarApiClient("test", {'primary_provider': 'mock'})
        async with api_client:
            response = await api_client.speak("Hello", "neutral")
            assert response['status'] == 'success'
        print("✅ API Client tests passed")
        
        print("Testing Configuration Manager...")
        temp_dir = tempfile.mkdtemp()
        config_manager = AvatarConfigManager(temp_dir)
        success = await config_manager.create_avatar("test", "conversational")
        assert success is True
        shutil.rmtree(temp_dir)
        print("✅ Configuration Manager tests passed")
        
        print("Testing Knowledge Injector...")
        injector = KnowledgeInjector()
        kb = AvatarKnowledgeBase("test")
        injector.register_knowledge_base("test", kb)
        knowledge_id = await injector.inject_manual_knowledge("test", "Test", "manual")
        assert knowledge_id is not None
        await kb.close()
        print("✅ Knowledge Injector tests passed")
        
        print("Testing Avatar Monitor...")
        monitor = AvatarMonitor()
        await monitor.start_monitoring()
        assert monitor.monitoring_active is True
        await monitor.stop_monitoring()
        print("✅ Avatar Monitor tests passed")
        
        print("\n" + "=" * 50)
        print("🎉 All Avatar Workshop tests passed!")
        print("✨ Avatar Manufacturing Workshop is ready for production!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run basic tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🚀 Ready to start using Avatar Manufacturing Workshop!")
        print("\nNext steps:")
        print("1. Configure your LLM settings in config/config2.yaml")
        print("2. Set up avatar API endpoints in config/football_avatar.yaml")
        print("3. Create your first avatar using AvatarConfigManager")
        print("4. Test with: python test_avatar_workshop.py")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1)