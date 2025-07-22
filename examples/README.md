# Examples

This directory contains example implementations that demonstrate various features and capabilities of the AI Avatar Platform.

## Available Examples

### 🏈 Football Commentary (`football_commentary/`)

A comprehensive multi-agent system for football match commentary that showcases:

- **Multi-Agent Coordination**: Three specialized agents working together
- **Event Routing**: Different event types routed to appropriate agents
- **Custom Actions**: Domain-specific actions and prompts
- **MetaGPT Integration**: Team-based agent orchestration

**Components:**
- `PlayByPlayCommentator` - Energetic match narration
- `TacticalAnalyst` - Strategic analysis and formations
- `ShowHost` - Discussion moderation and transitions
- `FootballCommentaryTeam` - System orchestration

**Usage:**
```bash
# Run the commentary system
python examples/football_commentary/football_commentary_team.py

# Test with sample events
python examples/football_commentary/test_commentary.py
```

**Features Demonstrated:**
- Agent specialization and coordination
- Event-driven processing
- Custom prompt templates
- Team-based workflows
- Real-time commentary generation

See [football_commentary/README.md](football_commentary/README.md) for detailed documentation.

## How to Use Examples

1. **From Project Root**: Run examples from the project root directory to ensure proper imports and configuration
2. **Configuration**: Examples use the main platform configuration files in `config/`
3. **Dependencies**: Ensure MetaGPT and other dependencies are installed
4. **Exploration**: Each example includes comprehensive documentation and comments

## Creating New Examples

When creating new examples:

1. **Create Directory**: `examples/your_example_name/`
2. **Package Structure**: Include `__init__.py` and proper imports
3. **Documentation**: Add README.md explaining the example
4. **Test Script**: Include a test/demo script
5. **Configuration**: Use existing config files or create example-specific ones

### Example Template

```
examples/your_example/
├── __init__.py              # Package initialization
├── your_main_component.py   # Main implementation
├── supporting_agents.py     # Additional agents
├── test_example.py          # Test and demo script
└── README.md               # Documentation
```

## Integration with Avatar Workshop

Examples can be enhanced with Avatar Manufacturing Workshop components:

```python
from management.avatar_config_manager import AvatarConfigManager
from agents.avatar.base_avatar_agent import BaseAvatarAgent

# Create specialized avatars for your example
manager = AvatarConfigManager()
await manager.create_avatar("example_avatar", "conversational", {
    'initial_knowledge': [
        {'content': 'Domain-specific knowledge', 'category': 'domain'}
    ]
})
```

## Learning Path

1. **Start with Football Commentary** - Understand multi-agent coordination
2. **Explore Agent Types** - See different agent specializations
3. **Study Integration Patterns** - Learn how components work together
4. **Create Your Own** - Build domain-specific examples

These examples serve as both learning materials and starting points for your own implementations using the AI Avatar Platform.