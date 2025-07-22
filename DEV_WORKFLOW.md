# Development Workflow & Environment Setup

## 🏗️ Current Status: Phase 1 Complete ✅

Phase 1 Infrastructure Setup is **COMPLETE**. All core platform components have been implemented and are ready for testing in an environment with MetaGPT.

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
├── setup_ubuntu.sh               # Ubuntu environment setup script
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

### Phase 2 Files (To Be Implemented) 🔲
```
agents/avatar/                     # Avatar Manufacturing Workshop
├── base_avatar_agent.py          # Core avatar agent
├── avatar_knowledge_base.py      # Knowledge management
├── avatar_personality.py         # Personality system
├── avatar_content_generator.py   # Content generation
└── avatar_api_client.py          # Avatar API communication

management/                        # Avatar management interface
├── avatar_config_manager.py      # Configuration UI
├── knowledge_injector.py         # Dynamic knowledge updates
└── avatar_monitor.py             # Performance monitoring
```

## 🧪 Testing Strategy

### Phase 1 Testing (Ready)
- **Infrastructure Tests**: `test_infrastructure.py`
  - Configuration management
  - Base agent functionality  
  - Platform manager initialization
  - Logging system
  - Directory structure validation

### Phase 2 Testing (To Create)
- **Avatar Workshop Tests**: `test_avatar_workshop.py`
- **Integration Tests**: Test with existing football example
- **API Communication Tests**: Test avatar provider integrations

## 🎯 Success Metrics

### Phase 1 Achievements ✅
- **14 files created** with ~1,500 lines of code
- **7 major components** implemented
- **3 integration points** (MetaGPT, n8n, MCP)
- **Modular architecture** with proper separation of concerns

### Phase 2 Targets 🎯
- **Avatar agents** that can be configured via API
- **Single-phrase to complete response** generation
- **Multi-provider avatar API** support
- **Dynamic knowledge base** integration

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
# Test infrastructure
python test_infrastructure.py

# Test current functionality
python test_commentary.py
python agents/football_commentary_team.py
```

### Development
```bash
# Run platform (when complete)
python main.py --mode full

# Run specific components
python main.py --mode avatar
python main.py --mode content
```

## 📋 Development Notes

### Key Implementation Details
1. **Configuration System**: Supports environment variables, validation, and hot-reloading
2. **Agent Framework**: Built on MetaGPT with enhanced base classes
3. **Event System**: Comprehensive event dispatching and workflow integration
4. **Modular Design**: Each component can be developed and tested independently

### Integration Points
- **MetaGPT**: Agent framework and team orchestration
- **n8n**: Workflow automation and external service integration
- **MCP**: Tool integration and external API management

---

**📖 For detailed progress and next steps, see [PROGRESS.md](./PROGRESS.md)**

**🐛 Issues? Check the Known Issues section in PROGRESS.md**