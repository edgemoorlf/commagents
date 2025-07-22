"""
Base Agent and Action classes for the AI Avatar Platform
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.logs import logger


class BaseAction(Action):
    """Base action class for all platform actions"""
    
    def __init__(self, name: str = "", context: Optional[Dict] = None):
        super().__init__(name=name, context=context)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.created_at = datetime.now()
        
    async def run(self, *args, **kwargs) -> Any:
        """Execute the action with logging and error handling"""
        self.logger.info(f"Executing action: {self.name}")
        start_time = datetime.now()
        
        try:
            result = await self._execute(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Action {self.name} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Action {self.name} failed: {e}")
            raise
            
    @abstractmethod
    async def _execute(self, *args, **kwargs) -> Any:
        """Abstract method to be implemented by subclasses"""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get action metadata"""
        return {
            "name": self.name,
            "class": self.__class__.__name__,
            "created_at": self.created_at.isoformat(),
            "context": self.context
        }


class BaseAgent(Role):
    """Base agent class for all platform agents"""
    
    def __init__(self, name: str = "", profile: str = "", config: Optional[Dict] = None):
        super().__init__(name=name, profile=profile)
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.created_at = datetime.now()
        self.state = "initialized"
        self.metrics = {
            "messages_processed": 0,
            "actions_executed": 0,
            "errors": 0,
            "last_active": None
        }
        
    async def _act(self) -> Message:
        """Enhanced act method with metrics and error handling"""
        self.logger.debug(f"Agent {self.name} starting action")
        
        try:
            # Update metrics
            self.metrics["last_active"] = datetime.now().isoformat()
            
            # Execute the agent-specific action
            result = await self._execute_action()
            
            # Update success metrics
            self.metrics["actions_executed"] += 1
            self.state = "active"
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.state = "error"
            self.logger.error(f"Agent {self.name} action failed: {e}")
            raise
            
    @abstractmethod
    async def _execute_action(self) -> Message:
        """Abstract method for agent-specific action execution"""
        pass
        
    def process_message(self, message: Message) -> None:
        """Process incoming message with metrics tracking"""
        self.metrics["messages_processed"] += 1
        self.logger.debug(f"Processing message from {message.role}")
        
        # Add message to memory
        self.rc.memory.add(message)
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "name": self.name,
            "profile": self.profile,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics,
            "config": self.config
        }
        
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update agent configuration"""
        self.config.update(new_config)
        self.logger.info(f"Configuration updated for agent {self.name}")
        
    async def initialize(self) -> None:
        """Initialize agent-specific resources"""
        self.logger.info(f"Initializing agent: {self.name}")
        self.state = "ready"
        
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        self.logger.info(f"Cleaning up agent: {self.name}")
        self.state = "stopped"


class WorkflowAction(BaseAction):
    """Action that can trigger n8n workflows"""
    
    def __init__(self, name: str = "", workflow_id: str = "", context: Optional[Dict] = None):
        super().__init__(name=name, context=context)
        self.workflow_id = workflow_id
        
    async def trigger_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n workflow"""
        # TODO: Implement when n8n client is ready
        self.logger.info(f"Triggering workflow {self.workflow_id} with data: {data}")
        return {"status": "triggered", "workflow_id": self.workflow_id}


class McpAction(BaseAction):
    """Action that can use MCP tools"""
    
    def __init__(self, name: str = "", tools: Optional[List[str]] = None, context: Optional[Dict] = None):
        super().__init__(name=name, context=context)
        self.tools = tools or []
        
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call an MCP tool"""
        # TODO: Implement when MCP client is ready
        self.logger.info(f"Calling MCP tool {tool_name} with parameters: {parameters}")
        return {"status": "called", "tool": tool_name, "result": "placeholder"}


class EventDrivenAgent(BaseAgent):
    """Agent that responds to specific event types"""
    
    def __init__(self, name: str = "", profile: str = "", 
                 event_types: Optional[List[str]] = None, config: Optional[Dict] = None):
        super().__init__(name=name, profile=profile, config=config)
        self.event_types = event_types or []
        
    def can_handle_event(self, event_type: str) -> bool:
        """Check if agent can handle specific event type"""
        return event_type in self.event_types or not self.event_types
        
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> Optional[Message]:
        """Handle a specific event"""
        if not self.can_handle_event(event_type):
            return None
            
        self.logger.info(f"Handling event {event_type}")
        
        # Create a message from the event
        event_message = Message(
            content=f"{event_type}: {json.dumps(event_data)}",
            role=self.profile,
            cause_by=type(self)
        )
        
        # Process the event message
        self.process_message(event_message)
        
        # Execute action
        return await self._act()