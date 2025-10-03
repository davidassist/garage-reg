"""
Comprehensive Audit and Security Monitoring System
Real-time security event logging, monitoring, and alerting
"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field, asdict
import hashlib
import ipaddress
from urllib.parse import urlparse

import redis.asyncio as redis
import structlog
from fastapi import Request, Response
from pydantic import BaseModel
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = structlog.get_logger(__name__)

class SecurityEventType(Enum):
    """Security event types for audit logging"""
    
    # Authentication Events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGIN_BLOCKED = "auth.login.blocked"
    LOGOUT = "auth.logout"
    TOKEN_CREATED = "auth.token.created"
    TOKEN_EXPIRED = "auth.token.expired"
    TOKEN_REVOKED = "auth.token.revoked"
    
    # Authorization Events
    ACCESS_GRANTED = "authz.access.granted"
    ACCESS_DENIED = "authz.access.denied"
    PERMISSION_CHANGED = "authz.permission.changed"
    ROLE_ASSIGNED = "authz.role.assigned"
    ROLE_REVOKED = "authz.role.revoked"
    
    # Data Access Events
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    
    # Security Events
    SUSPICIOUS_ACTIVITY = "security.suspicious"
    RATE_LIMIT_EXCEEDED = "security.rate_limit"
    BRUTE_FORCE_DETECTED = "security.brute_force"
    SQL_INJECTION_ATTEMPT = "security.sql_injection"
    XSS_ATTEMPT = "security.xss"
    CSRF_ATTEMPT = "security.csrf"
    
    # System Events
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"
    CONFIG_CHANGE = "system.config_change"
    BACKUP_CREATED = "system.backup.created"
    BACKUP_RESTORED = "system.backup.restored"
    
    # Admin Events
    ADMIN_ACTION = "admin.action"
    USER_CREATED = "admin.user.created"
    USER_DELETED = "admin.user.deleted"
    USER_SUSPENDED = "admin.user.suspended"
    
    # API Events
    API_KEY_CREATED = "api.key.created"
    API_KEY_REVOKED = "api.key.revoked"
    API_RATE_LIMIT = "api.rate_limit"
    API_QUOTA_EXCEEDED = "api.quota_exceeded"

class SecurityEventSeverity(Enum):
    """Security event severity levels"""
    
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Alert notification channels"""
    
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DATABASE = "database"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    
    event_id: str
    event_type: SecurityEventType
    severity: SecurityEventSeverity
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    resource_id: Optional[str] = None
    organization_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: int = 0
    geo_location: Optional[Dict[str, str]] = None
    fingerprint: Optional[str] = None
    
    def __post_init__(self):
        """Generate fingerprint for event deduplication"""
        if not self.fingerprint:
            fingerprint_data = f"{self.event_type.value}:{self.source_ip}:{self.user_id}:{self.endpoint}"
            self.fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

@dataclass 
class AlertRule:
    """Alert rule configuration"""
    
    rule_id: str
    name: str
    description: str
    event_types: Set[SecurityEventType]
    severity_threshold: SecurityEventSeverity
    conditions: Dict[str, Any] = field(default_factory=dict)
    time_window: int = 300  # seconds
    threshold_count: int = 1
    channels: Set[AlertChannel] = field(default_factory=set)
    enabled: bool = True
    cooldown_period: int = 300  # seconds
    
