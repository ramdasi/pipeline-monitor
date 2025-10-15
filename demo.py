"""
Interactive demo of the Pipeline Monitoring System
Simulates various failure and recovery scenarios
"""

import asyncio
from datetime import datetime
from pipeline_monitor import (
    PipelineHealthMonitor,
    PipelineComponent,
    HealthStatus,
    HealthCheck
)


def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


async def demo_healthy_system():
    """Demo 1: All systems healthy"""
    print_separator("DEMO 1: Healthy System")
    
    monitor = PipelineHealthMonitor()
    
    print("Performing health checks...")
    checks = await monitor.perform_health_checks()
    
    for check in checks:
        status_icon = "✅" if check.status == HealthStatus.HEALTHY else "❌"
        print(f"{status_icon} {check.component.value}: {check.status.value} "
              f"(latency: {check.latency_ms:.2f}ms)" if check.latency_ms else f"{status_icon} {check.component.value}: {check.status.value}")
    
    status = monitor.get_pipeline_status()
    print(f"\nOverall Status: {status.overall_status.value}")
    print(f"Uptime: {status.uptime_percentage:.2f}%")
    
    print("\n--- Editor Message ---")
    print(monitor.get_editor_message())


async def demo_network_failure_recovery():
    """Demo 2: Network failure with successful recovery"""
    print_separator("DEMO 2: Network Failure → Auto-Recovery Success")
    
    monitor = PipelineHealthMonitor()
    
    # Simulate network failure
    print("⚠️  Simulating network failure...")
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
    print(f"❌ Network Status: {network_check.status.value}")
    print(f"   Error: {network_check.error_message}")
    
    # Show status before recovery
    status = monitor.get_pipeline_status()
    print(f"\n📊 Pipeline Status: {status.overall_status.value}")
    print(f"🔧 Suggested Actions:")
    for action in status.suggested_actions:
        print(f"   {action}")
    
    # Attempt recovery
    print("\n🔄 Attempting auto-recovery...")
    
    # Mock successful recovery
    async def mock_reconnect(component):
        await asyncio.sleep(0.3)
        print("   → Reconnecting to network...")
        await asyncio.sleep(0.2)
        print("   → Verifying connection...")
    
    monitor._reconnect = mock_reconnect
    attempt = await monitor.attempt_recovery(PipelineComponent.NETWORK)
    
    if attempt.success:
        print(f"✅ Recovery Successful!")
        print(f"   Duration: {attempt.duration_ms:.2f}ms")
        print(f"   Action: {attempt.action.value}")
    
    # Show final status
    status = monitor.get_pipeline_status()
    print(f"\n📊 Final Pipeline Status: {status.overall_status.value}")
    
    print("\n--- Editor Message ---")
    print(monitor.get_editor_message())


async def demo_validation_service_failure():
    """Demo 3: Validation service failure (requires manual intervention)"""
    print_separator("DEMO 3: Validation Service Crash → Manual Intervention Required")
    
    monitor = PipelineHealthMonitor()
    
    # Simulate validation service failure
    print("⚠️  Simulating validation service crash...")
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
    print(f"❌ Validation Service Status: {val_check.status.value}")
    print(f"   Error: {val_check.error_message}")
    
    # Show status
    status = monitor.get_pipeline_status()
    print(f"\n📊 Pipeline Status: {status.overall_status.value}")
    print(f"🔧 Auto-Recoverable: {status.is_auto_recoverable}")
    print(f"\n💡 Suggested Actions:")
    for action in status.suggested_actions:
        print(f"   {action}")
    
    # Attempt recovery (will fail)
    print("\n🔄 Attempting auto-recovery...")
    
    async def mock_restart_service(component):
        await asyncio.sleep(0.3)
        print("   → Attempting service restart...")
        await asyncio.sleep(0.2)
        raise Exception("Service restart failed - requires manual intervention")
    
    monitor._restart_service = mock_restart_service
    attempt = await monitor.attempt_recovery(PipelineComponent.VALIDATION_SERVICE)
    
    if not attempt.success:
        print(f"❌ Recovery Failed!")
        print(f"   Error: {attempt.error_message}")
        print(f"   Duration: {attempt.duration_ms:.2f}ms")
    
    print("\n--- Editor Message ---")
    print(monitor.get_editor_message())


