"""
Knowledge Injector

Dynamic knowledge injection system for real-time avatar knowledge updates.
Supports various knowledge sources and automatic content processing.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import aiohttp
from pathlib import Path

from agents.avatar.avatar_knowledge_base import AvatarKnowledgeBase


class KnowledgeSource(Enum):
    """Knowledge source types"""
    WEB_SCRAPING = "web_scraping"
    RSS_FEED = "rss_feed"
    API_ENDPOINT = "api_endpoint"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    MANUAL = "manual"
    WEBHOOK = "webhook"


@dataclass
class KnowledgeInjectionJob:
    """Knowledge injection job definition"""
    job_id: str
    avatar_id: str
    source_type: KnowledgeSource
    source_config: Dict[str, Any]
    processing_config: Dict[str, Any]
    schedule: Optional[str] = None  # cron-like schedule
    category: str = "injected"
    tags: List[str] = None
    priority: int = 1
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: str = "inactive"  # inactive, running, completed, error
    error_count: int = 0
    success_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class KnowledgeProcessor:
    """Base knowledge processor"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process(self, raw_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process raw content into knowledge items"""
        return [{
            'content': raw_content,
            'category': metadata.get('category', 'general'),
            'tags': metadata.get('tags', []),
            'priority': metadata.get('priority', 1),
            'context': metadata
        }]


