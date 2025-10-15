# Publishing Pipeline Recovery System

A comprehensive health monitoring and auto-recovery system for EssentiallySports's article publishing pipeline. This system automatically detects failures, attempts recovery, and provides clear operational visibility for editors and engineers.

## Features

- 🔍 **Real-time Health Monitoring**: Continuous monitoring of all pipeline components
- 🔄 **Auto-Recovery**: Automatic recovery attempts for common failure scenarios
- 🚨 **Intelligent Alerting**: Immediate alerts when failures are detected
- 📊 **Operational Dashboard**: Clear status reporting for editors and engineers
- 📝 **Comprehensive Audit Logs**: Detailed logging of all events and recovery attempts
- 📈 **Metrics & Analytics**: Track uptime, recovery success rates, and system health

## Components Monitored

1. **Network**: Internet connectivity and external service access
2. **Validation Service**: Article validation microservice
3. **Database**: PostgreSQL/MySQL connection and health
4. **Storage**: File storage system (S3, local, etc.)
5. **Message Queue**: RabbitMQ/Redis queue broker

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Pipeline Monitor                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Health Check Components                   │  │
│  │  • Network      • Validation    • Database        │  │
│  │  • Storage      • Queue                           │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Failure Detection & Alerting              │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Auto-Recovery Engine                      │  │
│  │  • Reconnect    • Restart      • Failover         │  │
│  │  • Clear Queue  • Manual Intervention             │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Audit Logger & Metrics                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd pipeline-recovery
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the system**:
```bash
# Start the API server
python api.py

# Or with custom settings
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### API Endpoints

#### 1. Get Pipeline Status
```bash
GET /api/pipeline/status
```

Returns detailed pipeline health information:
```json
{
  "overall_status": "healthy",
  "components": {
    "network": "healthy",
    "validation_service": "healthy",
    "database": "healthy",
    "storage": "healthy",
    "queue": "healthy"
  },
  "uptime_percentage": 99.5,
  "recent_failures": [],
  "suggested_actions": ["✅ All systems operational. No action needed."],
  "is_auto_recoverable": true
}
```

#### 2. Get Editor-Facing Message
```bash
GET /api/pipeline/editor-message
```

Returns a clear, human-readable status message:
```json
{
  "message": "✅ **Publishing Pipeline: OPERATIONAL**\n\nAll systems are running normally...",
  "status": "healthy",
  "can_publish": true,
  "timestamp": "2025-10-15T14:23:15.123456"
}
```

#### 3. Trigger Manual Recovery
```bash
POST /api/pipeline/recovery/{component}
```

Example:
```bash
curl -X POST http://localhost:8000/api/pipeline/recovery/network
```

#### 4. Get Metrics
```bash
GET /api/pipeline/metrics
```

Returns system metrics:
```json
{
  "total_checks": 1000,
  "failed_checks": 5,
  "success_rate": 99.5,
  "recovery_stats": {
    "successful_recoveries": 8,
    "failed_recoveries": 2,
    "success_rate": 80.0
  }
}
```

#### 5. Force Immediate Health Check
```bash
POST /api/pipeline/force-check
```

#### 6. Get Event History
```bash
GET /api/pipeline/history?limit=50
```

### Python API Usage

```python
from pipeline_monitor import PipelineHealthMonitor, PipelineComponent
import asyncio

# Initialize monitor
monitor = PipelineHealthMonitor(check_interval=30)

# Start monitoring
monitor.start_monitoring()

# Get status
status = monitor.get_pipeline_status()
print(f"Overall Status: {status.overall_status.value}")
print(f"Uptime: {status.uptime_percentage}%")

# Get editor message
message = monitor.get_editor_message()
print(message)

# Manual recovery
attempt = asyncio.run(
    monitor.attempt_recovery(PipelineComponent.NETWORK)
)
print(f"Recovery Success: {attempt.success}")

