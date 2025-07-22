"""
Football Tactical Analyst Agent

Example agent that provides strategic analysis of football matches.
Demonstrates specialized agent behavior for tactical content.

This agent:
- Analyzes formations, strategies, and tactical plays
- Responds to events prefixed with "TACTICAL:"
- Provides detailed 2-3 sentence analysis
- Shows how to create domain-specific agents

Usage:
    Part of the FootballCommentaryTeam system
"""
from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message

class AnalyzeTactics(Action):
    PROMPT_TEMPLATE: str = """
    You are a tactical soccer analyst. 
    Given the match event: {event}
    Explain the strategies, formations, and key plays in detail in 2-3 sentences.
    """
    name: str = "AnalyzeTactics"

    async def run(self, event: str):
        prompt = self.PROMPT_TEMPLATE.format(event=event)
        rsp = await self._aask(prompt)
        return rsp

class TacticalAnalyst(Role):
    name: str = "TacticalAnalyst"
    profile: str = "Soccer Tactical Expert"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeTactics])
        self._watch([Message])  # Watches for incoming match events

    async def _act(self) -> Message:
        # logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        event = self.get_memories()[0].content  # Get latest match event
        
        analysis = await todo.run(event)
        return Message(content=analysis, role=self.profile, cause_by=type(todo))
