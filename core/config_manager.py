"""
Configuration Manager for the AI Avatar Platform
"""
import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from copy import deepcopy


@dataclass
class LLMConfig:
    """LLM configuration structure"""
    api_type: str = "openai"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o"
    timeout: int = 300
    proxy: Optional[str] = None
    pricing_plan: Optional[str] = None


@dataclass
class AvatarConfig:
    """Avatar configuration structure"""
    api_endpoint: str = "http://localhost:8000/speak"
    default_language: str = "Chinese"
    emotion_mappings: Dict[str, str] = None
    
    def __post_init__(self):
        if self.emotion_mappings is None:
            self.emotion_mappings = {
                "goal": "excited",
                "card": "serious", 
                "substitution": "neutral",
                "save": "surprised",
                "halftime": "neutral",
                "tactical": "analytical",
                "stat": "informative",
                "transition": "friendly",
                "penalty": "intense"
            }


@dataclass
class N8nConfig:
    """n8n workflow configuration"""
    webhook_url: str = "http://localhost:5678/webhook/match"
    api_url: str = "http://localhost:5678/api/v1"
    api_key: Optional[str] = None
    event_types: List[str] = None
    
    def __post_init__(self):
        if self.event_types is None:
            self.event_types = [
                "goal", "card", "substitution", "save", "halftime",
                "tactical", "stat", "transition", "penalty"
            ]


@dataclass
class McpConfig:
    """MCP server configuration"""
    server_url: str = "http://localhost:8080"
    tools: List[str] = None
    timeout: int = 30
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = ["process_match_event", "trigger_avatar"]


class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_path: str = "config/config2.yaml"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self._config_cache = {}
        self._watchers = []
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file with validation and defaults"""
        try:
            config = self._load_yaml_config()
            validated_config = self._validate_and_set_defaults(config)
            self._config_cache = validated_config
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return validated_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
            
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
            
    def _validate_and_set_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and set defaults"""
        validated = deepcopy(config)
        
        # LLM configuration
        if "llm" in validated:
            llm_config = LLMConfig(**validated["llm"])
            validated["llm"] = asdict(llm_config)
        else:
            validated["llm"] = asdict(LLMConfig())
            
        # Avatar configuration  
        if "avatar" in validated:
            avatar_config = AvatarConfig(**validated["avatar"])
            validated["avatar"] = asdict(avatar_config)
        else:
            validated["avatar"] = asdict(AvatarConfig())
            
        # n8n configuration
        if "n8n" in validated:
            n8n_config = N8nConfig(**validated["n8n"])
            validated["n8n"] = asdict(n8n_config)
        else:
            validated["n8n"] = asdict(N8nConfig())
            
        # MCP configuration
        if "mcp" in validated:
            mcp_config = McpConfig(**validated["mcp"])
            validated["mcp"] = asdict(mcp_config)
        else:
            validated["mcp"] = asdict(McpConfig())
            
        # Environment variable substitution
        validated = self._substitute_env_vars(validated)
        
        return validated
        
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace environment variable placeholders in config"""
        def _substitute_recursive(obj):
            if isinstance(obj, dict):
                return {k: _substitute_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_substitute_recursive(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                default_value = ""
                if ":" in env_var:
                    env_var, default_value = env_var.split(":", 1)
                return os.getenv(env_var, default_value)
            else:
                return obj
                
        return _substitute_recursive(config)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        if not self._config_cache:
            self.load_config()
            
        keys = key.split('.')
        value = self._config_cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)"""
        if not self._config_cache:
            self.load_config()
            
        keys = key.split('.')
        config = self._config_cache
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        
        # Notify watchers
        self._notify_watchers(key, value)
        
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        path = Path(config_path) if config_path else self.config_path
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_cache, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
            
    def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from file"""
        self.logger.info("Reloading configuration...")
        return self.load_config()
        
    def get_llm_config(self, role: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for specific role or default"""
        if role and "roles" in self._config_cache:
            for role_config in self._config_cache["roles"]:
                if role_config.get("role") == role and "llm" in role_config:
                    return role_config["llm"]
                    
        return self.get("llm", {})
        
    def get_avatar_config(self) -> Dict[str, Any]:
        """Get avatar configuration"""
        return self.get("avatar", {})
        
    def get_n8n_config(self) -> Dict[str, Any]:
        """Get n8n configuration"""
        return self.get("n8n", {})
        
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration"""
        return self.get("mcp", {})
        
    def add_watcher(self, callback) -> None:
        """Add configuration change watcher"""
        self._watchers.append(callback)
        
    def remove_watcher(self, callback) -> None:
        """Remove configuration change watcher"""
        if callback in self._watchers:
            self._watchers.remove(callback)
            
    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify all watchers of configuration changes"""
        for watcher in self._watchers:
            try:
                watcher(key, value)
            except Exception as e:
                self.logger.error(f"Configuration watcher failed: {e}")
                
    def export_config(self, format: str = "yaml") -> str:
        """Export configuration in specified format"""
        if format.lower() == "json":
            return json.dumps(self._config_cache, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump(self._config_cache, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def validate_config(self) -> List[str]:
        """Validate current configuration and return list of issues"""
        issues = []
        
        # Check required fields
        required_fields = ["llm.api_key", "avatar.api_endpoint"]
        for field in required_fields:
            value = self.get(field)
            if not value or value == "YOUR_API_KEY":
                issues.append(f"Missing or invalid value for: {field}")
                
        # Check URL formats
        url_fields = ["avatar.api_endpoint", "n8n.webhook_url", "mcp.server_url"]
        for field in url_fields:
            value = self.get(field)
            if value and not (value.startswith("http://") or value.startswith("https://")):
                issues.append(f"Invalid URL format for: {field}")
                
        return issues