"""
MCP (Model Context Protocol) Client for tool integration
"""
import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin
from datetime import datetime


class McpClient:
    """Client for MCP (Model Context Protocol) server integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.server_url = config.get("server_url", "http://localhost:8080")
        self.tools = config.get("tools", [])
        self.timeout = config.get("timeout", 30)
        
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize the MCP client"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"Content-Type": "application/json"}
            )
            
            # Test connection and load available tools
            await self.test_connection()
            await self.load_available_tools()
            
            self.connected = True
            self.logger.info("MCP client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP client: {e}")
            raise
            
    async def test_connection(self) -> bool:
        """Test connection to MCP server"""
        try:
            if not self.session:
                return False
                
            # Try to get server info
            url = urljoin(self.server_url, "/health")
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.logger.info("MCP server connection successful")
                    return True
                else:
                    self.logger.warning(f"MCP server returned status {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.warning(f"MCP connection test failed: {e}")
            return False
            
    async def load_available_tools(self) -> None:
        """Load available tools from MCP server"""
        try:
            if not self.session:
                return
                
            url = urljoin(self.server_url, "/tools")
            async with self.session.get(url) as response:
                if response.status == 200:
                    tools_data = await response.json()
                    self.available_tools = {
                        tool["name"]: tool 
                        for tool in tools_data.get("tools", [])
                    }
                    self.logger.info(f"Loaded {len(self.available_tools)} available tools")
                else:
                    self.logger.warning(f"Failed to load tools: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load available tools: {e}")
            
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if not self.session:
            raise RuntimeError("MCP client not initialized")
            
        try:
            # Check if tool is available
            if tool_name not in self.available_tools:
                raise ValueError(f"Tool '{tool_name}' not available. Available tools: {list(self.available_tools.keys())}")
                
            # Prepare tool call request
            request_data = {
                "tool": tool_name,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
            
            url = urljoin(self.server_url, f"/tools/{tool_name}/call")
            
            async with self.session.post(url, json=request_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.logger.info(f"MCP tool '{tool_name}' called successfully")
                    return {
                        "status": "success",
                        "tool": tool_name,
                        "result": response_data.get("result"),
                        "execution_time": response_data.get("execution_time")
                    }
                else:
                    self.logger.error(f"MCP tool call failed: {response_data}")
                    return {
                        "status": "error",
                        "tool": tool_name,
                        "error": response_data.get("error", f"HTTP {response.status}")
                    }
                    
        except Exception as e:
            self.logger.error(f"MCP tool call failed: {e}")
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e)
            }
            
    async def process_match_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a match event using MCP tools"""
        try:
            parameters = {
                "event": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("process_match_event", parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to process match event: {e}")
            return {"status": "error", "message": str(e)}
            
    async def trigger_avatar(self, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger avatar action using MCP tools"""
        try:
            parameters = {
                "avatar_data": avatar_data,
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("trigger_avatar", parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger avatar: {e}")
            return {"status": "error", "message": str(e)}
            
    async def import_content(self, source: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Import content from external source via MCP"""
        try:
            tool_parameters = {
                "source": source,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("import_content", tool_parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to import content: {e}")
            return {"status": "error", "message": str(e)}
            
    async def generate_content(self, prompt: str, content_type: str = "text", 
                             parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate content using MCP tools"""
        try:
            tool_parameters = {
                "prompt": prompt,
                "content_type": content_type,
                "parameters": parameters or {},
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("generate_content", tool_parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to generate content: {e}")
            return {"status": "error", "message": str(e)}
            
    async def web_search(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform web search using MCP tools"""
        try:
            tool_parameters = {
                "query": query,
                "parameters": parameters or {},
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("web_search", tool_parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to perform web search: {e}")
            return {"status": "error", "message": str(e)}
            
    async def crawl_website(self, url: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crawl website using MCP tools"""
        try:
            tool_parameters = {
                "url": url,
                "parameters": parameters or {},
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.call_tool("crawl_website", tool_parameters)
            
        except Exception as e:
            self.logger.error(f"Failed to crawl website: {e}")
            return {"status": "error", "message": str(e)}
            
    async def batch_call_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple tool calls in batch"""
        results = []
        
        for call in tool_calls:
            tool_name = call.get("tool")
            parameters = call.get("parameters", {})
            
            if not tool_name:
                results.append({"status": "error", "error": "Missing tool name"})
                continue
                
            try:
                result = await self.call_tool(tool_name, parameters)
                results.append(result)
                
            except Exception as e:
                results.append({
                    "status": "error",
                    "tool": tool_name,
                    "error": str(e)
                })
                
        return results
        
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available tools"""
        return self.available_tools.copy()
        
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if specific tool is available"""
        return tool_name in self.available_tools
        
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about specific tool"""
        return self.available_tools.get(tool_name)
        
    async def reload_tools(self) -> None:
        """Reload available tools from server"""
        await self.load_available_tools()
        
    async def close(self) -> None:
        """Close the MCP client"""
        if self.session:
            await self.session.close()
            self.session = None
            
        self.connected = False
        self.logger.info("MCP client closed")
        
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "connected": self.connected,
            "server_url": self.server_url,
            "available_tools": list(self.available_tools.keys()),
            "configured_tools": self.tools,
            "timeout": self.timeout
        }