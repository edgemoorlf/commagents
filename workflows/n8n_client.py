"""
n8n Client for workflow integration
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import json


class N8nClient:
    """Client for n8n workflow automation platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webhook_url = config.get("webhook_url", "http://localhost:5678/webhook/match")
        self.api_url = config.get("api_url", "http://localhost:5678/api/v1")
        self.api_key = config.get("api_key")
        self.event_types = config.get("event_types", [])
        
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        
    async def initialize(self) -> None:
        """Initialize the n8n client"""
        try:
            # Create HTTP session
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-N8N-API-KEY"] = self.api_key
                
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers=headers
            )
            
            # Test connection
            await self.test_connection()
            self.connected = True
            self.logger.info("n8n client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize n8n client: {e}")
            raise
            
    async def test_connection(self) -> bool:
        """Test connection to n8n server"""
        try:
            if not self.session:
                return False
                
            # Try to get workflows to test API connection
            url = urljoin(self.api_url, "workflows")
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.logger.info("n8n API connection successful")
                    return True
                elif response.status == 401:
                    self.logger.warning("n8n API authentication failed")
                    return False
                else:
                    self.logger.warning(f"n8n API returned status {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.warning(f"n8n connection test failed: {e}")
            return False
            
    async def trigger_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n webhook with event data"""
        if not self.session:
            raise RuntimeError("n8n client not initialized")
            
        try:
            # Prepare webhook payload
            payload = {
                "event_type": event_type,
                "timestamp": data.get("timestamp"),
                "data": data
            }
            
            # Send webhook request
            async with self.session.post(self.webhook_url, json=payload) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.logger.info(f"Webhook triggered successfully for event: {event_type}")
                    return {"status": "success", "response": response_data}
                else:
                    self.logger.error(f"Webhook failed with status {response.status}: {response_data}")
                    return {"status": "error", "code": response.status, "response": response_data}
                    
        except Exception as e:
            self.logger.error(f"Webhook trigger failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def execute_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific workflow by ID"""
        if not self.session:
            raise RuntimeError("n8n client not initialized")
            
        try:
            url = urljoin(self.api_url, f"workflows/{workflow_id}/execute")
            
            async with self.session.post(url, json=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.logger.info(f"Workflow {workflow_id} executed successfully")
                    return {"status": "success", "execution_id": response_data.get("data", {}).get("executionId")}
                else:
                    self.logger.error(f"Workflow execution failed: {response_data}")
                    return {"status": "error", "response": response_data}
                    
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {"status": "error", "message": str(e)}
            
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows"""
        if not self.session:
            raise RuntimeError("n8n client not initialized")
            
        try:
            url = urljoin(self.api_url, "workflows")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    self.logger.error(f"Failed to get workflows: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Failed to get workflows: {e}")
            return []
            
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of a workflow execution"""
        if not self.session:
            raise RuntimeError("n8n client not initialized")
            
        try:
            url = urljoin(self.api_url, f"executions/{execution_id}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to get execution status: {response.status}")
                    return {"status": "error"}
                    
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {e}")
            return {"status": "error", "message": str(e)}
            
    async def send_avatar_command(self, avatar_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to avatar via n8n workflow"""
        try:
            # Prepare avatar command data
            data = {
                "avatar_id": avatar_id,
                "command": command,
                "timestamp": command.get("timestamp")
            }
            
            # Trigger avatar webhook
            return await self.trigger_webhook("avatar_command", data)
            
        except Exception as e:
            self.logger.error(f"Failed to send avatar command: {e}")
            return {"status": "error", "message": str(e)}
            
    async def notify_content_ready(self, content_type: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notify that content is ready for processing"""
        try:
            data = {
                "content_type": content_type,
                "content": content_data,
                "timestamp": content_data.get("timestamp")
            }
            
            return await self.trigger_webhook("content_ready", data)
            
        except Exception as e:
            self.logger.error(f"Failed to notify content ready: {e}")
            return {"status": "error", "message": str(e)}
            
    def can_handle_event(self, event_type: str) -> bool:
        """Check if client can handle specific event type"""
        return not self.event_types or event_type in self.event_types
        
    async def close(self) -> None:
        """Close the n8n client"""
        if self.session:
            await self.session.close()
            self.session = None
            
        self.connected = False
        self.logger.info("n8n client closed")
        
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "connected": self.connected,
            "webhook_url": self.webhook_url,
            "api_url": self.api_url,
            "event_types": self.event_types,
            "has_api_key": bool(self.api_key)
        }