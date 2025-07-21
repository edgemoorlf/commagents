"""
Football PlayByPlay Commentator Agent
"""
import re
from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message

class GeneratePlayByPlay(Action):
    PROMPT_TEMPLATE: str = """
    You are a passionate play-by-play soccer commentator. 
    Given the match event: {event}
    Provide vivid and energetic narration in 1-2 sentences.
    """
    name: str = "GeneratePlayByPlay"

    async def run(self, event: str):
        prompt = self.PROMPT_TEMPLATE.format(event=event)
        rsp = await self._aask(prompt)
        return rsp

class PlayByPlayCommentator(Role):
    name: str = "PlayByPlayCommentator"
    profile: str = "Passionate Soccer Commentator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GeneratePlayByPlay])
        self._watch([Message])  # Watches for incoming match events

    async def _act(self) -> Message:
        # logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        event = self.get_memories()[0].content  # Get latest match event
        
        commentary = await todo.run(event)
        return Message(content=commentary, role=self.profile, cause_by=type(todo))
