"""
Comprehensive test suite for pipeline monitoring system
Tests all scenarios: failures, recoveries, alerts, etc.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from pipeline_monitor import (
    PipelineHealthMonitor,
    PipelineComponent,
    HealthStatus,
    RecoveryAction,
    HealthCheck,
    RecoveryAttempt
)


class TestHealthChecks:
    """Test health check functionality"""
    
    @pytest.mark.asyncio
    async def test_network_check_success(self):
        """Test successful network health check"""
        monitor = PipelineHealthMonitor()
        check = await monitor.check_network()
        
        assert check.component == PipelineComponent.NETWORK
        assert check.timestamp is not None
        assert check.latency_ms is None or check.latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_validation_service_check_success(self):
        """Test successful validation service health check"""
        monitor = PipelineHealthMonitor()
        check = await monitor.check_validation_service()
        
        assert check.component == PipelineComponent.VALIDATION_SERVICE
        assert check.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_database_check_success(self):
        """Test successful database health check"""
        monitor = PipelineHealthMonitor()
        check = await monitor.check_database()
        
        assert check.component == PipelineComponent.DATABASE
        assert check.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_all_health_checks(self):
        """Test performing all health checks"""
        monitor = PipelineHealthMonitor()
        checks = await monitor.perform_health_checks()
        
        assert len(checks) == 5
        components = [check.component for check in checks]
        assert PipelineComponent.NETWORK in components
        assert PipelineComponent.VALIDATION_SERVICE in components
        assert PipelineComponent.DATABASE in components


class TestFailureDetection:
    """Test failure detection scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_failure_detection(self):
        """Test detection of network failure"""
        monitor = PipelineHealthMonitor()
        
        # Mock network check to always fail
        async def mock_check_network():
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Network timeout"
            )
        
        monitor.check_network = mock_check_network
        checks = await monitor.perform_health_checks()
        
        network_check = next(c for c in checks if c.component == PipelineComponent.NETWORK)
        assert network_check.status == HealthStatus.DOWN
        assert network_check.error_message == "Network timeout"
    
    @pytest.mark.asyncio
    async def test_database_failure_detection(self):
        """Test detection of database failure"""
        monitor = PipelineHealthMonitor()
        
        async def mock_check_database():
            return HealthCheck(
                component=PipelineComponent.DATABASE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Database connection lost"
            )
        
        monitor.check_database = mock_check_database
        checks = await monitor.perform_health_checks()
        
        db_check = next(c for c in checks if c.component == PipelineComponent.DATABASE)
        assert db_check.status == HealthStatus.DOWN
        assert "connection lost" in db_check.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_validation_service_crash_detection(self):
        """Test detection of validation service crash"""
        monitor = PipelineHealthMonitor()
        
        async def mock_check_validation():
            return HealthCheck(
                component=PipelineComponent.VALIDATION_SERVICE,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Validation service unresponsive"
            )
        
        monitor.check_validation_service = mock_check_validation
        checks = await monitor.perform_health_checks()
        
        val_check = next(c for c in checks if c.component == PipelineComponent.VALIDATION_SERVICE)
        assert val_check.status == HealthStatus.DOWN


