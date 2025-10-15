"""
FastAPI endpoints for pipeline monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any
import asyncio

from pipeline_monitor import (
    PipelineHealthMonitor,
    PipelineComponent,
    HealthStatus
)

app = FastAPI(
    title="Publishing Pipeline Monitor API",
    description="Monitor and recover the EssentiallySports publishing pipeline",
    version="1.0.0"
)

# Initialize monitor
monitor = PipelineHealthMonitor(check_interval=30)


@app.on_event("startup")
async def startup_event():
    """Start monitoring on application startup"""
    monitor.start_monitoring()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring on application shutdown"""
    monitor.stop_monitoring()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Publishing Pipeline Monitor",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "status": "/api/pipeline/status",
            "editor_message": "/api/pipeline/editor-message",
            "health": "/api/health",
            "recovery": "/api/pipeline/recovery/{component}",
            "metrics": "/api/pipeline/metrics"
        }
    }


@app.get("/api/health")
async def health_check():
    """Simple health check for the monitoring API itself"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """
    Get detailed pipeline status
    
    Returns:
        - Overall pipeline health
        - Individual component status
        - Recent failures
        - Suggested recovery actions
        - Auto-recovery capability
    """
    try:
        status = monitor.get_pipeline_status()
        
        return {
            "overall_status": status.overall_status.value,
            "components": status.components,
            "last_check": status.last_check.isoformat(),
            "uptime_percentage": round(status.uptime_percentage, 2),
            "recent_failures": status.recent_failures,
            "suggested_actions": status.suggested_actions,
            "is_auto_recoverable": status.is_auto_recoverable,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/editor-message")
async def get_editor_message():
    """
    Get clear, editor-facing status message
    
    Returns a simple message that editors can understand,
    with clear next steps based on current pipeline state.
    """
    try:
        message = monitor.get_editor_message()
        status = monitor.get_pipeline_status()
        
        return {
            "message": message,
            "status": status.overall_status.value,
            "can_publish": status.overall_status == HealthStatus.HEALTHY,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/recovery/{component}")
async def trigger_recovery(component: str):
    """
    Manually trigger recovery for a specific component
    
    Args:
        component: One of network, validation_service, database, storage, queue
    
    Returns:
        Recovery attempt result
    """
    try:
        # Validate component
        try:
            comp = PipelineComponent(component)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid component. Must be one of: {[c.value for c in PipelineComponent]}"
            )
        
        # Check if already healthy
        if monitor.component_status[comp] == HealthStatus.HEALTHY:
            return {
                "status": "success",
                "message": f"{component} is already healthy",
                "component": component,
                "timestamp": datetime.now().isoformat()
            }
        
        # Attempt recovery
        attempt = await monitor.attempt_recovery(comp)
        
        return {
            "status": "success" if attempt.success else "failed",
            "attempt_id": attempt.attempt_id,
            "component": component,
            "action": attempt.action.value,
            "duration_ms": round(attempt.duration_ms, 2),
            "error": attempt.error_message,
            "timestamp": attempt.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/metrics")
async def get_metrics():
    """
    Get pipeline metrics and statistics
    
    Returns:
        - Total health checks performed
        - Failed checks count
        - Success rate
        - Recovery statistics
        - Recent check history
    """
    try:
        status = monitor.get_pipeline_status()
        
        return {
            "total_checks": monitor.total_checks,
            "failed_checks": monitor.failed_checks,
            "success_rate": round(
                (monitor.total_checks - monitor.failed_checks) / monitor.total_checks * 100
                if monitor.total_checks > 0 else 100.0,
                2
            ),
            "recovery_stats": {
                "successful_recoveries": monitor.successful_recoveries,
                "failed_recoveries": monitor.failed_recoveries,
                "total_attempts": monitor.successful_recoveries + monitor.failed_recoveries,
                "success_rate": round(
                    monitor.successful_recoveries / (monitor.successful_recoveries + monitor.failed_recoveries) * 100
                    if (monitor.successful_recoveries + monitor.failed_recoveries) > 0 else 0.0,
                    2
                )
            },
            "current_status": {
                "overall": status.overall_status.value,
                "components": status.components
            },
            "recent_checks": len(monitor.recent_checks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/history")
async def get_history(limit: int = 50):
    """
    Get recent health check and recovery attempt history
    
    Args:
        limit: Number of recent events to return (default 50)
    
    Returns:
        Recent health checks and recovery attempts
    """
    try:
        recent_checks = [
            {
                "type": "health_check",
                "component": check.component.value,
                "status": check.status.value,
                "timestamp": check.timestamp.isoformat(),
                "latency_ms": check.latency_ms,
                "error": check.error_message
            }
            for check in monitor.recent_checks[-limit:]
        ]
        
        recent_recoveries = [
            {
                "type": "recovery_attempt",
                "attempt_id": attempt.attempt_id,
                "component": attempt.component.value,
                "action": attempt.action.value,
                "success": attempt.success,
                "timestamp": attempt.timestamp.isoformat(),
                "duration_ms": attempt.duration_ms,
                "error": attempt.error_message
            }
            for attempt in monitor.recovery_attempts[-limit:]
        ]
        
        # Combine and sort by timestamp
        all_events = recent_checks + recent_recoveries
        all_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "events": all_events[:limit],
            "total_events": len(all_events),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/force-check")
async def force_health_check():
    """
    Force an immediate health check on all components
    
    Returns:
        Results of the health check
    """
    try:
        checks = await monitor.perform_health_checks()
        
        return {
            "status": "completed",
            "checks": [
                {
                    "component": check.component.value,
                    "status": check.status.value,
                    "latency_ms": check.latency_ms,
                    "error": check.error_message
                }
                for check in checks
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)