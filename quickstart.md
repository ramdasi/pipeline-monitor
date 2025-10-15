# Quick Start Guide

Get the Pipeline Monitoring System running in under 5 minutes.

## 1. Installation (1 minute)

```bash
# Clone or download the files
cd pipeline-recovery

# Install dependencies
pip install -r requirements.txt
```

## 2. Run the System (30 seconds)

### Option A: API Server (Recommended for Production)

```bash
# Start the API server
python api.py

# Or with uvicorn
uvicorn api:app --reload
```

The server will start on `http://localhost:8000`

### Option B: Interactive Demo (Recommended for Testing)

```bash
# Run the interactive demo
python demo.py
```

## 3. Test the System (1 minute)

### Check Health Status

```bash
curl http://localhost:8000/api/pipeline/status
```

Expected response:
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
  "uptime_percentage": 100.0
}
```

### Get Editor Message

```bash
curl http://localhost:8000/api/pipeline/editor-message
```

### View Metrics

```bash
curl http://localhost:8000/api/pipeline/metrics
```

## 4. Monitor in Real-Time (ongoing)

### View Logs

```bash
# Watch audit logs in real-time
tail -f pipeline_audit.log
```

### Check Dashboard

Open `http://localhost:8000` in your browser to see available endpoints.

## Common Use Cases

### For Editors: Check if Publishing is Available

```bash
curl http://localhost:8000/api/pipeline/editor-message
```

Look for:
- ✅ = You can publish
- 🔄 = Wait a moment, system recovering
- 🚨 = Contact engineering

### For Engineers: Diagnose Issues

```bash
# Get detailed status
curl http://localhost:8000/api/pipeline/status | jq

# Check recent failures
curl http://localhost:8000/api/pipeline/history?limit=10 | jq

# View metrics
curl http://localhost:8000/api/pipeline/metrics | jq
```

### Trigger Manual Recovery

```bash
# Recover specific component
curl -X POST http://localhost:8000/api/pipeline/recovery/network

# Force immediate health check
curl -X POST http://localhost:8000/api/pipeline/force-check
```

## Running Tests

```bash
# Run all tests
pytest test_pipeline_monitor.py -v

# Run specific test
pytest test_pipeline_monitor.py::TestRecoverySuccess -v
```