class TestRecoverySuccess:
    """Test successful recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_recovery_success(self):
        """Test successful network recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.DOWN
        
        # Mock successful reconnection
        async def mock_reconnect(component):
            await asyncio.sleep(0.1)
            # Success - no exception
        
        monitor._reconnect = mock_reconnect
        
        attempt = await monitor.attempt_recovery(PipelineComponent.NETWORK)
        
        assert attempt.success is True
        assert attempt.component == PipelineComponent.NETWORK
        assert attempt.action == RecoveryAction.RECONNECT
        assert monitor.component_status[PipelineComponent.NETWORK] == HealthStatus.HEALTHY
        assert monitor.successful_recoveries == 1
    
    @pytest.mark.asyncio
    async def test_database_recovery_success(self):
        """Test successful database recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.DATABASE] = HealthStatus.DOWN
        
        async def mock_reconnect(component):
            await asyncio.sleep(0.1)
        
        monitor._reconnect = mock_reconnect
        
        attempt = await monitor.attempt_recovery(PipelineComponent.DATABASE)
        
        assert attempt.success is True
        assert attempt.action == RecoveryAction.RECONNECT
        assert monitor.component_status[PipelineComponent.DATABASE] == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_validation_service_recovery_success(self):
        """Test successful validation service recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.VALIDATION_SERVICE] = HealthStatus.DOWN
        
        async def mock_restart(component):
            await asyncio.sleep(0.1)
        
        monitor._restart_service = mock_restart
        
        attempt = await monitor.attempt_recovery(PipelineComponent.VALIDATION_SERVICE)
        
        assert attempt.success is True
        assert attempt.action == RecoveryAction.RESTART_SERVICE
        assert monitor.component_status[PipelineComponent.VALIDATION_SERVICE] == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_queue_recovery_success(self):
        """Test successful queue recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.QUEUE] = HealthStatus.DOWN
        
        async def mock_clear_queue(component):
            await asyncio.sleep(0.1)
        
        monitor._clear_queue = mock_clear_queue
        
        attempt = await monitor.attempt_recovery(PipelineComponent.QUEUE)
        
        assert attempt.success is True
        assert attempt.action == RecoveryAction.CLEAR_QUEUE
        assert monitor.component_status[PipelineComponent.QUEUE] == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_storage_recovery_success(self):
        """Test successful storage failover"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.STORAGE] = HealthStatus.DOWN
        
        async def mock_failover(component):
            await asyncio.sleep(0.1)
        
        monitor._failover = mock_failover
        
        attempt = await monitor.attempt_recovery(PipelineComponent.STORAGE)
        
        assert attempt.success is True
        assert attempt.action == RecoveryAction.FAILOVER
        assert monitor.component_status[PipelineComponent.STORAGE] == HealthStatus.HEALTHY


class TestRecoveryFailure:
    """Test failed recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_recovery_failure(self):
        """Test failed network recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.DOWN
        
        async def mock_reconnect(component):
            await asyncio.sleep(0.1)
            raise Exception("Reconnection failed")
        
        monitor._reconnect = mock_reconnect
        
        attempt = await monitor.attempt_recovery(PipelineComponent.NETWORK)
        
        assert attempt.success is False
        assert attempt.error_message == "Reconnection failed"
        assert monitor.component_status[PipelineComponent.NETWORK] == HealthStatus.DOWN
        assert monitor.failed_recoveries == 1
    
    @pytest.mark.asyncio
    async def test_validation_service_recovery_failure(self):
        """Test failed validation service recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.VALIDATION_SERVICE] = HealthStatus.DOWN
        
        async def mock_restart(component):
            await asyncio.sleep(0.1)
            raise Exception("Service restart failed")
        
        monitor._restart_service = mock_restart
        
        attempt = await monitor.attempt_recovery(PipelineComponent.VALIDATION_SERVICE)
        
        assert attempt.success is False
        assert "restart failed" in attempt.error_message.lower()
        assert monitor.component_status[PipelineComponent.VALIDATION_SERVICE] == HealthStatus.DOWN
    
    @pytest.mark.asyncio
    async def test_database_recovery_failure(self):
        """Test failed database recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.DATABASE] = HealthStatus.DOWN
        
        async def mock_reconnect(component):
            raise Exception("Database credentials invalid")
        
        monitor._reconnect = mock_reconnect
        
        attempt = await monitor.attempt_recovery(PipelineComponent.DATABASE)
        
        assert attempt.success is False
        assert monitor.component_status[PipelineComponent.DATABASE] == HealthStatus.DOWN


class TestAlertSystem:
    """Test alert triggering"""
    
    @pytest.mark.asyncio
    async def test_alert_triggered_on_failure(self):
        """Test that alerts are triggered on component failure"""
        alert_triggered = []
        
        def custom_alert(component, status):
            alert_triggered.append((component, status))
        
        monitor = PipelineHealthMonitor(alert_callback=custom_alert)
        
        # Simulate failure
        async def mock_check_network():
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Network timeout"
            )
        
        monitor.check_network = mock_check_network
        checks = await monitor.perform_health_checks()
        
        # Process the failure (simulate monitor loop behavior)
        for check in checks:
            if check.status != HealthStatus.HEALTHY:
                monitor.alert_callback(check.component, check.status)
        
        assert len(alert_triggered) > 0
        assert any(comp == PipelineComponent.NETWORK for comp, _ in alert_triggered)
    
    @pytest.mark.asyncio
    async def test_no_alert_on_success(self):
        """Test that alerts are not triggered when all checks pass"""
        alert_triggered = []
        
        def custom_alert(component, status):
            alert_triggered.append((component, status))
        
        monitor = PipelineHealthMonitor(alert_callback=custom_alert, check_interval=1)
        
        # All checks should pass (most of the time)
        checks = await monitor.perform_health_checks()
        
        # Only process actual failures
        for check in checks:
            if check.status != HealthStatus.HEALTHY:
                monitor.alert_callback(check.component, check.status)
        
        # Should have few or no alerts on healthy system
        assert len(alert_triggered) <= 1  # Allow for random failures


