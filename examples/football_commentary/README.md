# Football Commentary Example

This example demonstrates a multi-agent football commentary system built on the AI Avatar Platform. It showcases how multiple specialized agents can work together to provide comprehensive football match coverage.

## Overview

The Football Commentary Example consists of four main components:

### Agents

1. **PlayByPlayCommentator** (`playbyplay_commentator.py`)
   - Provides energetic, vivid narration of match events
   - Handles goals, saves, penalties, and general match events
   - Uses passionate, engaging language

2. **TacticalAnalyst** (`tactical_analyst.py`)
   - Analyzes formations, strategies, and tactical plays
   - Responds to events prefixed with "TACTICAL:"
   - Provides detailed strategic insights

3. **ShowHost** (`show_host.py`)
   - Moderates discussion flow between commentators
   - Handles events prefixed with "TRANSITION:"
   - Provides smooth transitions and summaries

### Team Orchestration

4. **FootballCommentaryTeam** (`football_commentary_team.py`)
   - Orchestrates all agents using MetaGPT's Team framework
   - Routes events to appropriate agents based on prefixes
   - Manages the overall commentary workflow

## Event Routing

The system uses event prefixes to route messages to the appropriate agent:

- **Default** → PlayByPlayCommentator (goals, saves, cards, etc.)
- **"TACTICAL:"** → TacticalAnalyst (formation changes, strategic analysis)
- **"TRANSITION:"** → ShowHost (discussion moderation, transitions)

## Usage

### Running the Example

```bash
# From the project root
cd examples/football_commentary

# Run the main commentary system
python football_commentary_team.py

# Run the test suite
python test_commentary.py
```

### Example Events

The system processes various types of football events:

```python
# Play-by-play events (handled by PlayByPlayCommentator)
"GOAL! Messi scores a stunning free kick in the 25th minute!"
"SAVE! Neuer denies a powerful shot from Mbappe."
"YELLOW CARD for Casemiro after a hard tackle on Modric."

# Tactical events (handled by TacticalAnalyst)
"TACTICAL: Argentina switches to 4-4-2 formation"
"TACTICAL: France using high press to disrupt Argentina's buildup"

# Transition events (handled by ShowHost)
"TRANSITION: Let's get analysis from our expert"
"TRANSITION: Back to the action on the pitch"
```

## Configuration

The example uses the main platform configuration:

- **LLM Settings**: Configure in `config/config2.yaml`
- **Avatar Settings**: Configure in `config/football_avatar.yaml`

## Integration with Avatar Workshop

This example can be enhanced with the Avatar Manufacturing Workshop components:

```python
from management.avatar_config_manager import AvatarConfigManager
from agents.avatar.base_avatar_agent import BaseAvatarAgent

# Create football commentator avatars
manager = AvatarConfigManager()

# Create play-by-play avatar with energetic personality
await manager.create_avatar("playbyplay_avatar", "conversational", {
    'name': 'Football Commentary Avatar',
    'personality_config': {
        'default_personality': {
            'extraversion': 0.9,  # Very outgoing
            'agreeableness': 0.7,
            'conscientiousness': 0.6,
            'neuroticism': -0.3,
            'openness': 0.8
        }
    },
    'initial_knowledge': [{
        'content': 'I am a passionate football commentator who loves the beautiful game',
        'category': 'identity',
        'tags': ['football', 'commentary', 'passionate']
    }]
})
```

## Key Learning Points

This example demonstrates:

1. **Multi-Agent Coordination**: How agents work together in teams
2. **Event Routing**: Directing different events to specialized agents
3. **Custom Actions**: Creating domain-specific actions and prompts
4. **MetaGPT Integration**: Using the MetaGPT framework for agent orchestration
5. **Extensibility**: How the system can be extended with new agent types

## Extending the Example

You can extend this example by:

1. **Adding New Agent Types**:
   - Statistics Analyst
   - Fan Reaction Agent
   - Historical Context Agent

2. **Enhanced Event Processing**:
   - Real-time data feeds
   - Video analysis integration
   - Player performance tracking

3. **Avatar Integration**:
   - Visual avatar representation
   - Emotion-based responses
   - Personalized commentary styles

4. **Workflow Integration**:
   - n8n workflow triggers
   - External service integration
   - Real-time broadcasting

## Files

- `football_commentary_team.py` - Main team orchestration
- `playbyplay_commentator.py` - Play-by-play commentary agent
- `tactical_analyst.py` - Strategic analysis agent  
- `show_host.py` - Discussion moderation agent
- `test_commentary.py` - Test and demonstration script
- `__init__.py` - Package initialization
- `README.md` - This documentation file

This example serves as a foundation for building sophisticated multi-agent systems on the AI Avatar Platform.