class ThreatIntelligence:
    """Threat intelligence and risk assessment"""
    
    def __init__(self):
        # Known malicious IP ranges (simplified - in production use threat feeds)
        self.malicious_ip_ranges = [
            ipaddress.IPv4Network('10.0.0.0/8'),  # Example - replace with real threat data
        ]
        
        # Suspicious user agents
        self.suspicious_user_agents = [
            'sqlmap',
            'nikto',
            'nessus',
            'burpsuite',
            'nmap',
            'masscan'
        ]
        
        # Known attack patterns
        self.attack_patterns = {
            'sql_injection': [
                r"union\s+select",
                r"insert\s+into",
                r"drop\s+table",
                r"'.*or.*1=1",
                r"admin'--"
            ],
            'xss': [
                r"<script>",
                r"javascript:",
                r"onload=",
                r"onerror=",
                r"alert\("
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"web\.config"
            ]
        }
    
    def assess_ip_reputation(self, ip_address: str) -> int:
        """Assess IP reputation (0-100 risk score)"""
        try:
            ip = ipaddress.IPv4Address(ip_address)
            
            # Check against malicious IP ranges
            for malicious_range in self.malicious_ip_ranges:
                if ip in malicious_range:
                    return 90
            
            # Check if it's a private IP (generally lower risk)
            if ip.is_private:
                return 10
            
            # Default risk for public IPs
            return 30
            
        except Exception:
            return 50  # Unknown format, medium risk
    
    def assess_user_agent(self, user_agent: str) -> int:
        """Assess user agent risk (0-100 risk score)"""
        if not user_agent:
            return 60
        
        user_agent_lower = user_agent.lower()
        
        # Check for known attack tools
        for suspicious_agent in self.suspicious_user_agents:
            if suspicious_agent in user_agent_lower:
                return 95
        
        # Check for missing or minimal user agent
        if len(user_agent) < 10:
            return 70
        
        return 20  # Normal user agent
    
    def detect_attack_patterns(self, payload: str, attack_type: str) -> List[str]:
        """Detect attack patterns in payload"""
        import re
        
        detected_patterns = []
        patterns = self.attack_patterns.get(attack_type, [])
        
        for pattern in patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        return detected_patterns