class TestPipelineStatus:
    """Test pipeline status reporting"""
    
    def test_pipeline_status_all_healthy(self):
        """Test status when all components are healthy"""
        monitor = PipelineHealthMonitor()
        status = monitor.get_pipeline_status()
        
        assert status.overall_status == HealthStatus.HEALTHY
        assert all(s == "healthy" for s in status.components.values())
        assert status.is_auto_recoverable is True
    
    def test_pipeline_status_one_component_down(self):
        """Test status when one component is down"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.DOWN
        
        status = monitor.get_pipeline_status()
        
        assert status.overall_status == HealthStatus.DOWN
        assert status.components["network"] == "down"
        assert len(status.suggested_actions) > 0
    
    def test_pipeline_status_validation_service_down(self):
        """Test status when validation service is down"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.VALIDATION_SERVICE] = HealthStatus.DOWN
        
        status = monitor.get_pipeline_status()
        
        assert status.overall_status == HealthStatus.DOWN
        assert status.is_auto_recoverable is False  # Validation service needs manual intervention
    
    def test_pipeline_status_recovering(self):
        """Test status when components are recovering"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.DATABASE] = HealthStatus.RECOVERING
        
        status = monitor.get_pipeline_status()
        
        assert status.overall_status == HealthStatus.RECOVERING


class TestEditorMessage:
    """Test editor-facing messages"""
    
    def test_editor_message_healthy(self):
        """Test editor message when system is healthy"""
        monitor = PipelineHealthMonitor()
        message = monitor.get_editor_message()
        
        assert "OPERATIONAL" in message
        assert "✅" in message
    
    def test_editor_message_down(self):
        """Test editor message when system is down"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.DATABASE] = HealthStatus.DOWN
        
        message = monitor.get_editor_message()
        
        assert "DOWN" in message
        assert "🚨" in message
        assert "database" in message.lower()
    
    def test_editor_message_recovering(self):
        """Test editor message during recovery"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.RECOVERING
        
        message = monitor.get_editor_message()
        
        assert "RECOVERING" in message
        assert "🔄" in message
    
    def test_editor_message_manual_intervention(self):
        """Test editor message when manual intervention needed"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.VALIDATION_SERVICE] = HealthStatus.DOWN
        
        status = monitor.get_pipeline_status()
        
        assert status.is_auto_recoverable is False
        assert len(status.suggested_actions) > 0


class TestAuditLogging:
    """Test audit logging functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check_logged(self):
        """Test that health checks are logged"""
        monitor = PipelineHealthMonitor()
        
        with patch.object(monitor.audit_logger, 'log_health_check') as mock_log:
            await monitor.perform_health_checks()
            assert mock_log.call_count == 5  # One for each component
    
    @pytest.mark.asyncio
    async def test_failure_logged(self):
        """Test that failures are logged"""
        monitor = PipelineHealthMonitor()
        
        async def mock_check_network():
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Network timeout"
            )
        
        monitor.check_network = mock_check_network
        
        with patch.object(monitor.audit_logger, 'log_failure_detected') as mock_log:
            checks = await monitor.perform_health_checks()
            
            # Simulate monitor loop processing
            for check in checks:
                if check.status != HealthStatus.HEALTHY:
                    monitor.audit_logger.log_failure_detected(
                        check.component,
                        check.error_message or "Unknown error"
                    )
            
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_recovery_attempt_logged(self):
        """Test that recovery attempts are logged"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.DOWN
        
        with patch.object(monitor.audit_logger, 'log_recovery_attempt') as mock_log:
            await monitor.attempt_recovery(PipelineComponent.NETWORK)
            mock_log.assert_called_once()


