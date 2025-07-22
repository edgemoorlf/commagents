"""
Platform Manager - Central orchestrator for the AI Avatar Platform
"""
import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path

from metagpt.team import Team
from metagpt.logs import logger

from .config_manager import ConfigManager
from workflows.n8n_client import N8nClient
from tools.mcp_client import McpClient


class PlatformManager:
    """Central manager for the AI Avatar Platform"""
    
    def __init__(self, config: Dict, mode: str = "full"):
        self.config = config
        self.mode = mode
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.teams: Dict[str, Team] = {}
        self.n8n_client: Optional[N8nClient] = None
        self.mcp_client: Optional[McpClient] = None
        
        # Component status
        self.running = False
        self.components_initialized = False
        
    async def start(self):
        """Start the platform and initialize all components"""
        self.logger.info(f"Initializing platform in {self.mode} mode")
        
        try:
            # Initialize core integrations
            await self._initialize_integrations()
            
            # Initialize components based on mode
            if self.mode in ["avatar", "full"]:
                await self._initialize_avatar_workshop()
                
            if self.mode in ["content", "full"]:
                await self._initialize_content_factory()
                
            if self.mode in ["analytics", "full"]:
                await self._initialize_analytics()
                
            self.components_initialized = True
            self.logger.info("Platform initialization completed")
            
        except Exception as e:
            self.logger.error(f"Platform initialization failed: {e}")
            raise
            
    async def _initialize_integrations(self):
        """Initialize n8n and MCP integrations"""
        try:
            # Initialize n8n client
            if "n8n" in self.config:
                self.n8n_client = N8nClient(self.config["n8n"])
                await self.n8n_client.initialize()
                self.logger.info("n8n integration initialized")
                
            # Initialize MCP client
            if "mcp" in self.config:
                self.mcp_client = McpClient(self.config["mcp"])
                await self.mcp_client.initialize()
                self.logger.info("MCP integration initialized")
                
        except Exception as e:
            self.logger.error(f"Integration initialization failed: {e}")
            raise
            
    async def _initialize_avatar_workshop(self):
        """Initialize Avatar Manufacturing Workshop components"""
        self.logger.info("Initializing Avatar Workshop...")
        
        # TODO: Initialize avatar agents when implemented
        # from agents.avatar.base_avatar_agent import BaseAvatarAgent
        # avatar_team = Team()
        # self.teams["avatar"] = avatar_team
        
        self.logger.info("Avatar Workshop initialized")
        
    async def _initialize_content_factory(self):
        """Initialize Content Factory components"""
        self.logger.info("Initializing Content Factory...")
        
        # TODO: Initialize content agents when implemented
        # from agents.content.content_import_agent import ContentImportAgent
        # from agents.content.content_generation_agent import ContentGenerationAgent
        # content_team = Team()
        # self.teams["content"] = content_team
        
        self.logger.info("Content Factory initialized")
        
    async def _initialize_analytics(self):
        """Initialize Data Analytics components"""
        self.logger.info("Initializing Analytics...")
        
        # TODO: Initialize analytics components when implemented
        # from analytics.metrics_collector import MetricsCollector
        
        self.logger.info("Analytics initialized")
        
    async def run(self):
        """Main platform run loop"""
        if not self.components_initialized:
            raise RuntimeError("Platform not properly initialized")
            
        self.running = True
        self.logger.info("Platform is now running")
        
        try:
            while self.running:
                # Main event loop - process events, handle workflows
                await asyncio.sleep(1)  # Prevent busy waiting
                
                # TODO: Add event processing logic here
                # - Process incoming events from MCP
                # - Handle n8n workflow triggers
                # - Manage agent interactions
                
        except Exception as e:
            self.logger.error(f"Platform runtime error: {e}")
            raise
            
    async def stop(self):
        """Gracefully stop the platform"""
        self.logger.info("Stopping platform...")
        self.running = False
        
        # Stop all teams
        for team_name, team in self.teams.items():
            self.logger.info(f"Stopping team: {team_name}")
            # TODO: Implement proper team shutdown when available
            
        # Close integrations
        if self.n8n_client:
            await self.n8n_client.close()
            
        if self.mcp_client:
            await self.mcp_client.close()
            
        self.logger.info("Platform stopped")
        
    def get_team(self, team_name: str) -> Optional[Team]:
        """Get a specific team by name"""
        return self.teams.get(team_name)
        
    def get_status(self) -> Dict:
        """Get platform status information"""
        return {
            "mode": self.mode,
            "running": self.running,
            "components_initialized": self.components_initialized,
            "teams": list(self.teams.keys()),
            "integrations": {
                "n8n": self.n8n_client is not None,
                "mcp": self.mcp_client is not None
            }
        }