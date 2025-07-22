"""
Avatar Monitor

Performance monitoring and analytics system for avatars.
Tracks metrics, health, usage patterns, and provides alerts.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

from agents.avatar.base_avatar_agent import BaseAvatarAgent


class MetricType(Enum):
    """Types of metrics to track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """Individual metric value"""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'metadata': self.metadata
        }


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    avatar_id: str
    level: AlertLevel
    message: str
    metric_name: Optional[str]
    threshold: Optional[float]
    current_value: Optional[float]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'avatar_id': self.avatar_id,
            'level': self.level.value,
            'message': self.message,
            'metric_name': self.metric_name,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged': self.acknowledged
        }


class MetricCollector:
    """Collects and stores metrics for an avatar"""
    
    def __init__(self, avatar_id: str, config: Optional[Dict] = None):
        self.avatar_id = avatar_id
        self.config = config or {}
        self.logger = logging.getLogger(f"MetricCollector_{avatar_id}")
        
        # Metric storage
        self.metrics: Dict[str, List[MetricValue]] = defaultdict(list)
        self.metric_types: Dict[str, MetricType] = {}
        
        # Configuration
        self.max_history_size = self.config.get('max_history_size', 1000)
        self.retention_hours = self.config.get('retention_hours', 24)
        
        # Performance optimization
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(hours=1)
    
    def record_metric(self, name: str, value: float, 
                     metric_type: MetricType = MetricType.GAUGE,
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a metric value"""
        
        metric_value = MetricValue(
            timestamp=datetime.now(),
            value=value,
            metadata=metadata
        )
        
        self.metrics[name].append(metric_value)
        self.metric_types[name] = metric_type
        
        # Cleanup old data if needed
        self._cleanup_if_needed()
        
        # Limit history size
        if len(self.metrics[name]) > self.max_history_size:
            self.metrics[name] = self.metrics[name][-self.max_history_size:]
    
    def get_metric_values(self, name: str, 
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> List[MetricValue]:
        """Get metric values with optional filtering"""
        
        values = self.metrics.get(name, [])
        
        if since:
            values = [v for v in values if v.timestamp >= since]
        
        if limit:
            values = values[-limit:]
        
        return values
    
    def get_current_value(self, name: str) -> Optional[float]:
        """Get most recent metric value"""
        values = self.metrics.get(name, [])
        return values[-1].value if values else None
    
    def calculate_rate(self, name: str, time_window_minutes: int = 5) -> float:
        """Calculate rate of change for a metric"""
        since = datetime.now() - timedelta(minutes=time_window_minutes)
        values = self.get_metric_values(name, since=since)
        
        if len(values) < 2:
            return 0.0
        
        time_diff = (values[-1].timestamp - values[0].timestamp).total_seconds()
        if time_diff == 0:
            return 0.0
        
        value_diff = values[-1].value - values[0].value
        return value_diff / (time_diff / 60)  # per minute
    
    def calculate_average(self, name: str, time_window_minutes: int = 5) -> float:
        """Calculate average value over time window"""
        since = datetime.now() - timedelta(minutes=time_window_minutes)
        values = self.get_metric_values(name, since=since)
        
        if not values:
            return 0.0
        
        return statistics.mean(v.value for v in values)
    
    def calculate_percentile(self, name: str, percentile: float,
                           time_window_minutes: int = 5) -> float:
        """Calculate percentile value over time window"""
        since = datetime.now() - timedelta(minutes=time_window_minutes)
        values = self.get_metric_values(name, since=since)
        
        if not values:
            return 0.0
        
        sorted_values = sorted(v.value for v in values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _cleanup_if_needed(self):
        """Cleanup old metrics if needed"""
        now = datetime.now()
        
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = now - timedelta(hours=self.retention_hours)
        
        for name in list(self.metrics.keys()):
            original_count = len(self.metrics[name])
            self.metrics[name] = [
                v for v in self.metrics[name] 
                if v.timestamp > cutoff_time
            ]
            
            removed_count = original_count - len(self.metrics[name])
            if removed_count > 0:
                self.logger.debug(f"Cleaned up {removed_count} old values for {name}")
        
        self.last_cleanup = now
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        
        for name, values in self.metrics.items():
            if not values:
                continue
            
            current = values[-1].value
            metric_type = self.metric_types.get(name, MetricType.GAUGE)
            
            summary[name] = {
                'current': current,
                'type': metric_type.value,
                'count': len(values),
                'average_5min': self.calculate_average(name, 5),
                'average_1hour': self.calculate_average(name, 60),
                'rate_5min': self.calculate_rate(name, 5) if metric_type == MetricType.COUNTER else None
            }
        
        return summary


class AvatarMonitor:
    """
    Comprehensive Avatar Monitoring System
    
    Features:
    - Real-time metric collection
    - Health monitoring
    - Performance analytics
    - Alert system
    - Usage pattern analysis
    - Resource utilization tracking
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Avatar tracking
        self.monitored_avatars: Dict[str, BaseAvatarAgent] = {}
        self.metric_collectors: Dict[str, MetricCollector] = {}
        
        # Alerts
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Monitoring configuration
        self.collection_interval = self.config.get('collection_interval_seconds', 30)
        self.health_check_interval = self.config.get('health_check_interval_seconds', 60)
        
        # Monitoring tasks
        self.collection_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
        # Setup default alert rules
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            'high_response_time': {
                'metric': 'avg_response_time',
                'threshold': 5.0,  # 5 seconds
                'comparison': 'greater',
                'level': AlertLevel.WARNING,
                'message': 'High response time detected'
            },
            'low_success_rate': {
                'metric': 'success_rate',
                'threshold': 0.8,  # 80%
                'comparison': 'less',
                'level': AlertLevel.ERROR,
                'message': 'Low success rate detected'
            },
            'high_error_rate': {
                'metric': 'error_rate',
                'threshold': 0.1,  # 10%
                'comparison': 'greater',
                'level': AlertLevel.WARNING,
                'message': 'High error rate detected'
            },
            'memory_usage_high': {
                'metric': 'memory_usage_mb',
                'threshold': 500,  # 500 MB
                'comparison': 'greater',
                'level': AlertLevel.WARNING,
                'message': 'High memory usage detected'
            }
        }
    
    async def start_monitoring(self):
        """Start monitoring system"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start collection task
        self.collection_task = asyncio.create_task(self._collection_loop())
        
        # Start health check task
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.info("Avatar monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        
        # Cancel tasks
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Avatar monitoring stopped")
    
    def register_avatar(self, avatar: BaseAvatarAgent):
        """Register avatar for monitoring"""
        avatar_id = avatar.avatar_id
        
        self.monitored_avatars[avatar_id] = avatar
        self.metric_collectors[avatar_id] = MetricCollector(
            avatar_id, 
            self.config.get('metric_collection', {})
        )
        
        self.logger.info(f"Registered avatar {avatar_id} for monitoring")
    
    def unregister_avatar(self, avatar_id: str):
        """Unregister avatar from monitoring"""
        if avatar_id in self.monitored_avatars:
            del self.monitored_avatars[avatar_id]
        
        if avatar_id in self.metric_collectors:
            del self.metric_collectors[avatar_id]
        
        # Clean up alerts
        avatar_alerts = [alert_id for alert_id, alert in self.alerts.items() 
                        if alert.avatar_id == avatar_id]
        for alert_id in avatar_alerts:
            del self.alerts[alert_id]
        
        self.logger.info(f"Unregistered avatar {avatar_id} from monitoring")
    
    async def _collection_loop(self):
        """Main metrics collection loop"""
        while self.monitoring_active:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _health_check_loop(self):
        """Main health check loop"""
        while self.monitoring_active:
            try:
                await self._check_all_health()
                await self._check_alert_rules()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _collect_all_metrics(self):
        """Collect metrics from all monitored avatars"""
        
        for avatar_id, avatar in self.monitored_avatars.items():
            try:
                await self._collect_avatar_metrics(avatar_id, avatar)
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for {avatar_id}: {e}")
    
    async def _collect_avatar_metrics(self, avatar_id: str, avatar: BaseAvatarAgent):
        """Collect metrics for specific avatar"""
        
        collector = self.metric_collectors[avatar_id]
        
        # Get avatar status
        status = avatar.get_avatar_status()
        
        # Basic metrics
        collector.record_metric('is_active', 1.0 if status['is_active'] else 0.0)
        collector.record_metric('conversation_length', status['conversation_length'])
        collector.record_metric('emotion_intensity', status['emotion_intensity'])
        
        # Interaction metrics
        metrics = status['interaction_metrics']
        collector.record_metric('total_interactions', metrics['total_interactions'], MetricType.COUNTER)
        collector.record_metric('successful_responses', metrics['successful_responses'], MetricType.COUNTER)
        collector.record_metric('failed_responses', metrics['failed_responses'], MetricType.COUNTER)
        collector.record_metric('avg_response_time', metrics['average_response_time'])
        
        # Calculate derived metrics
        total_responses = metrics['successful_responses'] + metrics['failed_responses']
        if total_responses > 0:
            success_rate = metrics['successful_responses'] / total_responses
            error_rate = metrics['failed_responses'] / total_responses
        else:
            success_rate = 1.0
            error_rate = 0.0
        
        collector.record_metric('success_rate', success_rate)
        collector.record_metric('error_rate', error_rate)
        
        # Knowledge base metrics
        kb_stats = status['knowledge_stats']
        collector.record_metric('knowledge_items', kb_stats['total_items'])
        collector.record_metric('knowledge_categories', kb_stats['categories'])
        collector.record_metric('expired_knowledge_items', kb_stats['expired_items'])
        
        # Content generation metrics
        content_stats = status['content_stats']
        collector.record_metric('content_generations', content_stats['total_generations'], MetricType.COUNTER)
        collector.record_metric('avg_content_length', content_stats['average_response_length'])
        
        if content_stats.get('average_rating'):
            collector.record_metric('avg_content_rating', content_stats['average_rating'])
        
        # API client metrics
        api_stats = status['api_stats']
        collector.record_metric('cache_size', api_stats['cache_size'])
        
        # System metrics (if available)
        await self._collect_system_metrics(avatar_id, collector)
    
    async def _collect_system_metrics(self, avatar_id: str, collector: MetricCollector):
        """Collect system-level metrics"""
        try:
            import psutil
            import os
            
            # Memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            collector.record_metric('memory_usage_mb', memory_mb)
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            collector.record_metric('cpu_usage_percent', cpu_percent)
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            self.logger.debug(f"Failed to collect system metrics: {e}")
    
    async def _check_all_health(self):
        """Check health of all monitored avatars"""
        
        for avatar_id, avatar in self.monitored_avatars.items():
            try:
                await self._check_avatar_health(avatar_id, avatar)
            except Exception as e:
                self.logger.error(f"Health check failed for {avatar_id}: {e}")
    
    async def _check_avatar_health(self, avatar_id: str, avatar: BaseAvatarAgent):
        """Check health of specific avatar"""
        
        status = avatar.get_avatar_status()
        collector = self.metric_collectors[avatar_id]
        
        # Health score calculation (0.0 to 1.0)
        health_factors = []
        
        # Activity factor
        health_factors.append(1.0 if status['is_active'] else 0.0)
        
        # Success rate factor
        success_rate = collector.get_current_value('success_rate') or 1.0
        health_factors.append(success_rate)
        
        # Response time factor (inverse relationship)
        avg_response_time = collector.get_current_value('avg_response_time') or 0.0
        response_time_factor = max(0.0, 1.0 - (avg_response_time / 10.0))  # 10s = 0 health
        health_factors.append(response_time_factor)
        
        # Error rate factor (inverse)
        error_rate = collector.get_current_value('error_rate') or 0.0
        error_rate_factor = max(0.0, 1.0 - (error_rate * 5))  # 20% error = 0 health
        health_factors.append(error_rate_factor)
        
        # Calculate overall health
        health_score = sum(health_factors) / len(health_factors)
        collector.record_metric('health_score', health_score)
        
        # Health status
        if health_score >= 0.8:
            health_status = 'healthy'
        elif health_score >= 0.6:
            health_status = 'degraded'
        elif health_score >= 0.3:
            health_status = 'unhealthy'
        else:
            health_status = 'critical'
        
        collector.record_metric('health_status_numeric', {
            'healthy': 3, 'degraded': 2, 'unhealthy': 1, 'critical': 0
        }[health_status])
    
    async def _check_alert_rules(self):
        """Check alert rules for all avatars"""
        
        for avatar_id in self.monitored_avatars.keys():
            collector = self.metric_collectors[avatar_id]
            
            for rule_name, rule in self.alert_rules.items():
                await self._check_alert_rule(avatar_id, rule_name, rule, collector)
    
    async def _check_alert_rule(self, avatar_id: str, rule_name: str,
                              rule: Dict[str, Any], collector: MetricCollector):
        """Check specific alert rule"""
        
        metric_name = rule['metric']
        threshold = rule['threshold']
        comparison = rule['comparison']
        level = rule['level']
        message = rule['message']
        
        current_value = collector.get_current_value(metric_name)
        if current_value is None:
            return
        
        # Check condition
        triggered = False
        if comparison == 'greater' and current_value > threshold:
            triggered = True
        elif comparison == 'less' and current_value < threshold:
            triggered = True
        elif comparison == 'equals' and abs(current_value - threshold) < 0.001:
            triggered = True
        
        alert_id = f"{avatar_id}_{rule_name}"
        
        if triggered:
            # Create or update alert
            if alert_id not in self.alerts:
                await self._create_alert(
                    alert_id=alert_id,
                    avatar_id=avatar_id,
                    level=level,
                    message=f"{message}: {current_value} (threshold: {threshold})",
                    metric_name=metric_name,
                    threshold=threshold,
                    current_value=current_value
                )
        else:
            # Resolve alert if exists
            if alert_id in self.alerts and not self.alerts[alert_id].resolved_at:
                await self._resolve_alert(alert_id)
    
    async def _create_alert(self, alert_id: str, avatar_id: str, level: AlertLevel,
                          message: str, metric_name: Optional[str] = None,
                          threshold: Optional[float] = None,
                          current_value: Optional[float] = None):
        """Create new alert"""
        
        alert = Alert(
            alert_id=alert_id,
            avatar_id=avatar_id,
            level=level,
            message=message,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            created_at=datetime.now()
        )
        
        self.alerts[alert_id] = alert
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
        
        self.logger.warning(f"Alert created: {alert_id} - {message}")
    
    async def _resolve_alert(self, alert_id: str):
        """Resolve existing alert"""
        
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolved_at = datetime.now()
            
            self.logger.info(f"Alert resolved: {alert_id}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_avatar_metrics(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics summary for avatar"""
        if avatar_id not in self.metric_collectors:
            return None
        
        collector = self.metric_collectors[avatar_id]
        return collector.get_all_metrics_summary()
    
    def get_avatar_alerts(self, avatar_id: str,
                         include_resolved: bool = False) -> List[Dict[str, Any]]:
        """Get alerts for specific avatar"""
        
        alerts = []
        for alert in self.alerts.values():
            if alert.avatar_id != avatar_id:
                continue
            
            if not include_resolved and alert.resolved_at:
                continue
            
            alerts.append(alert.to_dict())
        
        return sorted(alerts, key=lambda x: x['created_at'], reverse=True)
    
    def get_all_alerts(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """Get all alerts"""
        
        alerts = []
        for alert in self.alerts.values():
            if not include_resolved and alert.resolved_at:
                continue
            
            alerts.append(alert.to_dict())
        
        return sorted(alerts, key=lambda x: x['created_at'], reverse=True)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        
        active_alerts = sum(1 for alert in self.alerts.values() if not alert.resolved_at)
        resolved_alerts = sum(1 for alert in self.alerts.values() if alert.resolved_at)
        
        return {
            'monitoring_active': self.monitoring_active,
            'monitored_avatars': len(self.monitored_avatars),
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'alert_rules': len(self.alert_rules),
            'collection_interval': self.collection_interval,
            'health_check_interval': self.health_check_interval
        }
    
    async def generate_health_report(self, avatar_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        
        report = {
            'report_time': datetime.now().isoformat(),
            'monitoring_stats': self.get_monitoring_stats(),
            'avatars': {}
        }
        
        avatar_ids = [avatar_id] if avatar_id else list(self.monitored_avatars.keys())
        
        for aid in avatar_ids:
            if aid not in self.monitored_avatars:
                continue
            
            avatar = self.monitored_avatars[aid]
            collector = self.metric_collectors[aid]
            
            report['avatars'][aid] = {
                'status': avatar.get_avatar_status(),
                'metrics': collector.get_all_metrics_summary(),
                'alerts': self.get_avatar_alerts(aid, include_resolved=False),
                'health_trend': [
                    v.to_dict() for v in collector.get_metric_values(
                        'health_score', 
                        since=datetime.now() - timedelta(hours=1)
                    )
                ]
            }
        
        return report