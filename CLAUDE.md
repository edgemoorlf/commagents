# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Avatar Platform (commagents)** - A comprehensive AI-powered avatar platform that creates, manages, and operates digital avatars for content generation and live streaming. The platform consists of four main components: Avatar Manufacturing Workshop, Content Factory, Ecosystem Integration, and Data Analytics.

**LiveFootballAvatar** serves as the initial example implementation demonstrating the platform's capabilities through real-time football commentary generation.

## Platform Architecture

### 1. Avatar Manufacturing Workshop (数字人制造车间)

#### Live Avatar Agent
- **Knowledge Base Management**: Stores and injects knowledge for avatar personalities
- **General Knowledge Integration**: Dynamic knowledge updates and context awareness

#### Universal Avatar Assembly
- **Backend Management**: Administrative interface for avatar configuration
- **Avatar Customization**: Personality, voice, appearance, and behavior settings

#### Avatar Content Generation
- **One-Phrase Generation**: Generate complete avatar responses from simple prompts
- **LLM-Powered**: Uses configured language models for natural content creation

#### Avatar Task Orchestration
- **n8n Workflow Integration**: Automates avatar tasks and responses
- **Event-Driven Actions**: Triggers based on external events and schedules

### 2. Content Factory (内容工厂)

#### Content Import Agent
- **API Integration**: Imports content via REST APIs and MCP protocols
- **Web Tools**: WebSurfer and WebCrawler for content acquisition
- **Agent-Based**: Autonomous content discovery and import

#### Content Generation Agent
- **Multi-Source Generation**:
  1. Single-phrase prompts
  2. Content reprocessing and micro-innovation
  3. IP-style content transformation
- **Tool-Enhanced**: Uses LLM + external tools + n8n workflows

#### Video Production Pipeline Agent
- **End-to-End Video Creation**: From script to final video
- **n8n Workflow Integration**: Automated production pipeline
- **Tool Integration**: External video processing tools

### 3. Ecosystem Integration (生态平台接入)

#### Publishing Pipeline Agent
- **Multi-Platform Publishing**: Automated content distribution
- **n8n Workflow**: Orchestrates publishing across platforms
- **WebSurfer Integration**: Platform-specific publishing logic

### 4. Data Analytics (数据分析)
- **Live Avatar Metrics**: Performance tracking and analytics
- **User Engagement**: Interaction and response analytics
- **Content Performance**: Success metrics and optimization insights

## Current Implementation (LiveFootballAvatar Example)

### Core Architecture

- **MetaGPT-based Multi-Agent System**: Uses MetaGPT's Team framework with specialized Role and Action classes
- **Event-Driven Commentary**: Match events are routed to appropriate agents based on event type prefixes
- **Avatar Integration**: Generated commentary is sent to avatar APIs with emotion mappings
- **n8n Workflow Integration**: Triggers external workflows for avatar control and messaging

## Agent Roles

### PlayByPlayCommentator (`agents/playbyplay_commentator.py`)
- Handles general match events (goals, saves, penalties)
- Generates vivid, energetic 1-2 sentence narrations
- Default recipient for events without specific prefixes

### TacticalAnalyst (`agents/tactical_analyst.py`) 
- Processes events prefixed with "TACTICAL:"
- Provides 2-3 sentence strategic analysis of formations and plays
- Focuses on tactical explanations

### ShowHost (`agents/show_host.py`)
- Handles events prefixed with "TRANSITION:"
- Moderates discussion flow between other commentators
- Provides smooth transitions and summaries

## Key Components

### FootballCommentaryTeam (`agents/football_commentary_team.py`)
Main orchestrator class that:
- Initializes MetaGPT Team with all three agents
- Routes events to appropriate agents based on prefixes
- Manages the commentary generation workflow

### Event Routing Logic
```python
send_to = "PlayByPlayCommentator"  # default
if event.startswith('TACTICAL:'):
    send_to = "TacticalAnalyst"
elif event.startswith('TRANSITION:'):
    send_to = "ShowHost"
```

## Configuration

### Main Config (`config/config2.example.yaml`)
Standard MetaGPT configuration covering:
- LLM settings (OpenAI/Azure/etc.)
- Role-specific LLM configurations
- Embedding, search, browser automation settings
- TTS integration (Azure, iFlytek)

### Football Avatar Config (`config/football_avatar.yaml`)
Project-specific settings:
- Avatar API endpoint configuration
- Emotion mappings for different event types
- n8n webhook URLs and event types
- MCP server settings

## Implementation Plan

### Phase 1: Core Platform Foundation
**Timeline: Weeks 1-4**

#### Infrastructure Setup
- [ ] Create base platform structure with MetaGPT framework
- [ ] Implement core Agent base classes and framework patterns
- [ ] Set up configuration management system
- [ ] Establish n8n workflow integration foundation
- [ ] Create MCP server integration layer

#### Avatar Manufacturing Workshop - Foundation
- [ ] Implement `LiveAvatarAgent` base class with knowledge management
- [ ] Create avatar configuration system
- [ ] Build basic content generation from single phrases
- [ ] Implement avatar-to-API communication layer

