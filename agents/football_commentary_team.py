"""
Football Commentary Team
"""
import fire
from metagpt.team import Team
from metagpt.schema import Message
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
        # Broadcast event to all agents
        if event.startswith('TACTICAL:'):
            event = event.removeprefix("TACTICAL:")
            msg = Message(
                content=f"Match Event: {event}",
                role="User",
                send_to="TacticalAnalyst"
            )
        elif event.startswith('TRANSITION:'):
            event = event.removeprefix("TRANSITION:")
            msg = Message(
                content=f"Match Event: {event}",
                role="User",
                send_to="ShowHost"
            )
        else:
            msg = Message(
                content=f"Match Event: {event}",
                role="User",
                send_to="PlayByPlayCommentator"
            )
        await self.team.run_project(msg.content, send_to=msg.send_to)

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