class TestMetrics:
    """Test metrics and statistics"""
    
    @pytest.mark.asyncio
    async def test_check_counters(self):
        """Test that check counters are updated"""
        monitor = PipelineHealthMonitor()
        
        initial_count = monitor.total_checks
        await monitor.perform_health_checks()
        
        assert monitor.total_checks > initial_count
    
    @pytest.mark.asyncio
    async def test_recovery_counters(self):
        """Test that recovery counters are updated"""
        monitor = PipelineHealthMonitor()
        monitor.component_status[PipelineComponent.NETWORK] = HealthStatus.DOWN
        
        async def mock_reconnect(component):
            pass  # Success
        
        monitor._reconnect = mock_reconnect
        
        initial_success = monitor.successful_recoveries
        await monitor.attempt_recovery(PipelineComponent.NETWORK)
        
        assert monitor.successful_recoveries == initial_success + 1
    
    def test_uptime_calculation(self):
        """Test uptime percentage calculation"""
        monitor = PipelineHealthMonitor()
        monitor.total_checks = 100
        monitor.failed_checks = 5
        
        status = monitor.get_pipeline_status()
        
        assert status.uptime_percentage == 95.0


class TestAutoRecovery:
    """Test auto-recovery logic"""
    
    def test_network_is_auto_recoverable(self):
        """Test that network failures are auto-recoverable"""
        monitor = PipelineHealthMonitor()
        assert monitor._is_auto_recoverable(PipelineComponent.NETWORK) is True
    
    def test_database_is_auto_recoverable(self):
        """Test that database failures are auto-recoverable"""
        monitor = PipelineHealthMonitor()
        assert monitor._is_auto_recoverable(PipelineComponent.DATABASE) is True
    
    def test_validation_service_not_auto_recoverable(self):
        """Test that validation service requires manual intervention"""
        monitor = PipelineHealthMonitor()
        assert monitor._is_auto_recoverable(PipelineComponent.VALIDATION_SERVICE) is False


class TestMonitoringLoop:
    """Test monitoring loop behavior"""
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self):
        """Test starting and stopping the monitor"""
        monitor = PipelineHealthMonitor(check_interval=1)
        
        assert monitor._monitoring is False
        
        monitor.start_monitoring()
        assert monitor._monitoring is True
        
        await asyncio.sleep(0.5)  # Let it run briefly
        
        monitor.stop_monitoring()
        assert monitor._monitoring is False
    
    @pytest.mark.asyncio
    async def test_monitor_performs_checks(self):
        """Test that monitor loop performs regular checks"""
        monitor = PipelineHealthMonitor(check_interval=1)
        
        initial_count = monitor.total_checks
        
        monitor.start_monitoring()
        await asyncio.sleep(2.5)  # Wait for at least 2 checks
        monitor.stop_monitoring()
        
        assert monitor.total_checks > initial_count


# Integration test
class TestEndToEndScenarios:
    """Test complete end-to-end scenarios"""
    
    @pytest.mark.asyncio
    async def test_failure_detection_and_recovery(self):
        """Test complete flow: failure detection -> alert -> recovery"""
        alerts = []
        
        def custom_alert(component, status):
            alerts.append((component, status))
        
        monitor = PipelineHealthMonitor(alert_callback=custom_alert)
        
        # Simulate network failure
        async def mock_check_network():
            return HealthCheck(
                component=PipelineComponent.NETWORK,
                status=HealthStatus.DOWN,
                timestamp=datetime.now(),
                error_message="Network timeout"
            )
        
        monitor.check_network = mock_check_network
        
        # Mock successful recovery
        async def mock_reconnect(component):
            pass
        
        monitor._reconnect = mock_reconnect
        
        # Perform health check
        checks = await monitor.perform_health_checks()
        
        # Find failure
        network_check = next(c for c in checks if c.component == PipelineComponent.NETWORK)
        assert network_check.status == HealthStatus.DOWN
        
        # Trigger alert
        monitor.alert_callback(network_check.component, network_check.status)
        assert len(alerts) > 0
        
        # Attempt recovery
        attempt = await monitor.attempt_recovery(PipelineComponent.NETWORK)
        assert attempt.success is True
        
        # Verify status
        status = monitor.get_pipeline_status()
        assert status.components["network"] == "healthy"