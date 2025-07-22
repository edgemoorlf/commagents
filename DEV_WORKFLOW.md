# Development Workflow & Environment Setup

## 🏗️ Current Status: Phase 2 Complete (Avatar Manufacturing Workshop) ✅

**Phase 2: Avatar Manufacturing Workshop** is **COMPLETE**. All avatar system components have been implemented, tested, and are ready for production use.

## 🔧 Environment Setup Options

### Option 1: Using pip (Recommended)
```bash
# Clone and enter directory
git clone <repository-url>
cd ai-avatar-platform

# Install with development dependencies
pip install -e ".[dev]"

# Or install from requirements.txt
pip install -r requirements.txt
```

### Option 2: Using conda/mamba
```bash
# Create environment from environment.yml
conda env create -f environment.yml
conda activate ai-avatar-platform

# Or manually create environment
conda create -n ai-avatar-platform python=3.10
conda activate ai-avatar-platform
pip install -e ".[dev]"
```

### Option 3: Quick setup script
```bash
# Run setup script (creates dirs, installs deps, copies config)
./setup.sh
```

## 📦 Dependency Management

### Core Dependencies
- **metagpt**: Multi-agent framework
- **aiohttp**: Async HTTP client/server
- **pyyaml**: YAML configuration parsing
- **asyncio-mqtt**: MQTT async support

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **black**: Code formatter
- **flake8**: Linting
- **mypy**: Type checking

### Configuration Files
- `requirements.txt`: Basic pip dependencies
- `pyproject.toml`: Modern Python project configuration
- `environment.yml`: Complete conda environment specification

## 📁 File Structure Overview

### Phase 1 Files (Completed) ✅
```
commagents/
├── main.py                        # Platform entry point
├── PROGRESS.md                    # Development progress tracking  
├── test_infrastructure.py        # Infrastructure testing suite
├── core/                          # Core platform components
│   ├── platform_manager.py      # Central orchestrator
│   ├── config_manager.py         # Configuration management
│   └── base_agent.py             # Base agent framework
├── workflows/                     # n8n integration
│   ├── n8n_client.py            # n8n API client
│   ├── workflow_manager.py       # Workflow orchestration  
│   └── event_dispatcher.py       # Event routing
├── tools/                         # External integrations
│   └── mcp_client.py             # MCP protocol client
└── utils/                         # Utilities
    └── logger.py                 # Logging system
```

### Phase 2 Files (Completed) ✅
```
agents/avatar/                     # Avatar Manufacturing Workshop ✅
├── __init__.py                   # Avatar package initialization ✅
├── base_avatar_agent.py          # Core avatar agent with full integration ✅
├── avatar_knowledge_base.py      # Advanced knowledge management system ✅
├── avatar_personality.py         # Comprehensive personality & emotion system ✅
├── avatar_content_generator.py   # Multi-mode content generation ✅
└── avatar_api_client.py          # Multi-provider avatar API client ✅

management/                        # Avatar management interface ✅
├── __init__.py                   # Management package initialization ✅
├── avatar_config_manager.py      # Avatar lifecycle & configuration management ✅
├── knowledge_injector.py         # Dynamic knowledge injection system ✅
└── avatar_monitor.py             # Performance monitoring & analytics ✅

examples/                          # Example implementations ✅
└── football_commentary/          # Football commentary example ✅
    ├── __init__.py               # Package initialization ✅
    ├── football_commentary_team.py # Team orchestration ✅
    ├── playbyplay_commentator.py   # Play-by-play agent ✅
    ├── tactical_analyst.py         # Tactical analysis agent ✅
    ├── show_host.py                # Show host agent ✅
    ├── test_commentary.py          # Example tests ✅
    └── README.md                   # Example documentation ✅

test_avatar_workshop.py            # Comprehensive avatar system tests ✅
```

### Phase 3 Files (To Be Implemented) 🔲
```
agents/content/                    # Content Factory
├── content_import_agent.py       # Multi-source content acquisition
├── content_generation_agent.py   # Advanced content generation
├── web_surfer_agent.py           # Web content discovery
├── api_integration_agent.py      # API content import
└── video_production_agent.py     # Video creation pipeline

test_content_factory.py           # Content factory tests
```

## 🧪 Testing Strategy

### Phase 1 Infrastructure Tests ✅
- **Infrastructure Tests**: `test_infrastructure.py` ✅
  - Configuration management ✅
  - Base agent functionality ✅  
  - Platform manager initialization ✅
  - Logging system ✅
  - Directory structure validation ✅

### Phase 2 Avatar Workshop Tests ✅
- **Avatar Workshop Tests**: `test_avatar_workshop.py` ✅
  - Knowledge base operations ✅
  - Personality system functionality ✅
  - Content generation pipeline ✅
  - API client communication ✅
  - Configuration management ✅
  - Knowledge injection system ✅
  - Performance monitoring ✅
  - Full integration workflow ✅

### Phase 3 Content Factory Tests 🔲 (Upcoming)
- **Content Factory Tests**: `test_content_factory.py`
- **Content import from multiple sources**
- **Content generation and transformation**
- **Video production pipeline**
- **Integration with avatar system**

## 🎯 Success Metrics

