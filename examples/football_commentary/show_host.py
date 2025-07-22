"""
Football Show Host Agent

Example agent that moderates discussion flow between commentators.
Demonstrates how to create coordinating agents that manage interactions.

This agent:
- Provides smooth transitions between different commentary types  
- Responds to events prefixed with "TRANSITION:"
- Moderates discussion flow and provides summaries
- Shows agent coordination patterns

Usage:
    Part of the FootballCommentaryTeam system
"""
from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message

class ModerateDiscussion(Action):
    PROMPT_TEMPLATE: str = """
    You are a friendly sports show host.
    Given the current match context: {context}
    And the latest commentary: {commentary}
    Provide a smooth transition or summary in 1-2 sentences to keep the discussion flowing.
    """
    name: str = "ModerateDiscussion"

    async def run(self, context: str, commentary: str):
        prompt = self.PROMPT_TEMPLATE.format(context=context, commentary=commentary)
        rsp = await self._aask(prompt)
        return rsp

class ShowHost(Role):
    name: str = "ShowHost"
    profile: str = "Sports Show Host"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ModerateDiscussion])
        self._watch([Message])  # Watches for incoming commentary

    async def _act(self) -> Message:
        # logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        context = self.get_memories()[0].content  # Get match context
        commentary = self.get_memories()[1].content if len(self.get_memories()) > 1 else ""
        
        moderation = await todo.run(context, commentary)
        return Message(content=moderation, role=self.profile, cause_by=type(todo))