# Stop monitoring
monitor.stop_monitoring()
```

## Log Interpretation

### Log Format

All logs follow this format:
```
TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE
```

### Log Types

#### 1. Health Check Logs
```
INFO - HEALTH_CHECK: {"component": "network", "status": "healthy", "latency_ms": 52.3}
```
- **Frequency**: Every check interval (default: 30s)
- **Interpretation**: Component health status with latency

#### 2. Failure Detection Logs
```
ERROR - FAILURE_DETECTED: component=database, error=Database connection lost
```
- **Frequency**: When failures occur
- **Action Required**: Check if auto-recovery succeeded or manual intervention needed

#### 3. Alert Logs
```
WARNING - ALERT_TRIGGERED: component=database, severity=CRITICAL
```
- **Frequency**: Immediately after failure detection
- **Action Required**: Check dashboard or respond to notification

#### 4. Recovery Attempt Logs
```
INFO - RECOVERY_ATTEMPT: {"attempt_id": "network_123", "success": true, "duration_ms": 300.5}
```
- **Frequency**: When recovery is attempted
- **Interpretation**: 
  - `success: true` → Component recovered automatically
  - `success: false` → Recovery failed, check error_message

### Common Scenarios

#### Scenario 1: Successful Auto-Recovery
```
ERROR - FAILURE_DETECTED: component=network, error=Network timeout
WARNING - ALERT_TRIGGERED: component=network, severity=CRITICAL
INFO - RECOVERY_ATTEMPT: {..., "success": true}
INFO - HEALTH_CHECK: {"component": "network", "status": "healthy"}
```
**Action**: None required. System recovered automatically.

#### Scenario 2: Failed Recovery (Manual Intervention Required)
```
ERROR - FAILURE_DETECTED: component=validation_service, error=Service unresponsive
WARNING - ALERT_TRIGGERED: component=validation_service, severity=CRITICAL
ERROR - RECOVERY_ATTEMPT: {..., "success": false, "error_message": "Service restart failed"}
```
**Action**: Contact engineering team immediately. Include the `attempt_id` from logs.

#### Scenario 3: Multiple Component Failures
```
ERROR - FAILURE_DETECTED: component=database, error=Connection lost
ERROR - FAILURE_DETECTED: component=queue, error=Broker connection failed
INFO - RECOVERY_ATTEMPT: {"component": "database", "success": true}
INFO - RECOVERY_ATTEMPT: {"component": "queue", "success": true}
```
**Action**: Monitor closely. Check for underlying infrastructure issues.

## Recovery Actions by Component

| Component | Auto-Recoverable | Recovery Action | Manual Steps if Failed |
|-----------|-----------------|----------------|----------------------|
| Network | ✅ Yes | Reconnect | Check firewall, DNS, internet connectivity |
| Validation Service | ❌ No | Restart Service | SSH to server, check logs, restart manually |
| Database | ✅ Yes | Reconnect | Verify DB server, check credentials, restart connection pool |
| Storage | ✅ Yes | Failover | Check storage service, verify credentials, check disk space |
| Queue | ✅ Yes | Clear Queue | Check broker status, clear stuck messages, restart broker |

## Testing

### Run All Tests
```bash
pytest test_pipeline_monitor.py -v
```

### Run Specific Test Categories
```bash
# Test health checks
pytest test_pipeline_monitor.py::TestHealthChecks -v

# Test recovery scenarios
pytest test_pipeline_monitor.py::TestRecoverySuccess -v
pytest test_pipeline_monitor.py::TestRecoveryFailure -v

# Test alerting
pytest test_pipeline_monitor.py::TestAlertSystem -v

# Test end-to-end scenarios
pytest test_pipeline_monitor.py::TestEndToEndScenarios -v
```

### Test Coverage
```bash
pytest --cov=pipeline_monitor --cov-report=html
```

## Configuration

### Environment Variables

```bash
# Check interval (seconds)
PIPELINE_CHECK_INTERVAL=30

# Alert webhook URL
ALERT_WEBHOOK_URL=https://your-webhook.com/alerts

# Log file location
AUDIT_LOG_FILE=pipeline_audit.log

# Database connection
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Custom Configuration

```python
from pipeline_monitor import PipelineHealthMonitor

monitor = PipelineHealthMonitor(
    check_interval=60,  # Check every 60 seconds
    alert_callback=custom_alert_function
)
```

## Troubleshooting

### Issue: Monitor not starting
```bash
# Check if port is already in use
lsof -i :8000

# Run with different port
uvicorn api:app --port 8001
```

### Issue: High false positive rate
- Increase check interval to reduce network noise
- Adjust failure thresholds in health check methods
- Check network stability

### Issue: Recovery attempts timing out
- Check system resources (CPU, memory)
- Verify network connectivity to services
- Review service health independently

### Issue: Logs not appearing
- Check file permissions on log directory
- Verify `AUDIT_LOG_FILE` path exists
- Check disk space

## Dashboard Integration

The system provides a REST API that can be integrated with any dashboard:

```javascript
// Example: Fetch status for dashboard
async function updateDashboard() {
    const response = await fetch('http://localhost:8000/api/pipeline/status');
    const data = await response.json();
    
    updateStatusIndicator(data.overall_status);
    updateComponentHealth(data.components);
    updateMetrics(data.uptime_percentage);
}
```

## Alerting Integration

### Slack Integration
```python
def slack_alert(component, status):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    message = {
        "text": f"🚨 Pipeline Alert: {component.value} is {status.value}",
        "channel": "#publishing-alerts"
    }
    requests.post(webhook_url, json=message)

monitor = PipelineHealthMonitor(alert_callback=slack_alert)
```

### Email Integration
```python
def email_alert(component, status):
    send_email(
        to="engineering@example.com",
        subject=f"Pipeline Alert: {component.value}",
        body=f"Component {component.value} is {status.value}"
    )

monitor = PipelineHealthMonitor(alert_callback=email_alert)
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t pipeline-monitor .
docker run -p 8000:8000 pipeline-monitor
```

### Using Systemd

Create `/etc/systemd/system/pipeline-monitor.service`:
```ini
[Unit]
Description=Pipeline Health Monitor
After=network.target

[Service]
Type=simple
User=pipeline
WorkingDirectory=/opt/pipeline-monitor
ExecStart=/usr/bin/python3 /opt/pipeline-monitor/api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pipeline-monitor
sudo systemctl start pipeline-monitor
```

## Monitoring Best Practices

1. **Set appropriate check intervals**: Too frequent checks can cause noise; too infrequent can delay detection
2. **Review logs regularly**: Weekly review of audit logs helps identify patterns
3. **Test recovery procedures**: Periodically test manual recovery steps
4. **Monitor the monitor**: Use external monitoring to ensure the monitor itself is healthy
5. **Document custom procedures**: Add component-specific recovery steps to runbooks

## Support

For issues or questions:
- Check audit logs: `tail -f pipeline_audit.log`
- Review metrics: `GET /api/pipeline/metrics`
- Contact: engineering@essentiallysports.com

## License

Internal use only - EssentiallySports