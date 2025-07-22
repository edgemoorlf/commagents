# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation File Index

### Core Documentation Files
- **CLAUDE.md** (this file) - Primary development guidance for Claude Code with project architecture and implementation plans
- **CLAUDE_zh.md** - Chinese version of development guidance with identical structure to CLAUDE.md
- **REQUIREMENTS.md** - Living requirements specification document (versioned, current active requirements)
- **PROGRESS.md** - Development progress tracking (what's implemented, current phase status, next steps)
- **README.md** - Public project overview and quick start guide for external users
- **README_zh.md** - Chinese version of public project overview with identical structure to README.md

### Change Management Documentation
- **CHANGELOG.md** - Historical record of requirement changes with impact analysis and rollback information
- **docs/ROLLBACK_PROCEDURES.md** - Detailed rollback procedures and change management workflows
- **docs/archived_plans/*.md** - Archived copies of replaced architectural plans for rollback reference

### Specialized Documentation
- **DEV_WORKFLOW.md** - Development workflow and contribution guidelines

### Update Protocol
When making changes that affect project architecture, features, or requirements:

1. **Always Update (Primary):**
   - **CLAUDE.md** - Core architecture, implementation plans, agent specifications
   - **REQUIREMENTS.md** - Add new version with updated specifications
   - **CHANGELOG.md** - Document changes with impact analysis
   - **PROGRESS.md** - Update phase status and development progress

2. **Update When Relevant (Secondary):**
   - **README.md/README_zh.md** - If changes affect public API or user-facing features
   - **CLAUDE_zh.md** - Mirror all changes made to CLAUDE.md
   - **docs/archived_plans/** - Archive replaced plans before major changes

3. **Update Protocol Checklist:**
   ```
   [ ] CLAUDE.md - Updated architecture/plans
   [ ] REQUIREMENTS.md - New version created
   [ ] CHANGELOG.md - Change documented with impact
   [ ] PROGRESS.md - Phase status updated
   [ ] CLAUDE_zh.md - Chinese equivalent updated
   [ ] README.md/README_zh.md - Public documentation updated (if needed)
   [ ] Archived old plans (if major architectural change)
   [ ] Git tagged with requirement version
   ```

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

#### Influencer Content Harvesting Agent
- **WebSurfer Integration**: Automated browsing and content scraping from social media platforms
- **Multi-Media Extraction**: Downloads and processes vlogs, images, and short videos
- **Content Cataloging**: Organizes harvested content by type, date, and engagement metrics
- **Platform Coverage**: TikTok, Instagram, YouTube, Twitter, and other major platforms

#### Style Analysis Agent
- **Content Style Extraction**: Analyzes visual aesthetics, tone, themes, and presentation patterns
- **AI-Powered Pattern Recognition**: Uses computer vision and NLP to identify unique style elements
- **Trend Identification**: Extracts recurring themes, topics, and content formats
- **Personality Modeling**: Creates comprehensive influencer personality and brand profiles

#### Content Generation Agent
- **Style-Matched Generation**: Produces content that mimics identified influencer styles
- **Multi-Format Creation**: Generates vlogs, images, short videos, and social media posts
- **Brand Consistency**: Maintains coherent voice and visual identity across content types
- **Tool-Enhanced**: Uses LLM + external tools + n8n workflows + AI image/video generation

#### Video Production Pipeline Agent
- **End-to-End Video Creation**: From script to final video
- **n8n Workflow Integration**: Automated production pipeline
- **Tool Integration**: External video processing tools

### 3. Ecosystem Integration (生态平台接入)

#### Social Media Publishing Agent
- **Multi-Platform Distribution**: Automated posting to TikTok, Instagram, YouTube, Twitter, etc.
- **Platform Optimization**: Adapts content format and metadata for each social media platform
- **Scheduling and Timing**: Optimizes posting times based on audience engagement patterns
- **Cross-Platform Strategy**: Coordinates content release across multiple platforms
- **WebSurfer Integration**: Platform-specific publishing logic and API management

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
- **ADD: WebSurfer configuration for content scraping**
- **ADD: AI generation tool APIs (DALL-E, RunwayML, ElevenLabs)**

### Social Media Config (`config/social_media.yaml`) - NEW
Influencer pipeline specific settings:
- Platform API credentials (TikTok, Instagram, YouTube, Twitter)
- Content harvesting targets and schedules
- Publishing workflows and timing optimization
- Style analysis model configurations

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
- [ ] Set up configuration management system with social media API support
- [ ] Establish n8n workflow integration foundation
- [ ] Create MCP server integration layer
- [ ] **ADD: WebSurfer tool integration for content scraping**
- [ ] **ADD: Multi-platform API client base classes**
- [ ] **ADD: Content storage and media management system**

#### Avatar Manufacturing Workshop - Foundation
- [ ] Implement `LiveAvatarAgent` base class with knowledge management
- [ ] Create avatar configuration system
- [ ] Build basic content generation from single phrases
- [ ] Implement avatar-to-API communication layer
- [ ] **ADD: Avatar personality adaptation for influencer styles**

### Phase 2: Avatar Manufacturing Workshop Enhancement
**Timeline: Weeks 5-8**

#### Enhanced Avatar System
- [ ] Implement advanced avatar personality system with style adaptation
- [ ] Create dynamic knowledge injection from social media content
- [ ] Build multi-modal content generation (text, voice, visual style)
- [ ] **ADD: Avatar brand consistency engine for influencer mimicry**
- [ ] **ADD: Personality evolution based on content analysis**

#### Content Processing Foundation
- [ ] Implement basic WebSurfer integration for content discovery
- [ ] Create content quality and filtering mechanisms
- [ ] Build content versioning and management system
- [ ] **ADD: Media processing pipeline for images and videos**
- [ ] **ADD: Style analysis preparation for Phase 3 integration**

#### Management Interface Enhancement
- [ ] Enhanced avatar configuration for influencer-style avatars
- [ ] **ADD: Social media account linking and management**
- [ ] **ADD: Content scheduling and publishing workflow preparation**

### Phase 3: Influencer Content Pipeline
**Timeline: Weeks 9-12**

#### Influencer Content Harvesting
- [ ] Implement `InfluencerHarvestingAgent` with WebSurfer capabilities
- [ ] Build multi-platform content scraping (TikTok, Instagram, YouTube, Twitter)
- [ ] Create media download and storage system for vlogs, images, videos
- [ ] Implement content metadata extraction and cataloging

#### Style Analysis and Modeling
- [ ] Develop `StyleAnalysisAgent` for content pattern recognition
- [ ] Build AI-powered visual and textual style extraction
- [ ] Create influencer personality and brand modeling system
- [ ] Implement trend and theme identification algorithms

#### AI Content Generation Pipeline
- [ ] Build style-matched content generation capabilities
- [ ] Integrate AI image and video generation tools
- [ ] Create multi-format content creation (vlogs, posts, stories)
- [ ] Implement brand consistency and quality control systems

#### Social Media Publishing & Analytics
- [ ] Develop `SocialMediaPublishingAgent` for multi-platform distribution
- [ ] Build platform-specific content optimization and formatting
- [ ] Implement automated scheduling and timing optimization
- [ ] Create comprehensive engagement and performance analytics

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

#### Influencer Content Pipeline Agents
```
agents/content/
├── influencer_harvesting_agent.py    # Multi-platform content scraping with WebSurfer
├── style_analysis_agent.py           # AI-powered style and pattern extraction
├── content_generation_agent.py       # Style-matched multi-format content creation
├── social_media_publishing_agent.py  # Multi-platform automated publishing
└── content_transformer.py            # Brand-consistent content transformation
```

#### Content Processing Tools
```
tools/content/
├── media_downloader.py               # Video, image, and audio extraction
├── style_extractor.py                # Visual and textual style analysis
├── brand_profiler.py                 # Influencer personality modeling
├── content_generator.py              # AI-powered content creation
└── platform_optimizer.py             # Social media platform-specific formatting
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
├── video_production_agent.py     # End-to-end video creation from harvested content
├── vlog_generator.py             # AI-powered vlog script and video generation
├── short_video_creator.py        # TikTok/Instagram Reels style video creation
├── video_processor.py            # External tool integration for video editing
└── production_pipeline.py       # Automated video workflow with style matching
```

### Social Media Integration Tasks
```
social_media/
├── platform_clients/
│   ├── tiktok_client.py             # TikTok API integration
│   ├── instagram_client.py          # Instagram Graph API integration
│   ├── youtube_client.py            # YouTube Data API integration
│   └── twitter_client.py            # Twitter API v2 integration
├── content_adapters/
│   ├── format_optimizer.py          # Platform-specific format conversion
│   ├── metadata_generator.py        # Hashtags, captions, descriptions
│   └── engagement_optimizer.py      # Timing and audience targeting
└── publishing_scheduler.py       # Cross-platform posting coordination
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

### Influencer Content Pipeline Development Commands
```bash
# Run influencer harvesting agent
python agents/content/influencer_harvesting_agent.py --target-url <influencer_profile>

# Analyze harvested content styles
python agents/content/style_analysis_agent.py --content-dir ./harvested_content

# Generate style-matched content
python agents/content/content_generation_agent.py --style-profile ./profiles/influencer_style.json

# Publish to social media platforms
python agents/content/social_media_publishing_agent.py --content ./generated_content --platforms all
```

### Configuration Setup
1. Copy `config/config2.example.yaml` to `config/config2.yaml`
2. Update API keys and endpoints in the configuration files
3. Configure avatar API endpoint in `config/football_avatar.yaml`
4. Set up social media platform API credentials in `config/social_media.yaml`
5. Configure content harvesting targets in `config/influencer_targets.yaml`

## Integration Points

### MCP Server Integration
- Server URL: `http://localhost:8080`
- Tools: `process_match_event`, `trigger_avatar`

### n8n Workflow
- Webhook: `http://localhost:5678/webhook/match`
- Supported event types: goal, card, substitution, save, halftime, tactical, stat, transition, penalty

### Social Media Platform APIs
- **TikTok**: Research API, Creator Portal API
- **Instagram**: Graph API, Basic Display API
- **YouTube**: Data API v3, Analytics API
- **Twitter**: API v2, Media Upload API

### Content Generation Tools
- **AI Image Generation**: DALL-E 3, Midjourney API, Stable Diffusion
- **AI Video Generation**: RunwayML, Pika Labs, Synthesia API
- **Voice Cloning**: ElevenLabs, Murf, Azure Cognitive Services
- **Text Generation**: GPT-4, Claude, custom fine-tuned models

### Content Analysis Tools
- **Computer Vision**: OpenCV, YOLO, Google Vision API
- **Style Analysis**: Custom CNN models, feature extraction
- **NLP Processing**: spaCy, NLTK, sentiment analysis models
- **Audio Analysis**: librosa, speech-to-text APIs

## Development Notes

- The system uses async/await pattern throughout
- Each agent extends MetaGPT's Role class with custom Action implementations
- Event processing is handled through MetaGPT's Team.run() method with targeted message routing
- All agents watch for Message types to trigger their actions