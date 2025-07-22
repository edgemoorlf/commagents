"""
Avatar Knowledge Base

Manages knowledge storage, retrieval, and context awareness for avatars.
Supports dynamic knowledge injection and real-time updates.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class KnowledgeItem:
    """Single knowledge item with metadata"""
    id: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    priority: int = 1  # 1-5, higher is more important
    context: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if knowledge item is expired"""
        return self.expires_at is not None and datetime.now() > self.expires_at


class AvatarKnowledgeBase:
    """
    Knowledge management system for avatars
    
    Features:
    - Category-based organization
    - Tag-based filtering
    - Priority-weighted retrieval
    - Time-based expiration
    - Context-aware matching
    """
    
    def __init__(self, avatar_id: str, config: Optional[Dict] = None):
        self.avatar_id = avatar_id
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{avatar_id}")
        
        # Knowledge storage
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> list of knowledge IDs
        self.tags: Dict[str, List[str]] = {}  # tag -> list of knowledge IDs
        
        # Configuration
        self.max_items = self.config.get('max_knowledge_items', 10000)
        self.default_ttl = self.config.get('default_ttl_hours', 24 * 7)  # 1 week
        self.cleanup_interval = self.config.get('cleanup_interval_seconds', 3600)  # 1 hour
        
        # Start background cleanup
        self._cleanup_task = None
        # Don't start cleanup automatically - let the user start it when ready
    
    def _start_cleanup(self):
        """Start background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup of expired items"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired()
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    async def add_knowledge(self, 
                          content: str,
                          category: str,
                          tags: Optional[List[str]] = None,
                          priority: int = 1,
                          context: Optional[Dict[str, Any]] = None,
                          ttl_hours: Optional[int] = None,
                          knowledge_id: Optional[str] = None) -> str:
        """Add new knowledge item"""
        
        # Generate ID if not provided
        if knowledge_id is None:
            knowledge_id = f"{self.avatar_id}_{datetime.now().timestamp()}"
        
        # Set expiration if TTL provided
        expires_at = None
        if ttl_hours is not None:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
        elif self.default_ttl > 0:
            expires_at = datetime.now() + timedelta(hours=self.default_ttl)
        
        # Create knowledge item
        item = KnowledgeItem(
            id=knowledge_id,
            content=content,
            category=category,
            tags=tags or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            priority=priority,
            context=context,
            expires_at=expires_at
        )
        
        # Store item
        self.knowledge_items[knowledge_id] = item
        
        # Update indexes
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(knowledge_id)
        
        for tag in item.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(knowledge_id)
        
        # Check storage limits
        await self._check_storage_limits()
        
        self.logger.info(f"Added knowledge item {knowledge_id} to category {category}")
        return knowledge_id
    
    async def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Get specific knowledge item by ID"""
        item = self.knowledge_items.get(knowledge_id)
        if item and item.is_expired():
            await self.remove_knowledge(knowledge_id)
            return None
        return item
    
    async def search_knowledge(self,
                             query: str = "",
                             categories: Optional[List[str]] = None,
                             tags: Optional[List[str]] = None,
                             min_priority: int = 1,
                             limit: int = 10,
                             context: Optional[Dict[str, Any]] = None) -> List[KnowledgeItem]:
        """Search knowledge with filters and ranking"""
        
        # Get candidate items
        candidates = []
        
        if categories:
            for category in categories:
                if category in self.categories:
                    candidates.extend(self.categories[category])
        elif tags:
            for tag in tags:
                if tag in self.tags:
                    candidates.extend(self.tags[tag])
        else:
            candidates = list(self.knowledge_items.keys())
        
        # Remove duplicates and filter
        candidates = list(set(candidates))
        results = []
        
        for item_id in candidates:
            item = await self.get_knowledge(item_id)
            if not item:
                continue
                
            # Filter by priority
            if item.priority < min_priority:
                continue
                
            # Filter by query (simple text matching)
            if query and query.lower() not in item.content.lower():
                continue
                
            # Context matching (if both provided)
            if context and item.context:
                # Simple context matching - can be enhanced
                context_match = any(
                    item.context.get(k) == v 
                    for k, v in context.items()
                )
                if not context_match:
                    continue
            
            results.append(item)
        
        # Sort by priority and recency
        results.sort(
            key=lambda x: (x.priority, x.updated_at),
            reverse=True
        )
        
        return results[:limit]
    
    async def update_knowledge(self, 
                             knowledge_id: str,
                             content: Optional[str] = None,
                             category: Optional[str] = None,
                             tags: Optional[List[str]] = None,
                             priority: Optional[int] = None,
                             context: Optional[Dict[str, Any]] = None) -> bool:
        """Update existing knowledge item"""
        
        item = await self.get_knowledge(knowledge_id)
        if not item:
            return False
        
        # Update fields
        if content is not None:
            item.content = content
        if category is not None:
            # Remove from old category
            if item.category in self.categories:
                self.categories[item.category].remove(knowledge_id)
            # Add to new category
            item.category = category
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(knowledge_id)
        if tags is not None:
            # Remove from old tags
            for old_tag in item.tags:
                if old_tag in self.tags:
                    self.tags[old_tag].remove(knowledge_id)
            # Add to new tags
            item.tags = tags
            for tag in tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(knowledge_id)
        if priority is not None:
            item.priority = priority
        if context is not None:
            item.context = context
        
        item.updated_at = datetime.now()
        self.logger.info(f"Updated knowledge item {knowledge_id}")
        return True
    
    async def remove_knowledge(self, knowledge_id: str) -> bool:
        """Remove knowledge item"""
        item = self.knowledge_items.get(knowledge_id)
        if not item:
            return False
        
        # Remove from indexes
        if item.category in self.categories:
            self.categories[item.category].remove(knowledge_id)
            if not self.categories[item.category]:
                del self.categories[item.category]
        
        for tag in item.tags:
            if tag in self.tags:
                self.tags[tag].remove(knowledge_id)
                if not self.tags[tag]:
                    del self.tags[tag]
        
        # Remove item
        del self.knowledge_items[knowledge_id]
        self.logger.info(f"Removed knowledge item {knowledge_id}")
        return True
    
    async def cleanup_expired(self) -> int:
        """Remove expired knowledge items"""
        expired_ids = [
            item_id for item_id, item in self.knowledge_items.items()
            if item.is_expired()
        ]
        
        for item_id in expired_ids:
            await self.remove_knowledge(item_id)
        
        if expired_ids:
            self.logger.info(f"Cleaned up {len(expired_ids)} expired knowledge items")
        
        return len(expired_ids)
    
    async def _check_storage_limits(self):
        """Check and enforce storage limits"""
        if len(self.knowledge_items) > self.max_items:
            # Remove oldest, lowest priority items
            items_to_remove = sorted(
                self.knowledge_items.items(),
                key=lambda x: (x[1].priority, x[1].updated_at)
            )
            
            remove_count = len(self.knowledge_items) - self.max_items
            for item_id, _ in items_to_remove[:remove_count]:
                await self.remove_knowledge(item_id)
            
            self.logger.warning(f"Storage limit exceeded, removed {remove_count} items")
    
    async def get_context_summary(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Get contextual knowledge summary"""
        relevant_items = await self.search_knowledge(
            context=context,
            limit=5,
            min_priority=2
        )
        
        if not relevant_items:
            return "No specific contextual knowledge available."
        
        summary_parts = []
        for item in relevant_items:
            summary_parts.append(f"- {item.content}")
        
        return "Relevant knowledge:\n" + "\n".join(summary_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        now = datetime.now()
        return {
            "total_items": len(self.knowledge_items),
            "categories": len(self.categories),
            "tags": len(self.tags),
            "expired_items": sum(1 for item in self.knowledge_items.values() if item.is_expired()),
            "priority_distribution": {
                str(p): sum(1 for item in self.knowledge_items.values() if item.priority == p)
                for p in range(1, 6)
            },
            "recent_items_24h": sum(
                1 for item in self.knowledge_items.values()
                if (now - item.created_at).total_seconds() < 24 * 3600
            )
        }
    
    async def export_knowledge(self) -> List[Dict[str, Any]]:
        """Export all knowledge as dictionaries"""
        return [item.to_dict() for item in self.knowledge_items.values()]
    
    async def import_knowledge(self, knowledge_data: List[Dict[str, Any]]) -> int:
        """Import knowledge from dictionaries"""
        imported_count = 0
        
        for item_data in knowledge_data:
            try:
                item = KnowledgeItem.from_dict(item_data)
                self.knowledge_items[item.id] = item
                
                # Update indexes
                if item.category not in self.categories:
                    self.categories[item.category] = []
                self.categories[item.category].append(item.id)
                
                for tag in item.tags:
                    if tag not in self.tags:
                        self.tags[tag] = []
                    self.tags[tag].append(item.id)
                
                imported_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to import knowledge item: {e}")
        
        self.logger.info(f"Imported {imported_count} knowledge items")
        return imported_count
    
    async def close(self):
        """Cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Knowledge base closed")