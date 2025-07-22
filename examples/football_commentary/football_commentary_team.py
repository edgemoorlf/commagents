"""
Football Commentary Team

Example implementation demonstrating multi-agent football commentary system.
Shows how specialized agents work together for comprehensive match coverage.
"""
import fire
import sys
from pathlib import Path

# Add project root to path for imports when run directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from metagpt.team import Team
from metagpt.schema import Message

# Handle imports based on execution context
try:
    # Try relative imports first (when imported as module)
    from .playbyplay_commentator import PlayByPlayCommentator
    from .tactical_analyst import TacticalAnalyst
    from .show_host import ShowHost
except ImportError:
    # Fall back to absolute imports (when run directly)
    from playbyplay_commentator import PlayByPlayCommentator
    from tactical_analyst import TacticalAnalyst
    from show_host import ShowHost

class FootballCommentaryTeam:
    def __init__(self):
        self.team = Team()
        self.team.hire([
            PlayByPlayCommentator(),
            TacticalAnalyst(),
            ShowHost()
        ])

    async def process_event(self, event: str):
        # Routing events to agents
        send_to = "PlayByPlayCommentator"
        if event.startswith('TACTICAL:'):
            send_to="TacticalAnalyst"
        elif event.startswith('TRANSITION:'):
            send_to="ShowHost"

        await self.team.run(idea=event, send_to=send_to, n_round=1)
        

async def main():
    team = FootballCommentaryTeam()
    
    # Sample events (would come from MCP server in production)
    events = [
        # Play-by-play events
        "GOAL! Messi scores a stunning free kick in the 25th minute!",
        "SAVE! Neuer denies a powerful shot from Mbappe.",
        "PENALTY! Foul in the box by Upamecano!",
        
        # Tactical analysis events
        "TACTICAL: Argentina switches to 4-4-2 formation",
        "TACTICAL: France using high press to disrupt Argentina's buildup",
        "TACTICAL: Possession - Argentina 58%, France 42%",
        
        # Host transition events
        "TRANSITION: Let's get analysis from our expert",
        "TRANSITION: Back to the action on the pitch",
        "TRANSITION: What a first half we've had!",
        
        # Other match events
        "YELLOW CARD for Casemiro after a hard tackle on Modric.",
        "SUBSTITUTION: Haaland comes off, replaced by Alvarez.",
        "HALF TIME: Argentina 1 - 0 France.",
    ]

    for event in events:
        await team.process_event(event)

if __name__ == "__main__":
    fire.Fire(main)
