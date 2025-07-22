"""
Event Dispatcher for routing events to appropriate handlers
"""
import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import json
from collections import defaultdict


class EventDispatcher:
    """Routes events to appropriate handlers and workflows"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Event handlers by event type
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Event history for debugging
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # Event statistics
        self.stats = {
            "total_events": 0,
            "events_by_type": defaultdict(int),
            "handler_errors": 0,
            "last_event_time": None
        }
        
    def register_handler(self, event_type: str, handler: Callable, priority: int = 0) -> None:
        """Register an event handler for specific event type"""
        # Store handler with priority for sorting
        handler_info = {
            "handler": handler,
            "priority": priority,
            "registered_at": datetime.now().isoformat()
        }
        
        self.handlers[event_type].append(handler_info)
        
        # Sort handlers by priority (higher priority first)
        self.handlers[event_type].sort(key=lambda x: x["priority"], reverse=True)
        
        self.logger.info(f"Registered handler for event type '{event_type}' with priority {priority}")
        
    def unregister_handler(self, event_type: str, handler: Callable) -> bool:
        """Unregister an event handler"""
        if event_type in self.handlers:
            original_count = len(self.handlers[event_type])
            self.handlers[event_type] = [
                h for h in self.handlers[event_type] 
                if h["handler"] != handler
            ]
            
            removed = original_count - len(self.handlers[event_type])
            if removed > 0:
                self.logger.info(f"Unregistered {removed} handler(s) for event type '{event_type}'")
                return True
                
        return False
        
    async def dispatch_event(self, event_type: str, event_data: Dict[str, Any], 
                           source: str = "unknown") -> List[Dict[str, Any]]:
        """Dispatch event to all registered handlers"""
        try:
            # Record event
            event_record = {
                "type": event_type,
                "data": event_data,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "event_id": f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            }
            
            # Update statistics
            self.stats["total_events"] += 1
            self.stats["events_by_type"][event_type] += 1
            self.stats["last_event_time"] = event_record["timestamp"]
            
            # Add to history
            self.event_history.append(event_record)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
                
            self.logger.info(f"Dispatching event '{event_type}' from '{source}'")
            
            # Get handlers for this event type
            handlers = self.handlers.get(event_type, [])
            if not handlers:
                self.logger.warning(f"No handlers registered for event type '{event_type}'")
                return []
                
            # Execute all handlers
            results = []
            for handler_info in handlers:
                try:
                    handler = handler_info["handler"]
                    
                    # Call handler (support both sync and async)
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(event_type, event_data, event_record)
                    else:
                        result = handler(event_type, event_data, event_record)
                        
                    results.append({
                        "handler": handler.__name__,
                        "status": "success",
                        "result": result,
                        "priority": handler_info["priority"]
                    })
                    
                except Exception as e:
                    self.stats["handler_errors"] += 1
                    self.logger.error(f"Handler {handler.__name__} failed for event '{event_type}': {e}")
                    
                    results.append({
                        "handler": handler.__name__,
                        "status": "error",
                        "error": str(e),
                        "priority": handler_info["priority"]
                    })
                    
            self.logger.info(f"Event '{event_type}' processed by {len(results)} handlers")
            return results
            
        except Exception as e:
            self.logger.error(f"Event dispatch failed for '{event_type}': {e}")
            raise
            
    async def dispatch_batch(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Dispatch multiple events in batch"""
        results = {}
        
        for event in events:
            event_type = event.get("type", "unknown")
            event_data = event.get("data", {})
            source = event.get("source", "batch")
            
            try:
                event_results = await self.dispatch_event(event_type, event_data, source)
                results[event.get("id", event_type)] = event_results
                
            except Exception as e:
                self.logger.error(f"Batch event dispatch failed for '{event_type}': {e}")
                results[event.get("id", event_type)] = [{
                    "status": "error",
                    "error": str(e)
                }]
                
        return results
        
    def register_wildcard_handler(self, handler: Callable, priority: int = 0) -> None:
        """Register handler that receives all events"""
        self.register_handler("*", handler, priority)
        
    async def _dispatch_to_wildcard_handlers(self, event_type: str, event_data: Dict[str, Any], 
                                           event_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Dispatch to wildcard handlers"""
        wildcard_handlers = self.handlers.get("*", [])
        results = []
        
        for handler_info in wildcard_handlers:
            try:
                handler = handler_info["handler"]
                
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_type, event_data, event_record)
                else:
                    result = handler(event_type, event_data, event_record)
                    
                results.append({
                    "handler": f"{handler.__name__} (wildcard)",
                    "status": "success", 
                    "result": result,
                    "priority": handler_info["priority"]
                })
                
            except Exception as e:
                self.logger.error(f"Wildcard handler {handler.__name__} failed: {e}")
                results.append({
                    "handler": f"{handler.__name__} (wildcard)",
                    "status": "error",
                    "error": str(e),
                    "priority": handler_info["priority"]
                })
                
        return results
        
    def get_event_history(self, event_type: Optional[str] = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self.event_history if e["type"] == event_type]
            return filtered[-limit:]
        else:
            return self.event_history[-limit:]
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get event dispatcher statistics"""
        return {
            "total_events": self.stats["total_events"],
            "events_by_type": dict(self.stats["events_by_type"]),
            "handler_errors": self.stats["handler_errors"],
            "last_event_time": self.stats["last_event_time"],
            "registered_handlers": {
                event_type: len(handlers) 
                for event_type, handlers in self.handlers.items()
            }
        }
        
    def clear_history(self) -> None:
        """Clear event history"""
        self.event_history.clear()
        self.logger.info("Event history cleared")
        
    def clear_statistics(self) -> None:
        """Clear event statistics"""
        self.stats = {
            "total_events": 0,
            "events_by_type": defaultdict(int),
            "handler_errors": 0,
            "last_event_time": None
        }
        self.logger.info("Event statistics cleared")