### Phase 2: Content Factory Development
**Timeline: Weeks 5-8**

#### Content Agents
- [ ] Implement `ContentImportAgent` with API/MCP integration
- [ ] Build `ContentGenerationAgent` with multi-source capabilities
- [ ] Create WebSurfer and WebCrawler tool integrations
- [ ] Develop content transformation and IP-style generation

#### Pipeline Integration
- [ ] Establish content flow between import → generation → avatar
- [ ] Implement content quality and filtering mechanisms
- [ ] Create content versioning and management system

### Phase 3: Advanced Features
**Timeline: Weeks 9-12**

#### Video Production Pipeline
- [ ] Implement `VideoProductionAgent` base structure
- [ ] Integrate external video processing tools
- [ ] Create automated video generation workflows
- [ ] Build quality control and optimization systems

#### Publishing & Analytics
- [ ] Develop `PublishingPipelineAgent` for multi-platform distribution
- [ ] Implement data collection and analytics system
- [ ] Create performance monitoring and optimization tools
- [ ] Build user engagement tracking

### Phase 4: Platform Maturation
**Timeline: Weeks 13-16**

#### Advanced Avatar Features
- [ ] Implement advanced personality and behavior systems
- [ ] Create real-time learning and adaptation capabilities
- [ ] Build multi-avatar coordination and interaction
- [ ] Develop advanced emotion and context awareness

#### Ecosystem Integration
- [ ] Complete platform API development
- [ ] Implement advanced workflow orchestration
- [ ] Create developer tools and documentation
- [ ] Build monitoring and deployment automation

## Implementation Tasks by Component

### Avatar Manufacturing Workshop Tasks

#### Core Avatar System
```
agents/avatar/
├── base_avatar_agent.py          # Base avatar class with knowledge management
├── avatar_personality.py         # Personality and behavior configuration
├── avatar_knowledge_base.py      # Knowledge storage and retrieval
├── avatar_content_generator.py   # Single-phrase to full content generation
└── avatar_api_client.py          # Avatar API communication layer
```

#### Management Interface
```
management/
├── avatar_config_manager.py      # Avatar configuration and assembly
├── knowledge_injector.py         # Dynamic knowledge updates
└── avatar_monitor.py             # Avatar performance monitoring
```

### Content Factory Tasks

#### Import and Generation Agents
```
agents/content/
├── content_import_agent.py       # API/MCP content import
├── content_generation_agent.py   # Multi-source content generation
├── web_surfer_agent.py           # Web content acquisition
└── content_transformer.py       # IP-style transformation
```

#### Tools Integration
```
tools/
├── mcp_client.py                 # MCP protocol implementation
├── web_crawler.py                # Web crawling capabilities
├── content_processor.py          # Content analysis and processing
└── quality_filter.py             # Content quality assessment
```

### Video Production Tasks
```
agents/video/
├── video_production_agent.py     # End-to-end video creation
├── script_generator.py           # Video script creation
├── video_processor.py            # External tool integration
└── production_pipeline.py        # Automated video workflow
```

### Platform Integration Tasks

#### Workflow Orchestration
```
workflows/
├── n8n_client.py                 # n8n integration client
├── workflow_manager.py           # Workflow execution management
├── event_dispatcher.py           # Event routing and handling
└── task_scheduler.py             # Automated task scheduling
```

#### Data and Analytics
```
analytics/
├── metrics_collector.py          # Data collection system
├── performance_analyzer.py       # Performance metrics analysis
├── user_engagement_tracker.py    # Engagement analytics
└── optimization_engine.py        # Performance optimization
```

## Development Commands

### Platform Development
```bash
# Run the full platform (when implemented)
python main.py

# Run specific components
python agents/avatar/base_avatar_agent.py
python agents/content/content_import_agent.py
python workflows/workflow_manager.py
```

### Current Example (LiveFootballAvatar)
```bash
# Run the football commentary system
python agents/football_commentary_team.py

# Run tests for current implementation
python test_commentary.py
```

### Configuration Setup
1. Copy `config/config2.example.yaml` to `config/config2.yaml`
2. Update API keys and endpoints in the configuration files
3. Configure avatar API endpoint in `config/football_avatar.yaml`

## Integration Points

### MCP Server Integration
- Server URL: `http://localhost:8080`
- Tools: `process_match_event`, `trigger_avatar`

### n8n Workflow
- Webhook: `http://localhost:5678/webhook/match`
- Supported event types: goal, card, substitution, save, halftime, tactical, stat, transition, penalty

### Avatar API
- Endpoint: `http://localhost:8000/speak`
- Payload format: `{"text": "commentary", "emotion": "excited", "language": "Chinese"}`

## Development Notes

- The system uses async/await pattern throughout
- Each agent extends MetaGPT's Role class with custom Action implementations
- Event processing is handled through MetaGPT's Team.run() method with targeted message routing
- All agents watch for Message types to trigger their actions