class TextChunkProcessor(KnowledgeProcessor):
    """Processor that chunks text into smaller pieces"""
    
    async def process(self, raw_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunk_size = self.config.get('chunk_size', 500)
        overlap = self.config.get('overlap', 50)
        
        chunks = []
        start = 0
        
        while start < len(raw_content):
            end = min(start + chunk_size, len(raw_content))
            
            # Try to break at sentence boundary
            if end < len(raw_content):
                last_period = raw_content.rfind('.', start, end)
                if last_period > start + chunk_size // 2:
                    end = last_period + 1
            
            chunk = raw_content[start:end].strip()
            if chunk:
                chunks.append({
                    'content': chunk,
                    'category': metadata.get('category', 'general'),
                    'tags': metadata.get('tags', []) + ['chunk'],
                    'priority': metadata.get('priority', 1),
                    'context': {**metadata, 'chunk_index': len(chunks), 'total_chunks': 'unknown'}
                })
            
            start = max(end - overlap, start + 1)
        
        # Update total chunks
        for chunk in chunks:
            chunk['context']['total_chunks'] = len(chunks)
        
        return chunks


class SummaryProcessor(KnowledgeProcessor):
    """Processor that creates summaries of content"""
    
    async def process(self, raw_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simple extractive summary (first sentences)
        sentences = raw_content.split('. ')
        summary_length = self.config.get('summary_sentences', 3)
        
        summary = '. '.join(sentences[:summary_length])
        if not summary.endswith('.'):
            summary += '.'
        
        return [{
            'content': summary,
            'category': metadata.get('category', 'summary'),
            'tags': metadata.get('tags', []) + ['summary'],
            'priority': metadata.get('priority', 2),  # Summaries get higher priority
            'context': {**metadata, 'is_summary': True, 'original_length': len(raw_content)}
        }]


class KnowledgeInjector:
    """
    Dynamic Knowledge Injection System
    
    Features:
    - Multiple knowledge sources
    - Scheduled injection jobs
    - Content processing pipelines
    - Real-time injection via webhooks
    - Job monitoring and management
    - Error handling and retry logic
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Job management
        self.injection_jobs: Dict[str, KnowledgeInjectionJob] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        
        # Avatar knowledge bases
        self.knowledge_bases: Dict[str, AvatarKnowledgeBase] = {}
        
        # Processors
        self.processors = {
            'text_chunk': TextChunkProcessor,
            'summary': SummaryProcessor,
            'default': KnowledgeProcessor
        }
        
        # HTTP session for web requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Scheduling
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        await self.start_scheduler()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_scheduler()
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session and cleanup"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def register_knowledge_base(self, avatar_id: str, knowledge_base: AvatarKnowledgeBase):
        """Register avatar knowledge base"""
        self.knowledge_bases[avatar_id] = knowledge_base
        self.logger.info(f"Registered knowledge base for avatar {avatar_id}")
    
    def unregister_knowledge_base(self, avatar_id: str):
        """Unregister avatar knowledge base"""
        if avatar_id in self.knowledge_bases:
            del self.knowledge_bases[avatar_id]
            self.logger.info(f"Unregistered knowledge base for avatar {avatar_id}")
    
    async def create_injection_job(self, job_id: str, avatar_id: str,
                                 source_type: KnowledgeSource,
                                 source_config: Dict[str, Any],
                                 processing_config: Optional[Dict[str, Any]] = None,
                                 schedule: Optional[str] = None,
                                 **kwargs) -> bool:
        """Create new knowledge injection job"""
        
        if job_id in self.injection_jobs:
            self.logger.error(f"Job {job_id} already exists")
            return False
        
        if avatar_id not in self.knowledge_bases:
            self.logger.error(f"Knowledge base for avatar {avatar_id} not registered")
            return False
        
        try:
            job = KnowledgeInjectionJob(
                job_id=job_id,
                avatar_id=avatar_id,
                source_type=source_type,
                source_config=source_config,
                processing_config=processing_config or {},
                schedule=schedule,
                **kwargs
            )
            
            self.injection_jobs[job_id] = job
            self.logger.info(f"Created injection job {job_id} for avatar {avatar_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create injection job {job_id}: {e}")
            return False
    
    async def run_injection_job(self, job_id: str) -> bool:
        """Run specific injection job"""
        
        if job_id not in self.injection_jobs:
            self.logger.error(f"Job {job_id} not found")
            return False
        
        job = self.injection_jobs[job_id]
        
        if not job.enabled:
            self.logger.warning(f"Job {job_id} is disabled")
            return False
        
        if job_id in self.running_jobs:
            self.logger.warning(f"Job {job_id} is already running")
            return False
        
        try:
            # Create and start job task
            task = asyncio.create_task(self._execute_job(job))
            self.running_jobs[job_id] = task
            
            # Wait for completion
            result = await task
            
            # Cleanup
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run job {job_id}: {e}")
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            return False
    
    async def _execute_job(self, job: KnowledgeInjectionJob) -> bool:
        """Execute injection job"""
        
        job.status = 'running'
        job.last_run = datetime.now()
        
        try:
            # Fetch content from source
            raw_content, metadata = await self._fetch_content(job)
            
            if not raw_content:
                self.logger.warning(f"No content fetched for job {job.job_id}")
                job.status = 'completed'
                return True
            
            # Process content
            processed_items = await self._process_content(raw_content, metadata, job)
            
            # Inject into knowledge base
            knowledge_base = self.knowledge_bases[job.avatar_id]
            injected_count = 0
            
            for item in processed_items:
                knowledge_id = await knowledge_base.add_knowledge(
                    content=item['content'],
                    category=item['category'],
                    tags=item['tags'],
                    priority=item['priority'],
                    context=item.get('context'),
                    ttl_hours=job.processing_config.get('ttl_hours')
                )
                
                if knowledge_id:
                    injected_count += 1
            
            # Update job status
            job.status = 'completed'
            job.success_count += 1
            
            self.logger.info(f"Job {job.job_id} completed: injected {injected_count} items")
            return True
            
        except Exception as e:
            job.status = 'error'
            job.error_count += 1
            self.logger.error(f"Job {job.job_id} failed: {e}")
            return False
    
    async def _fetch_content(self, job: KnowledgeInjectionJob) -> tuple[str, Dict[str, Any]]:
        """Fetch content from source"""
        
        source_type = job.source_type
        config = job.source_config
        
        if source_type == KnowledgeSource.WEB_SCRAPING:
            return await self._fetch_web_content(config)
        elif source_type == KnowledgeSource.RSS_FEED:
            return await self._fetch_rss_content(config)
        elif source_type == KnowledgeSource.API_ENDPOINT:
            return await self._fetch_api_content(config)
        elif source_type == KnowledgeSource.FILE_SYSTEM:
            return await self._fetch_file_content(config)
        elif source_type == KnowledgeSource.MANUAL:
            return config.get('content', ''), config.get('metadata', {})
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def _fetch_web_content(self, config: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Fetch content from web URL"""
        url = config['url']
        
        await self._ensure_session()
        
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                
                # Simple HTML tag removal (basic)
                if config.get('remove_html', True):
                    import re
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                
                metadata = {
                    'source_url': url,
                    'fetch_time': datetime.now().isoformat(),
                    'content_type': response.headers.get('content-type', ''),
                    'status_code': response.status
                }
                
                return content, metadata
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")
    
    async def _fetch_rss_content(self, config: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Fetch content from RSS feed"""
        # Simple RSS parsing - in production, use feedparser
        url = config['url']
        
        await self._ensure_session()
        
        async with self.session.get(url) as response:
            if response.status == 200:
                rss_content = await response.text()
                
                # Extract items (very basic RSS parsing)
                import re
                items = re.findall(r'<item>(.*?)</item>', rss_content, re.DOTALL)
                
                combined_content = []
                for item in items[:config.get('max_items', 10)]:
                    title_match = re.search(r'<title>(.*?)</title>', item)
                    desc_match = re.search(r'<description>(.*?)</description>', item)
                    
                    if title_match:
                        combined_content.append(f"Title: {title_match.group(1)}")
                    if desc_match:
                        combined_content.append(f"Description: {desc_match.group(1)}")
                
                content = '\n\n'.join(combined_content)
                metadata = {
                    'source_url': url,
                    'fetch_time': datetime.now().isoformat(),
                    'item_count': len(items),
                    'source_type': 'rss'
                }
                
                return content, metadata
            else:
                raise Exception(f"HTTP {response.status}: Failed to fetch RSS")
    
    async def _fetch_api_content(self, config: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Fetch content from API endpoint"""
        url = config['url']
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        params = config.get('params', {})
        
        await self._ensure_session()
        
        async with self.session.request(method, url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                # Extract content based on configuration
                content_field = config.get('content_field', 'content')
                if isinstance(data, dict):
                    content = str(data.get(content_field, data))
                elif isinstance(data, list):
                    content = '\n'.join(str(item.get(content_field, item)) for item in data)
                else:
                    content = str(data)
                
                metadata = {
                    'source_url': url,
                    'fetch_time': datetime.now().isoformat(),
                    'api_response': data if config.get('include_raw_response') else None
                }
                
                return content, metadata
            else:
                raise Exception(f"API error {response.status}: {await response.text()}")
    
    async def _fetch_file_content(self, config: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Fetch content from file system"""
        file_path = Path(config['path'])
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding=config.get('encoding', 'utf-8'))
        
        metadata = {
            'source_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'fetch_time': datetime.now().isoformat()
        }
        
        return content, metadata
    
    async def _process_content(self, raw_content: str, metadata: Dict[str, Any],
                             job: KnowledgeInjectionJob) -> List[Dict[str, Any]]:
        """Process raw content using configured processors"""
        
        processing_config = job.processing_config
        processor_type = processing_config.get('processor', 'default')
        
        # Get processor class
        processor_class = self.processors.get(processor_type, KnowledgeProcessor)
        processor = processor_class(processing_config)
        
        # Add job metadata
        enhanced_metadata = {
            **metadata,
            'category': job.category,
            'tags': job.tags,
            'priority': job.priority,
            'job_id': job.job_id,
            'avatar_id': job.avatar_id,
            'injection_time': datetime.now().isoformat()
        }
        
        # Process content
        return await processor.process(raw_content, enhanced_metadata)
    
    async def inject_manual_knowledge(self, avatar_id: str, content: str,
                                    category: str = "manual",
                                    tags: Optional[List[str]] = None,
                                    priority: int = 1) -> Optional[str]:
        """Manually inject knowledge"""
        
        if avatar_id not in self.knowledge_bases:
            self.logger.error(f"Knowledge base for avatar {avatar_id} not registered")
            return None
        
        knowledge_base = self.knowledge_bases[avatar_id]
        
        return await knowledge_base.add_knowledge(
            content=content,
            category=category,
            tags=tags or [],
            priority=priority,
            context={
                'injection_type': 'manual',
                'injection_time': datetime.now().isoformat()
            }
        )
    
    async def start_scheduler(self):
        """Start job scheduler"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Knowledge injection scheduler started")
    
    async def stop_scheduler(self):
        """Stop job scheduler"""
        self.scheduler_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
            self.scheduler_task = None
        
        # Cancel running jobs
        for job_id, task in self.running_jobs.items():
            task.cancel()
        
        self.running_jobs.clear()
        self.logger.info("Knowledge injection scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_running:
            try:
                await self._check_scheduled_jobs()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_jobs(self):
        """Check and run scheduled jobs"""
        now = datetime.now()
        
        for job in self.injection_jobs.values():
            if not job.enabled or not job.schedule:
                continue
            
            if job_id in self.running_jobs:
                continue  # Already running
            
            # Simple interval-based scheduling (extend for cron-like)
            if job.schedule.startswith('interval:'):
                interval_minutes = int(job.schedule.split(':')[1])
                
                if job.last_run is None:
                    should_run = True
                else:
                    next_run = job.last_run + timedelta(minutes=interval_minutes)
                    should_run = now >= next_run
                
                if should_run:
                    asyncio.create_task(self.run_injection_job(job.job_id))
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        if job_id not in self.injection_jobs:
            return None
        
        job = self.injection_jobs[job_id]
        return {
            'job_id': job.job_id,
            'avatar_id': job.avatar_id,
            'status': job.status,
            'last_run': job.last_run.isoformat() if job.last_run else None,
            'success_count': job.success_count,
            'error_count': job.error_count,
            'enabled': job.enabled,
            'source_type': job.source_type.value,
            'is_running': job_id in self.running_jobs
        }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all job statuses"""
        return [self.get_job_status(job_id) for job_id in self.injection_jobs.keys()]
    
    async def enable_job(self, job_id: str) -> bool:
        """Enable injection job"""
        if job_id in self.injection_jobs:
            self.injection_jobs[job_id].enabled = True
            return True
        return False
    
    async def disable_job(self, job_id: str) -> bool:
        """Disable injection job"""
        if job_id in self.injection_jobs:
            self.injection_jobs[job_id].enabled = False
            return True
        return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete injection job"""
        if job_id in self.running_jobs:
            self.running_jobs[job_id].cancel()
            del self.running_jobs[job_id]
        
        if job_id in self.injection_jobs:
            del self.injection_jobs[job_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get injection statistics"""
        total_jobs = len(self.injection_jobs)
        enabled_jobs = sum(1 for job in self.injection_jobs.values() if job.enabled)
        running_jobs = len(self.running_jobs)
        
        return {
            'total_jobs': total_jobs,
            'enabled_jobs': enabled_jobs,
            'running_jobs': running_jobs,
            'scheduler_running': self.scheduler_running,
            'registered_avatars': len(self.knowledge_bases),
            'available_processors': list(self.processors.keys())
        }