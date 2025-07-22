"""
Workflows package for n8n integration
"""
from .n8n_client import N8nClient
from .workflow_manager import WorkflowManager
from .event_dispatcher import EventDispatcher

__all__ = ["N8nClient", "WorkflowManager", "EventDispatcher"]