class SecurityAuditor:
    """Main security auditing and monitoring system"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.threat_intel = ThreatIntelligence()
        self.alert_rules: Dict[str, AlertRule] = {}
        self.running_tasks: Set[asyncio.Task] = set()
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default security alert rules"""
        
        # Brute force detection
        self.alert_rules["brute_force"] = AlertRule(
            rule_id="brute_force",
            name="Brute Force Detection",
            description="Multiple failed login attempts from same IP",
            event_types={SecurityEventType.LOGIN_FAILURE},
            severity_threshold=SecurityEventSeverity.MEDIUM,
            time_window=300,
            threshold_count=5,
            channels={AlertChannel.EMAIL, AlertChannel.DATABASE},
            conditions={"same_ip": True}
        )
        
        # Suspicious activity detection
        self.alert_rules["suspicious_activity"] = AlertRule(
            rule_id="suspicious_activity", 
            name="Suspicious Activity",
            description="High-risk security events detected",
            event_types={
                SecurityEventType.SQL_INJECTION_ATTEMPT,
                SecurityEventType.XSS_ATTEMPT,
                SecurityEventType.CSRF_ATTEMPT
            },
            severity_threshold=SecurityEventSeverity.HIGH,
            time_window=60,
            threshold_count=1,
            channels={AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.DATABASE}
        )
        
        # Unauthorized access attempts
        self.alert_rules["access_denied"] = AlertRule(
            rule_id="access_denied",
            name="Multiple Access Denials", 
            description="Multiple authorization failures",
            event_types={SecurityEventType.ACCESS_DENIED},
            severity_threshold=SecurityEventSeverity.MEDIUM,
            time_window=300,
            threshold_count=10,
            channels={AlertChannel.EMAIL, AlertChannel.DATABASE}
        )
        
        # Admin activity monitoring
        self.alert_rules["admin_activity"] = AlertRule(
            rule_id="admin_activity",
            name="Administrative Actions",
            description="Critical administrative actions performed",
            event_types={
                SecurityEventType.USER_DELETED,
                SecurityEventType.USER_SUSPENDED,
                SecurityEventType.ROLE_ASSIGNED,
                SecurityEventType.CONFIG_CHANGE
            },
            severity_threshold=SecurityEventSeverity.HIGH,
            time_window=1,
            threshold_count=1,
            channels={AlertChannel.EMAIL, AlertChannel.DATABASE}
        )
    
    async def log_security_event(self, event: SecurityEvent) -> bool:
        """Log security event and trigger alerting if needed"""
        try:
            # Enhance event with threat intelligence
            await self._enhance_event_with_threat_intel(event)
            
            # Store event in Redis
            event_key = f"security_event:{event.event_id}"
            event_data = asdict(event)
            
            # Convert datetime to ISO string for JSON serialization
            event_data['timestamp'] = event.timestamp.isoformat()
            
            # Store event (expires after 30 days)
            await self.redis.setex(
                event_key, 
                86400 * 30,  # 30 days
                json.dumps(event_data, default=str)
            )
            
            # Add to time-series index for queries
            await self._index_event_by_time(event)
            await self._index_event_by_type(event)
            await self._index_event_by_user(event)
            
            # Check alert rules
            await self._check_alert_rules(event)
            
            # Log structured event
            logger.info(
                "Security event logged",
                event_id=event.event_id,
                event_type=event.event_type.value,
                severity=event.severity.value,
                user_id=event.user_id,
                source_ip=event.source_ip,
                risk_score=event.risk_score,
                message=event.message
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to log security event", 
                        event_id=event.event_id, 
                        error=str(e))
            return False
    
    async def _enhance_event_with_threat_intel(self, event: SecurityEvent):
        """Enhance event with threat intelligence data"""
        risk_score = 0
        
        # Assess IP reputation if available
        if event.source_ip:
            ip_risk = self.threat_intel.assess_ip_reputation(event.source_ip)
            risk_score += ip_risk
            
            # Add geo-location (simplified - in production use GeoIP service)
            if not event.geo_location:
                event.geo_location = {"country": "Unknown", "city": "Unknown"}
        
        # Assess user agent if available  
        if event.user_agent:
            ua_risk = self.threat_intel.assess_user_agent(event.user_agent)
            risk_score += ua_risk
        
        # Add severity-based risk
        severity_risk = {
            SecurityEventSeverity.INFO: 5,
            SecurityEventSeverity.LOW: 15,
            SecurityEventSeverity.MEDIUM: 35,
            SecurityEventSeverity.HIGH: 70,
            SecurityEventSeverity.CRITICAL: 95
        }
        risk_score += severity_risk.get(event.severity, 30)
        
        # Cap risk score at 100
        event.risk_score = min(risk_score, 100)
    
    async def _index_event_by_time(self, event: SecurityEvent):
        """Index event by timestamp for time-based queries"""
        time_key = f"events_by_time:{event.timestamp.strftime('%Y-%m-%d:%H')}"
        await self.redis.zadd(
            time_key, 
            {event.event_id: event.timestamp.timestamp()}
        )
        # Expire hourly indexes after 7 days
        await self.redis.expire(time_key, 86400 * 7)
    
    async def _index_event_by_type(self, event: SecurityEvent):
        """Index event by type for filtering"""
        type_key = f"events_by_type:{event.event_type.value}"
        await self.redis.zadd(
            type_key,
            {event.event_id: event.timestamp.timestamp()}
        )
        # Expire type indexes after 30 days
        await self.redis.expire(type_key, 86400 * 30)
    
    async def _index_event_by_user(self, event: SecurityEvent):
        """Index event by user for user-specific queries"""
        if event.user_id:
            user_key = f"events_by_user:{event.user_id}"
            await self.redis.zadd(
                user_key,
                {event.event_id: event.timestamp.timestamp()}
            )
            # Expire user indexes after 90 days
            await self.redis.expire(user_key, 86400 * 90)
    
    async def _check_alert_rules(self, event: SecurityEvent):
        """Check if event triggers any alert rules"""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            if event.event_type not in rule.event_types:
                continue
            
            if event.severity.value not in [s.value for s in SecurityEventSeverity if s.name >= rule.severity_threshold.name]:
                continue
            
            # Check if we're in cooldown period
            cooldown_key = f"alert_cooldown:{rule.rule_id}"
            if await self.redis.exists(cooldown_key):
                continue
            
            # Count matching events in time window
            matching_events = await self._count_matching_events(event, rule)
            
            if matching_events >= rule.threshold_count:
                await self._trigger_alert(rule, event, matching_events)
    
    async def _count_matching_events(self, event: SecurityEvent, rule: AlertRule) -> int:
        """Count events matching alert rule criteria in time window"""
        end_time = event.timestamp.timestamp()
        start_time = end_time - rule.time_window
        
        count = 0
        
        for event_type in rule.event_types:
            type_key = f"events_by_type:{event_type.value}"
            
            # Get events in time window
            event_ids = await self.redis.zrangebyscore(
                type_key, start_time, end_time
            )
            
            # Apply additional conditions
            for event_id in event_ids:
                if await self._event_matches_conditions(event_id.decode(), event, rule):
                    count += 1
        
        return count
    
    async def _event_matches_conditions(self, event_id: str, trigger_event: SecurityEvent, rule: AlertRule) -> bool:
        """Check if stored event matches rule conditions"""
        try:
            event_key = f"security_event:{event_id}"
            event_data = await self.redis.get(event_key)
            
            if not event_data:
                return False
            
            stored_event_data = json.loads(event_data)
            
            # Apply rule conditions
            conditions = rule.conditions
            
            if conditions.get("same_ip") and stored_event_data.get("source_ip") != trigger_event.source_ip:
                return False
            
            if conditions.get("same_user") and stored_event_data.get("user_id") != trigger_event.user_id:
                return False
            
            if conditions.get("same_endpoint") and stored_event_data.get("endpoint") != trigger_event.endpoint:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking event conditions", event_id=event_id, error=str(e))
            return False
    
    async def _trigger_alert(self, rule: AlertRule, trigger_event: SecurityEvent, event_count: int):
        """Trigger security alert"""
        try:
            alert_id = f"alert_{rule.rule_id}_{int(trigger_event.timestamp.timestamp())}"
            
            alert_data = {
                "alert_id": alert_id,
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "trigger_event_id": trigger_event.event_id,
                "event_count": event_count,
                "time_window": rule.time_window,
                "timestamp": trigger_event.timestamp.isoformat(),
                "severity": trigger_event.severity.value,
                "message": f"{rule.description} - {event_count} events in {rule.time_window}s"
            }
            
            # Store alert
            alert_key = f"security_alert:{alert_id}"
            await self.redis.setex(
                alert_key,
                86400 * 30,  # Keep alerts for 30 days
                json.dumps(alert_data)
            )
            
            # Send notifications
            await self._send_alert_notifications(rule, alert_data, trigger_event)
            
            # Set cooldown period
            cooldown_key = f"alert_cooldown:{rule.rule_id}"
            await self.redis.setex(cooldown_key, rule.cooldown_period, "1")
            
            logger.warning(
                "Security alert triggered",
                alert_id=alert_id,
                rule_name=rule.name,
                event_count=event_count,
                severity=trigger_event.severity.value
            )
            
        except Exception as e:
            logger.error("Failed to trigger alert", rule_id=rule.rule_id, error=str(e))
    
    async def _send_alert_notifications(self, rule: AlertRule, alert_data: Dict, trigger_event: SecurityEvent):
        """Send alert notifications to configured channels"""
        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert_data, trigger_event)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert_data, trigger_event)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert_data, trigger_event)
                elif channel == AlertChannel.DATABASE:
                    # Already stored in Redis, could also store in main database
                    pass
                    
            except Exception as e:
                logger.error("Failed to send alert notification", 
                            channel=channel.value, 
                            alert_id=alert_data["alert_id"], 
                            error=str(e))
    
    async def _send_email_alert(self, alert_data: Dict, trigger_event: SecurityEvent):
        """Send email alert (simplified implementation)"""
        # In production, use proper email service configuration
        pass
    
    async def _send_slack_alert(self, alert_data: Dict, trigger_event: SecurityEvent):
        """Send Slack alert (simplified implementation)"""
        # In production, use Slack webhook/API
        pass
    
    async def _send_webhook_alert(self, alert_data: Dict, trigger_event: SecurityEvent):
        """Send webhook alert (simplified implementation)"""
        # In production, make HTTP POST to configured webhook
        pass
    
    async def get_security_events(self, 
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 event_types: Optional[List[SecurityEventType]] = None,
                                 user_id: Optional[str] = None,
                                 severity_min: Optional[SecurityEventSeverity] = None,
                                 limit: int = 100) -> List[Dict]:
        """Query security events with filters"""
        try:
            events = []
            
            # Default time range (last 24 hours)
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=1)
            
            # Query by time range
            time_key = f"events_by_time:{start_time.strftime('%Y-%m-%d:%H')}"
            event_ids = await self.redis.zrangebyscore(
                time_key,
                start_time.timestamp(),
                end_time.timestamp()
            )
            
            # Retrieve and filter events
            for event_id in event_ids[:limit]:
                event_key = f"security_event:{event_id.decode()}"
                event_data = await self.redis.get(event_key)
                
                if event_data:
                    event_dict = json.loads(event_data)
                    
                    # Apply filters
                    if event_types:
                        if event_dict.get("event_type") not in [et.value for et in event_types]:
                            continue
                    
                    if user_id and event_dict.get("user_id") != user_id:
                        continue
                    
                    if severity_min:
                        event_severity = SecurityEventSeverity(event_dict.get("severity"))
                        if event_severity.name < severity_min.name:
                            continue
                    
                    events.append(event_dict)
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error("Failed to get security events", error=str(e))
            return []
    
    async def get_security_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent security alerts"""
        try:
            # Get all alert keys (simplified - in production use proper indexing)
            alert_keys = await self.redis.keys("security_alert:*")
            alerts = []
            
            for alert_key in alert_keys[:limit]:
                alert_data = await self.redis.get(alert_key)
                if alert_data:
                    alerts.append(json.loads(alert_data))
            
            # Sort by timestamp
            alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error("Failed to get security alerts", error=str(e))
            return []
    
    async def get_security_metrics(self, time_range: int = 24) -> Dict[str, Any]:
        """Get security metrics for dashboard"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=time_range)
            
            # Get events in time range
            events = await self.get_security_events(start_time, end_time, limit=1000)
            
            # Calculate metrics
            total_events = len(events)
            
            # Count by severity
            severity_counts = {}
            for severity in SecurityEventSeverity:
                severity_counts[severity.value] = sum(
                    1 for event in events if event.get("severity") == severity.value
                )
            
            # Count by event type
            event_type_counts = {}
            for event in events:
                event_type = event.get("event_type", "unknown")
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            # Top source IPs
            ip_counts = {}
            for event in events:
                source_ip = event.get("source_ip")
                if source_ip:
                    ip_counts[source_ip] = ip_counts.get(source_ip, 0) + 1
            
            top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Average risk score
            risk_scores = [event.get("risk_score", 0) for event in events if event.get("risk_score")]
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            # Recent alerts count
            alerts = await self.get_security_alerts(limit=100)
            recent_alerts = sum(
                1 for alert in alerts 
                if datetime.fromisoformat(alert.get("timestamp", "1970-01-01")) >= start_time
            )
            
            return {
                "time_range_hours": time_range,
                "total_events": total_events,
                "severity_distribution": severity_counts,
                "event_type_distribution": event_type_counts,
                "top_source_ips": top_ips,
                "average_risk_score": round(avg_risk_score, 2),
                "recent_alerts": recent_alerts,
                "metrics_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to calculate security metrics", error=str(e))
            return {}

