"""
Test Football Commentary System

Example test demonstrating the football commentary team in action.
Shows how to process various match events through the multi-agent system.
"""
import asyncio
import yaml
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.football_commentary.football_commentary_team import FootballCommentaryTeam

async def main():
    # Load config from project root
    config_path = project_root / "config" / "football_avatar.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Initialize team
    team = FootballCommentaryTeam()

    # Test events
    events = [
        "GOAL! Messi scores a stunning free kick in the 25th minute!",
        "YELLOW CARD for Casemiro after a hard tackle on Modric.",
        "SUBSTITUTION: Haaland comes off, replaced by Alvarez.",
        "SAVE! Neuer denies a powerful shot from Mbappe.",
        "HALF TIME: Argentina 1 - 0 France.",
    ]

    # Process each event
    for event in events:
        print(f"\nProcessing event: {event}")
        await team.process_event(event)
        await asyncio.sleep(1)  # Simulate processing time

if __name__ == "__main__":
    asyncio.run(main())