### Phase 1 Achievements ✅
- **14 files created** with ~1,500 lines of code
- **7 major components** implemented
- **3 integration points** (MetaGPT, n8n, MCP)
- **Modular architecture** with proper separation of concerns

### Phase 2 Achievements ✅
- **12 additional files created** with ~3,500 lines of code
- **11 major avatar components** implemented
- **Complete avatar system** from knowledge to API communication
- **Comprehensive test suite** with 100% component coverage
- **Production-ready** avatar manufacturing capabilities

### Phase 3 Targets 🎯 (Upcoming)
- **Content factory** with multi-source import capabilities
- **Automated content generation** with quality filtering
- **Video production pipeline** integration
- **Complete content-to-avatar workflow**

## 🚀 Quick Commands Reference

### Environment Setup
```bash
# Ubuntu setup
./setup_ubuntu.sh

# Manual activation
conda activate m2
```

### Testing
```bash
# Test infrastructure (Phase 1)
python test_infrastructure.py

# Test avatar workshop (Phase 2)
python test_avatar_workshop.py

# Test current functionality with examples
python examples/football_commentary/test_commentary.py
python examples/football_commentary/football_commentary_team.py
```

### Avatar Workshop Usage (Phase 2)
```bash
# Create and manage avatars
python -c "
import asyncio
from management.avatar_config_manager import AvatarConfigManager

async def demo():
    manager = AvatarConfigManager()
    await manager.create_avatar('demo_avatar', 'conversational')
    print('Avatar created successfully!')

asyncio.run(demo())
"

# Test avatar components individually
python -c "
import asyncio
from agents.avatar.avatar_knowledge_base import AvatarKnowledgeBase

async def test_kb():
    kb = AvatarKnowledgeBase('test')
    kid = await kb.add_knowledge('Test knowledge', 'demo', ['test'])
    items = await kb.search_knowledge(categories=['demo'])
    print(f'Added knowledge: {len(items)} items found')
    await kb.close()

asyncio.run(test_kb())
"
```

### Development
```bash
# Run platform (when complete)
python main.py --mode full

# Run specific components
python main.py --mode avatar    # Avatar workshop only
python main.py --mode content   # Content factory (Phase 3)
```

## 📋 Development Notes

### Key Implementation Details
1. **Configuration System**: Supports environment variables, validation, and hot-reloading
2. **Agent Framework**: Built on MetaGPT with enhanced base classes
3. **Event System**: Comprehensive event dispatching and workflow integration
4. **Modular Design**: Each component can be developed and tested independently
5. **Avatar System**: Complete lifecycle from creation to content generation to API communication

### Avatar Workshop Components
- **BaseAvatarAgent**: Central orchestrator integrating all avatar components
- **AvatarKnowledgeBase**: Advanced knowledge storage with expiration, categorization, and context-aware retrieval
- **AvatarPersonality**: Big Five traits, dynamic emotions, and personality evolution
- **AvatarContentGenerator**: Multi-mode content generation with personality integration
- **AvatarApiClient**: Multi-provider API client with failover and health monitoring
- **Management Interface**: Complete avatar lifecycle management, monitoring, and knowledge injection

### Integration Points
- **MetaGPT**: Agent framework and team orchestration
- **n8n**: Workflow automation and external service integration
- **MCP**: Tool integration and external API management

### Usage Examples

#### Create and Use an Avatar
```python
from management.avatar_config_manager import AvatarConfigManager
from agents.avatar.base_avatar_agent import BaseAvatarAgent

# Create avatar configuration
manager = AvatarConfigManager()
await manager.create_avatar("my_assistant", "conversational", {
    'name': 'My Personal Assistant',
    'initial_knowledge': [{
        'content': 'I am a helpful personal assistant',
        'category': 'identity',
        'tags': ['helpful', 'assistant']
    }]
})

# Start avatar
await manager.start_avatar("my_assistant")
avatar = await manager.get_avatar("my_assistant")

# Generate response
response = await avatar.generate_response(
    "What can you help me with?",
    mode="conversational"
)
print(response['response'])
```

#### Dynamic Knowledge Management
```python
from agents.avatar.avatar_knowledge_base import AvatarKnowledgeBase

kb = AvatarKnowledgeBase("my_avatar")

# Add knowledge with different priorities and expiration
await kb.add_knowledge(
    "Today's weather is sunny and 72°F",
    category="weather",
    tags=["today", "weather"],
    priority=2,
    ttl_hours=6  # Expires in 6 hours
)

# Search contextually
weather_info = await kb.search_knowledge(
    query="weather",
    min_priority=2,
    limit=5
)
```

#### Monitor Avatar Performance
```python
from management.avatar_monitor import AvatarMonitor

monitor = AvatarMonitor()
await monitor.start_monitoring()

# Register avatar for monitoring
monitor.register_avatar(my_avatar)

# Get health report
report = await monitor.generate_health_report("my_avatar")
print(f"Avatar health score: {report['avatars']['my_avatar']['health_score']}")
```

---

**📖 For detailed progress and next steps, see [PROGRESS.md](./PROGRESS.md)**

**🐛 Issues? Check the Known Issues section in PROGRESS.md**