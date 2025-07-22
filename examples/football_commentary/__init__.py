"""
Football Commentary Example

Demonstrates a multi-agent football commentary system using the platform.
This example shows how to create specialized agents that work together
to provide comprehensive football match commentary.

Components:
- PlayByPlayCommentator: Energetic match narration
- TacticalAnalyst: Strategic analysis and formations
- ShowHost: Transitions and discussion moderation
- FootballCommentaryTeam: Orchestrates the entire system

Usage:
    python examples/football_commentary/football_commentary_team.py
    python examples/football_commentary/test_commentary.py
"""

from .football_commentary_team import FootballCommentaryTeam
from .playbyplay_commentator import PlayByPlayCommentator
from .tactical_analyst import TacticalAnalyst
from .show_host import ShowHost

__all__ = [
    'FootballCommentaryTeam',
    'PlayByPlayCommentator', 
    'TacticalAnalyst',
    'ShowHost'
]