async def demo_multiple_failures():
    """Demo 4: Multiple component failures"""
    print_separator("DEMO 4: Multiple Component Failures")
    
    monitor = PipelineHealthMonitor()
    
    print("⚠️  Simulating multiple failures...")
    
    # Simulate database failure
    async def mock_check_database():
        return HealthCheck(
            component=PipelineComponent.DATABASE,
            status=HealthStatus.DOWN,
            timestamp=datetime.now(),
            error_message="Database connection lost"
        )
    
    # Simulate queue failure
    async def mock_check_queue():
        return HealthCheck(
            component=PipelineComponent.QUEUE,
            status=HealthStatus.DOWN,
            timestamp=datetime.now(),
            error_message="Queue broker connection failed"
        )
    
    monitor.check_database = mock_check_database
    monitor.check_queue = mock_check_queue
    
    checks = await monitor.perform_health_checks()
    
    print("\n❌ Failed Components:")
    for check in checks:
        if check.status != HealthStatus.HEALTHY:
            print(f"   • {check.component.value}: {check.error_message}")
    
    # Show status
    status = monitor.get_pipeline_status()
    print(f"\n📊 Pipeline Status: {status.overall_status.value}")
    print(f"🔧 Auto-Recoverable: {status.is_auto_recoverable}")
    
    # Attempt recovery for both
    print("\n🔄 Attempting auto-recovery for all failed components...")
    
    async def mock_reconnect(component):
        await asyncio.sleep(0.2)
    
    async def mock_clear_queue(component):
        await asyncio.sleep(0.2)
    
    monitor._reconnect = mock_reconnect
    monitor._clear_queue = mock_clear_queue
    
    for check in checks:
        if check.status != HealthStatus.HEALTHY:
            print(f"\n   → Recovering {check.component.value}...")
            attempt = await monitor.attempt_recovery(check.component)
            if attempt.success:
                print(f"      ✅ Recovered ({attempt.duration_ms:.2f}ms)")
            else:
                print(f"      ❌ Failed: {attempt.error_message}")
    
    # Show final status
    status = monitor.get_pipeline_status()
    print(f"\n📊 Final Pipeline Status: {status.overall_status.value}")


async def demo_monitoring_loop():
    """Demo 5: Continuous monitoring"""
    print_separator("DEMO 5: Continuous Monitoring (10 seconds)")
    
    monitor = PipelineHealthMonitor(check_interval=2)
    
    print("Starting continuous monitoring...")
    print("(Monitoring for 10 seconds, then stopping)\n")
    
    # Custom alert handler
    def demo_alert(component, status):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🚨 ALERT: {component.value} is {status.value}")
    
    monitor.alert_callback = demo_alert
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Let it run for 10 seconds
    for i in range(10):
        await asyncio.sleep(1)
        if i % 2 == 0:
            status = monitor.get_pipeline_status()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {status.overall_status.value}, "
                  f"Checks: {monitor.total_checks}, "
                  f"Uptime: {status.uptime_percentage:.1f}%")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    print("\nMonitoring stopped.")
    print(f"\nFinal Statistics:")
    print(f"  Total Checks: {monitor.total_checks}")
    print(f"  Failed Checks: {monitor.failed_checks}")
    print(f"  Successful Recoveries: {monitor.successful_recoveries}")
    print(f"  Failed Recoveries: {monitor.failed_recoveries}")


async def demo_metrics():
    """Demo 6: System metrics"""
    print_separator("DEMO 6: System Metrics & Statistics")
    
    monitor = PipelineHealthMonitor()
    
    # Simulate some activity
    print("Simulating system activity...\n")
    
    for i in range(10):
        await monitor.perform_health_checks()
        await asyncio.sleep(0.1)
    
    # Simulate some failures and recoveries
    monitor.failed_checks = 3
    monitor.successful_recoveries = 5
    monitor.failed_recoveries = 1
    
    status = monitor.get_pipeline_status()
    
    print("📊 System Metrics:")
    print(f"  Total Health Checks: {monitor.total_checks}")
    print(f"  Failed Checks: {monitor.failed_checks}")
    print(f"  Success Rate: {((monitor.total_checks - monitor.failed_checks) / monitor.total_checks * 100):.2f}%")
    print(f"\n🔧 Recovery Statistics:")
    print(f"  Successful Recoveries: {monitor.successful_recoveries}")
    print(f"  Failed Recoveries: {monitor.failed_recoveries}")
    print(f"  Recovery Success Rate: {(monitor.successful_recoveries / (monitor.successful_recoveries + monitor.failed_recoveries) * 100):.2f}%")
    print(f"\n📈 Current Status:")
    print(f"  Overall: {status.overall_status.value}")
    print(f"  Uptime: {status.uptime_percentage:.2f}%")
    print(f"  Components Healthy: {sum(1 for s in status.components.values() if s == 'healthy')}/{len(status.components)}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  PIPELINE MONITORING SYSTEM - INTERACTIVE DEMO")
    print("="*60)
    
    demos = [
        ("Healthy System", demo_healthy_system),
        ("Network Failure & Recovery", demo_network_failure_recovery),
        ("Validation Service Failure", demo_validation_service_failure),
        ("Multiple Failures", demo_multiple_failures),
        ("Continuous Monitoring", demo_monitoring_loop),
        ("System Metrics", demo_metrics),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run All Demos")
    print(f"  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-7): ").strip()
            
            if choice == "0":
                print("\nExiting demo. Goodbye!")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(demos) + 1:
                # Run all demos
                for name, demo_func in demos:
                    await demo_func()
                    await asyncio.sleep(1)
                print_separator("All demos completed!")
                break
            elif 1 <= choice_num <= len(demos):
                # Run selected demo
                _, demo_func = demos[choice_num - 1]
                await demo_func()
            else:
                print("Invalid choice. Please select 0-7.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted. Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())