def create_security_event_from_request(
    event_type: SecurityEventType,
    request: Request,
    response: Optional[Response] = None,
    user_id: Optional[str] = None,
    message: str = "",
    severity: SecurityEventSeverity = SecurityEventSeverity.INFO,
    additional_details: Optional[Dict] = None
) -> SecurityEvent:
    """Helper function to create security event from FastAPI request"""
    import uuid
    
    # Extract request details
    source_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    endpoint = str(request.url.path)
    method = request.method
    status_code = response.status_code if response else None
    
    # Generate session ID from headers (simplified)
    session_id = request.headers.get("x-session-id")
    
    # Create event
    event = SecurityEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        severity=severity,
        timestamp=datetime.utcnow(),
        source_ip=source_ip,
        user_id=user_id,
        user_agent=user_agent,
        session_id=session_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        message=message,
        details=additional_details or {}
    )
    
    return event

# Global security auditor instance
_security_auditor: Optional[SecurityAuditor] = None

def get_security_auditor() -> Optional[SecurityAuditor]:
    """Get global security auditor instance"""
    return _security_auditor

def init_security_auditor(redis_client: redis.Redis) -> SecurityAuditor:
    """Initialize global security auditor"""
    global _security_auditor
    _security_auditor = SecurityAuditor(redis_client)
    logger.info("Security auditor initialized")
    return _security_auditor