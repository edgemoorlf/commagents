"""
Workflow Manager for orchestrating n8n workflows
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json

from .n8n_client import N8nClient


class WorkflowManager:
    """Manages workflow execution and orchestration"""
    
    def __init__(self, n8n_client: N8nClient):
        self.n8n_client = n8n_client
        self.logger = logging.getLogger(__name__)
        
        # Workflow state tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_handlers: Dict[str, Callable] = {}
        self.running = False
        
    async def initialize(self) -> None:
        """Initialize workflow manager"""
        try:
            # Get available workflows from n8n
            workflows = await self.n8n_client.get_workflows()
            self.logger.info(f"Found {len(workflows)} available workflows")
            
            # Register default workflow handlers
            self._register_default_handlers()
            
            self.logger.info("Workflow manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow manager: {e}")
            raise
            
    def _register_default_handlers(self) -> None:
        """Register default workflow event handlers"""
        self.workflow_handlers.update({
            "avatar_speak": self._handle_avatar_speak,
            "content_generation": self._handle_content_generation,
            "video_production": self._handle_video_production,
            "publishing": self._handle_publishing,
            "analytics_update": self._handle_analytics_update
        })
        
    async def trigger_workflow(self, workflow_type: str, data: Dict[str, Any], 
                             callback: Optional[Callable] = None) -> str:
        """Trigger a workflow and optionally register callback"""
        try:
            # Generate workflow execution ID
            execution_id = f"{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare workflow data
            workflow_data = {
                "execution_id": execution_id,
                "workflow_type": workflow_type,
                "timestamp": datetime.now().isoformat(),
                **data
            }
            
            # Track active workflow
            self.active_workflows[execution_id] = {
                "type": workflow_type,
                "status": "initiated",
                "started_at": datetime.now().isoformat(),
                "callback": callback,
                "data": workflow_data
            }
            
            # Execute workflow based on type
            if workflow_type in self.workflow_handlers:
                result = await self.workflow_handlers[workflow_type](workflow_data)
                self.active_workflows[execution_id]["status"] = "completed"
                self.active_workflows[execution_id]["result"] = result
            else:
                # Trigger generic webhook
                result = await self.n8n_client.trigger_webhook(workflow_type, workflow_data)
                self.active_workflows[execution_id]["status"] = "triggered"
                
            # Execute callback if provided
            if callback:
                try:
                    await callback(execution_id, result)
                except Exception as e:
                    self.logger.error(f"Workflow callback failed: {e}")
                    
            self.logger.info(f"Workflow {workflow_type} triggered with ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow {workflow_type}: {e}")
            raise
            
    async def _handle_avatar_speak(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle avatar speak workflow"""
        try:
            # Extract avatar speak parameters
            text = data.get("text", "")
            emotion = data.get("emotion", "neutral")
            language = data.get("language", "Chinese")
            avatar_id = data.get("avatar_id", "default")
            
            # Send command to avatar
            command = {
                "text": text,
                "emotion": emotion,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.n8n_client.send_avatar_command(avatar_id, command)
            
            self.logger.info(f"Avatar speak command sent: {text[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"Avatar speak workflow failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_content_generation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content generation workflow"""
        try:
            # Prepare content generation data
            content_data = {
                "prompt": data.get("prompt", ""),
                "content_type": data.get("content_type", "text"),
                "parameters": data.get("parameters", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Notify content generation
            result = await self.n8n_client.notify_content_ready("generation_request", content_data)
            
            self.logger.info("Content generation workflow triggered")
            return result
            
        except Exception as e:
            self.logger.error(f"Content generation workflow failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_video_production(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video production workflow"""
        try:
            # Prepare video production data
            video_data = {
                "script": data.get("script", ""),
                "style": data.get("style", "default"),
                "duration": data.get("duration", 60),
                "parameters": data.get("parameters", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.n8n_client.trigger_webhook("video_production", video_data)
            
            self.logger.info("Video production workflow triggered")
            return result
            
        except Exception as e:
            self.logger.error(f"Video production workflow failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_publishing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle publishing workflow"""
        try:
            # Prepare publishing data
            publish_data = {
                "content": data.get("content", ""),
                "platforms": data.get("platforms", []),
                "schedule": data.get("schedule"),
                "metadata": data.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.n8n_client.trigger_webhook("publishing", publish_data)
            
            self.logger.info(f"Publishing workflow triggered for platforms: {publish_data['platforms']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Publishing workflow failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_analytics_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analytics update workflow"""
        try:
            # Prepare analytics data
            analytics_data = {
                "metrics": data.get("metrics", {}),
                "event_type": data.get("event_type", ""),
                "entity_id": data.get("entity_id", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.n8n_client.trigger_webhook("analytics_update", analytics_data)
            
            self.logger.info("Analytics update workflow triggered")
            return result
            
        except Exception as e:
            self.logger.error(f"Analytics update workflow failed: {e}")
            return {"status": "error", "message": str(e)}
            
    def register_workflow_handler(self, workflow_type: str, handler: Callable) -> None:
        """Register custom workflow handler"""
        self.workflow_handlers[workflow_type] = handler
        self.logger.info(f"Registered handler for workflow type: {workflow_type}")
        
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific workflow execution"""
        return self.active_workflows.get(execution_id)
        
    def get_active_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get all active workflows"""
        return self.active_workflows.copy()
        
    async def cleanup_completed_workflows(self, max_age_hours: int = 24) -> None:
        """Clean up completed workflows older than specified hours"""
        try:
            current_time = datetime.now()
            to_remove = []
            
            for execution_id, workflow in self.active_workflows.items():
                if workflow["status"] in ["completed", "error"]:
                    started_at = datetime.fromisoformat(workflow["started_at"])
                    age_hours = (current_time - started_at).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        to_remove.append(execution_id)
                        
            for execution_id in to_remove:
                del self.active_workflows[execution_id]
                
            if to_remove:
                self.logger.info(f"Cleaned up {len(to_remove)} completed workflows")
                
        except Exception as e:
            self.logger.error(f"Workflow cleanup failed: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get workflow manager status"""
        return {
            "running": self.running,
            "active_workflows": len(self.active_workflows),
            "registered_handlers": list(self.workflow_handlers.keys()),
            "n8n_status": self.n8n_client.get_status()
        }