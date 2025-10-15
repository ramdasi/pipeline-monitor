"""
Publishing Pipeline Health Monitor and Recovery System
Monitors pipeline health, auto-recovers failures, and provides operational visibility.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import json


class PipelineComponent(Enum):
    """Pipeline components to monitor"""
    NETWORK = "network"
    VALIDATION_SERVICE = "validation_service"
    DATABASE = "database"
    STORAGE = "storage"
    QUEUE = "queue"


class HealthStatus(Enum):
    """Health status of components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    RECOVERING = "recovering"


class RecoveryAction(Enum):
    """Available recovery actions"""
    RECONNECT = "reconnect"
    RESTART_SERVICE = "restart_service"
    CLEAR_QUEUE = "clear_queue"
    FAILOVER = "failover"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class HealthCheck:
    """Health check result"""
    component: PipelineComponent
    status: HealthStatus
    timestamp: datetime
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class RecoveryAttempt:
    """Recovery attempt record"""
    attempt_id: str
    component: PipelineComponent
    action: RecoveryAction
    timestamp: datetime
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class PipelineStatus:
    """Overall pipeline status"""
    overall_status: HealthStatus
    components: Dict[str, HealthStatus]
    last_check: datetime
    uptime_percentage: float
    recent_failures: List[Dict]
    suggested_actions: List[str]
    is_auto_recoverable: bool


class AuditLogger:
    """Audit logger for all pipeline events"""
    
    def __init__(self, log_file: str = "pipeline_audit.log"):
        self.logger = logging.getLogger("pipeline_audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_health_check(self, check: HealthCheck):
        """Log health check result"""
        self.logger.info(f"HEALTH_CHECK: {json.dumps(asdict(check), default=str)}")
    
    def log_failure_detected(self, component: PipelineComponent, error: str):
        """Log failure detection"""
        self.logger.error(
            f"FAILURE_DETECTED: component={component.value}, error={error}"
        )
    
    def log_recovery_attempt(self, attempt: RecoveryAttempt):
        """Log recovery attempt"""
        level = logging.INFO if attempt.success else logging.ERROR
        self.logger.log(
            level,
            f"RECOVERY_ATTEMPT: {json.dumps(asdict(attempt), default=str)}"
        )
    
    def log_alert_triggered(self, component: PipelineComponent, severity: str):
        """Log alert triggering"""
        self.logger.warning(
            f"ALERT_TRIGGERED: component={component.value}, severity={severity}"
        )


class PipelineHealthMonitor:
    """
    Main pipeline health monitoring and recovery system
    """
    
    def __init__(
        self,
        check_interval: int = 30,
        alert_callback: Optional[Callable] = None
    ):
        self.check_interval = check_interval
        self.alert_callback = alert_callback or self._default_alert
        self.audit_logger = AuditLogger()
        
        # Health tracking
        self.component_status: Dict[PipelineComponent, HealthStatus] = {}
        self.recent_checks: List[HealthCheck] = []
        self.recovery_attempts: List[RecoveryAttempt] = []
        
        # Statistics
        self.total_checks = 0
        self.failed_checks = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        
        # Initialize all components as healthy
        for component in PipelineComponent:
            self.component_status[component] = HealthStatus.HEALTHY
        
        self._monitoring = False
        self._monitor_task = None
    
    async def check_network(self) -> HealthCheck:
        """Check network connectivity"""
        start = datetime.now()
        try:
            # Simulate network check
            await asyncio.sleep(0.05)  # Simulate latency
            
            # Simulate occasional failures
            import random
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Network timeout")
            
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=latency
            )
        except Exception as e:
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_validation_service(self) -> HealthCheck:
        """Check validation service health"""
        start = datetime.now()
        try:
            # Simulate service check
            await asyncio.sleep(0.03)
            
            import random
            if random.random() < 0.03:  # 3% failure rate
                raise Exception("Validation service unresponsive")
            
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheck(
                component=PipelineComponent.VALIDATION_SERVICE,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=latency,
                metadata={"active_validations": 5}
            )
        except Exception as e:
            return HealthCheck(
                component=PipelineComponent.VALIDATION_SERVICE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_database(self) -> HealthCheck:
        """Check database connectivity"""
        start = datetime.now()
        try:
            # Simulate DB check
            await asyncio.sleep(0.02)
            
            import random
            if random.random() < 0.02:  # 2% failure rate
                raise Exception("Database connection lost")
            
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheck(
                component=PipelineComponent.DATABASE,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=latency,
                metadata={"active_connections": 10, "pool_size": 20}
            )
        except Exception as e:
            return HealthCheck(
                component=PipelineComponent.DATABASE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_storage(self) -> HealthCheck:
        """Check storage system health"""
        start = datetime.now()
        try:
            await asyncio.sleep(0.04)
            
            import random
            if random.random() < 0.01:  # 1% failure rate
                raise Exception("Storage service unavailable")
            
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheck(
                component=PipelineComponent.STORAGE,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=latency,
                metadata={"disk_usage_percent": 65}
            )
        except Exception as e:
            return HealthCheck(
                component=PipelineComponent.STORAGE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_queue(self) -> HealthCheck:
        """Check message queue health"""
        start = datetime.now()
        try:
            await asyncio.sleep(0.02)
            
            import random
            if random.random() < 0.04:  # 4% failure rate
                raise Exception("Queue broker connection failed")
            
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheck(
                component=PipelineComponent.QUEUE,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=latency,
                metadata={"pending_messages": 42}
            )
        except Exception as e:
            return HealthCheck(
                component=PipelineComponent.QUEUE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def perform_health_checks(self) -> List[HealthCheck]:
        """Perform health checks on all components"""
        checks = await asyncio.gather(
            self.check_network(),
            self.check_validation_service(),
            self.check_database(),
            self.check_storage(),
            self.check_queue(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, HealthCheck):
                results.append(check)
                self.audit_logger.log_health_check(check)
        
        return results
    
    async def attempt_recovery(
        self,
        component: PipelineComponent
    ) -> RecoveryAttempt:
        """Attempt to recover a failed component"""
        attempt_id = f"{component.value}_{datetime.now().timestamp()}"
        start = datetime.now()
        
        # Determine recovery action
        recovery_map = {
            PipelineComponent.NETWORK: RecoveryAction.RECONNECT,
            PipelineComponent.VALIDATION_SERVICE: RecoveryAction.RESTART_SERVICE,
            PipelineComponent.DATABASE: RecoveryAction.RECONNECT,
            PipelineComponent.STORAGE: RecoveryAction.FAILOVER,
            PipelineComponent.QUEUE: RecoveryAction.CLEAR_QUEUE,
        }
        
        action = recovery_map.get(component, RecoveryAction.MANUAL_INTERVENTION)
        
        try:
            # Simulate recovery attempt
            self.component_status[component] = HealthStatus.RECOVERING
            
            if action == RecoveryAction.RECONNECT:
                await self._reconnect(component)
            elif action == RecoveryAction.RESTART_SERVICE:
                await self._restart_service(component)
            elif action == RecoveryAction.CLEAR_QUEUE:
                await self._clear_queue(component)
            elif action == RecoveryAction.FAILOVER:
                await self._failover(component)
            else:
                raise Exception("Manual intervention required")
            
            # Verify recovery
            await asyncio.sleep(0.5)
            
            duration = (datetime.now() - start).total_seconds() * 1000
            
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                component=component,
                action=action,
                timestamp=datetime.now(),
                success=True,
                duration_ms=duration,
                metadata={"retries": 1}
            )
            
            self.component_status[component] = HealthStatus.HEALTHY
            self.successful_recoveries += 1
            
        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                component=component,
                action=action,
                timestamp=datetime.now(),
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
            
            self.component_status[component] = HealthStatus.DOWN
            self.failed_recoveries += 1
        
        self.recovery_attempts.append(attempt)
        self.audit_logger.log_recovery_attempt(attempt)
        
        return attempt
    
    async def _reconnect(self, component: PipelineComponent):
        """Simulate reconnection"""
        await asyncio.sleep(0.3)
        import random
        if random.random() < 0.2:  # 20% failure rate
            raise Exception("Reconnection failed")
    
    async def _restart_service(self, component: PipelineComponent):
        """Simulate service restart"""
        await asyncio.sleep(0.5)
        import random
        if random.random() < 0.15:  # 15% failure rate
            raise Exception("Service restart failed")
    
    async def _clear_queue(self, component: PipelineComponent):
        """Simulate queue clearing"""
        await asyncio.sleep(0.2)
        import random
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Queue clear failed")
    
    async def _failover(self, component: PipelineComponent):
        """Simulate failover"""
        await asyncio.sleep(0.4)
        import random
        if random.random() < 0.25:  # 25% failure rate
            raise Exception("Failover failed")
    
    def _default_alert(self, component: PipelineComponent, status: HealthStatus):
        """Default alert handler"""
        severity = "CRITICAL" if status == HealthStatus.DOWN else "WARNING"
        self.audit_logger.log_alert_triggered(component, severity)
        print(f"🚨 ALERT: {component.value} is {status.value}")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Perform health checks
                checks = await self.perform_health_checks()
                self.total_checks += len(checks)
                
                # Store recent checks
                self.recent_checks.extend(checks)
                self.recent_checks = self.recent_checks[-100:]  # Keep last 100
                
                # Process failures
                for check in checks:
                    if check.status != HealthStatus.HEALTHY:
                        self.failed_checks += 1
                        
                        # Log failure
                        self.audit_logger.log_failure_detected(
                            check.component,
                            check.error_message or "Unknown error"
                        )
                        
                        # Trigger alert
                        self.alert_callback(check.component, check.status)
                        
                        # Update status
                        self.component_status[check.component] = check.status
                        
                        # Attempt auto-recovery
                        if self._is_auto_recoverable(check.component):
                            await self.attempt_recovery(check.component)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.audit_logger.logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def _is_auto_recoverable(self, component: PipelineComponent) -> bool:
        """Determine if component can be auto-recovered"""
        # All components except validation service can attempt auto-recovery
        return component != PipelineComponent.VALIDATION_SERVICE
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_task = asyncio.create_task(self.monitor_loop())
            self.audit_logger.logger.info("Pipeline monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
        self.audit_logger.logger.info("Pipeline monitoring stopped")
    
    def get_pipeline_status(self) -> PipelineStatus:
        """Get current pipeline status"""
        # Calculate overall status
        statuses = list(self.component_status.values())
        if any(s == HealthStatus.DOWN for s in statuses):
            overall = HealthStatus.DOWN
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        elif any(s == HealthStatus.RECOVERING for s in statuses):
            overall = HealthStatus.RECOVERING
        else:
            overall = HealthStatus.HEALTHY
        
        # Calculate uptime
        uptime = (
            ((self.total_checks - self.failed_checks) / self.total_checks * 100)
            if self.total_checks > 0 else 100.0
        )
        
        # Get recent failures
        recent_failures = [
            {
                "component": check.component.value,
                "timestamp": check.timestamp.isoformat(),
                "error": check.error_message
            }
            for check in self.recent_checks[-10:]
            if check.status != HealthStatus.HEALTHY
        ]
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions()
        
        # Check if auto-recoverable
        is_auto_recoverable = all(
            self._is_auto_recoverable(comp)
            for comp, status in self.component_status.items()
            if status != HealthStatus.HEALTHY
        )
        
        return PipelineStatus(
            overall_status=overall,
            components={
                comp.value: status.value 
                for comp, status in self.component_status.items()
            },
            last_check=datetime.now(),
            uptime_percentage=uptime,
            recent_failures=recent_failures,
            suggested_actions=suggested_actions,
            is_auto_recoverable=is_auto_recoverable
        )
    
    def _generate_suggested_actions(self) -> List[str]:
        """Generate suggested recovery actions"""
        actions = []
        
        for component, status in self.component_status.items():
            if status == HealthStatus.DOWN:
                if component == PipelineComponent.NETWORK:
                    actions.append(
                        "⚠️ Network is down. Check internet connectivity and firewall rules."
                    )
                elif component == PipelineComponent.VALIDATION_SERVICE:
                    actions.append(
                        "⚠️ Validation service crashed. Contact engineering to restart service."
                    )
                elif component == PipelineComponent.DATABASE:
                    actions.append(
                        "⚠️ Database connection lost. Check DB server status and credentials."
                    )
                elif component == PipelineComponent.STORAGE:
                    actions.append(
                        "⚠️ Storage unavailable. Verify storage service and check disk space."
                    )
                elif component == PipelineComponent.QUEUE:
                    actions.append(
                        "⚠️ Message queue down. Check queue broker and clear stuck messages."
                    )
        
        if not actions:
            actions.append("✅ All systems operational. No action needed.")
        
        return actions
    
    def get_editor_message(self) -> str:
        """Generate clear editor-facing message"""
        status = self.get_pipeline_status()
        
        if status.overall_status == HealthStatus.HEALTHY:
            return """
✅ **Publishing Pipeline: OPERATIONAL**

All systems are running normally. You can publish articles without issues.

Uptime: {:.2f}%
Last Check: {}
            """.format(
                status.uptime_percentage,
                status.last_check.strftime("%Y-%m-%d %H:%M:%S")
            ).strip()
        
        elif status.overall_status == HealthStatus.RECOVERING:
            return """
🔄 **Publishing Pipeline: RECOVERING**

The system detected issues and is attempting automatic recovery.
Please wait 1-2 minutes before trying to publish.

{}

If the issue persists, contact engineering.
            """.format("\n".join(status.suggested_actions)).strip()
        
        else:
            recovery_status = (
                "Automatic recovery in progress."
                if status.is_auto_recoverable
                else "Manual intervention required - contact engineering immediately."
            )
            
            return """
🚨 **Publishing Pipeline: DOWN**

The publishing system is currently unavailable.

**Issues Detected:**
{}

**Next Steps:**
{}

**Recent Failures:**
{}

For immediate assistance, contact the engineering team with this error report.
            """.format(
                "\n".join(f"- {comp}: {stat}" for comp, stat in status.components.items() if stat != "healthy"),
                recovery_status,
                "\n".join(f"- {f['component']}: {f['error']}" for f in status.recent_failures[-3:])
            ).strip()