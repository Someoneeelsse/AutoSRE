import asyncio
import json
import os
import psutil
import time
import re
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Initialize FastAPI app
app = FastAPI(title="AutoSRE Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
    ],  # Frontend and Grafana URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection Manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Alert thresholds
ALERT_THRESHOLDS = {
    "cpu_usage": 80.0,
    "memory_usage": 85.0,
    "disk_usage": 90.0,
    "error_rate": 10.0
}

class AlertManager:
    def __init__(self):
        self.active_alerts = set()
    
    def check_alerts(self, metrics: dict, analysis: dict) -> List[dict]:
        alerts = []
        
        # CPU alert
        if metrics.get("cpu", {}).get("usage_percent", 0) > ALERT_THRESHOLDS["cpu_usage"]:
            alert_id = "high_cpu"
            if alert_id not in self.active_alerts:
                alerts.append({
                    "id": alert_id,
                    "type": "warning",
                    "title": "High CPU Usage",
                    "message": f"CPU usage is {metrics['cpu']['usage_percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
                self.active_alerts.add(alert_id)
        else:
            self.active_alerts.discard("high_cpu")
        
        # Memory alert
        if metrics.get("memory", {}).get("usage_percent", 0) > ALERT_THRESHOLDS["memory_usage"]:
            alert_id = "high_memory"
            if alert_id not in self.active_alerts:
                alerts.append({
                    "id": alert_id,
                    "type": "warning",
                    "title": "High Memory Usage",
                    "message": f"Memory usage is {metrics['memory']['usage_percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
                self.active_alerts.add(alert_id)
        else:
            self.active_alerts.discard("high_memory")
        
        # Error rate alert
        if analysis and analysis.get("success_rate", 100) < (100 - ALERT_THRESHOLDS["error_rate"]):
            alert_id = "high_error_rate"
            if alert_id not in self.active_alerts:
                alerts.append({
                    "id": alert_id,
                    "type": "critical",
                    "title": "High Error Rate",
                    "message": f"Error rate is {100 - analysis['success_rate']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
                self.active_alerts.add(alert_id)
        else:
            self.active_alerts.discard("high_error_rate")
        
        return alerts

alert_manager = AlertManager()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('websocket_active_connections', 'Number of active WebSocket connections')
ERROR_COUNT = Counter('application_errors_total', 'Total application errors')
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage_percent', 'System disk usage percentage')

# Log file path for real nginx logs
LOG_FILE_PATH = "/app/nginx-logs/logs/access.log"
ERROR_LOG_FILE_PATH = "/app/nginx-logs/logs/error.log"

# Global variables for storing data
connected_clients = []
app_start_time = time.time()  # Track when the application started

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend is accessible"""
    return {"message": "Backend is accessible", "timestamp": datetime.now().isoformat()}

@app.get("/api/metrics")
async def get_system_metrics():
    """Get real-time system metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # Network metrics
        network = psutil.net_io_counters()
        network_bytes_sent = network.bytes_sent
        network_bytes_recv = network.bytes_recv
        
        # Application uptime (since service started)
        uptime_seconds = time.time() - app_start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        # Active connections (estimate based on open files)
        try:
            active_connections = len(psutil.net_connections())
        except:
            active_connections = len(psutil.Process().open_files())
        
        # Update Prometheus metrics
        SYSTEM_CPU_USAGE.set(cpu_percent)
        SYSTEM_MEMORY_USAGE.set(memory_percent)
        SYSTEM_DISK_USAGE.set(disk_percent)
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count
            },
            "memory": {
                "usage_percent": memory_percent,
                "used_gb": round(memory_used_gb, 2),
                "total_gb": round(memory_total_gb, 2)
            },
            "disk": {
                "usage_percent": disk_percent,
                "used_gb": round(disk_used_gb, 2),
                "total_gb": round(disk_total_gb, 2)
            },
            "network": {
                "bytes_sent": network_bytes_sent,
                "bytes_recv": network_bytes_recv
            },
            "uptime": {
                "hours": uptime_hours,
                "minutes": uptime_minutes
            },
            "active_connections": active_connections,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        ERROR_COUNT.inc()
        return {"error": str(e)}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    print("Metrics endpoint accessed")
    try:
        metrics_data = generate_latest()
        print(f"Generated metrics data length: {len(metrics_data)}")
        return Response(metrics_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        print(f"Error generating metrics: {e}")
        ERROR_COUNT.inc()
        return Response(f"Error generating metrics: {str(e)}", status_code=500)

@app.get("/metrics/api/v1/query")
async def prometheus_query():
    """Prometheus query endpoint for instant queries"""
    print("Prometheus query endpoint accessed")
    try:
        # Get current metric values properly
        cpu_value = SYSTEM_CPU_USAGE._value.get() if hasattr(SYSTEM_CPU_USAGE, '_value') else 0
        memory_value = SYSTEM_MEMORY_USAGE._value.get() if hasattr(SYSTEM_MEMORY_USAGE, '_value') else 0
        disk_value = SYSTEM_DISK_USAGE._value.get() if hasattr(SYSTEM_DISK_USAGE, '_value') else 0
        connections_value = ACTIVE_CONNECTIONS._value.get() if hasattr(ACTIVE_CONNECTIONS, '_value') else 0
        
        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "system_cpu_usage_percent"},
                        "value": [int(time.time()), str(cpu_value)]
                    },
                    {
                        "metric": {"__name__": "system_memory_usage_percent"},
                        "value": [int(time.time()), str(memory_value)]
                    },
                    {
                        "metric": {"__name__": "system_disk_usage_percent"},
                        "value": [int(time.time()), str(disk_value)]
                    },
                    {
                        "metric": {"__name__": "websocket_active_connections"},
                        "value": [int(time.time()), str(connections_value)]
                    }
                ]
            }
        }
    except Exception as e:
        print(f"Error in prometheus query: {e}")
        ERROR_COUNT.inc()
        return {"status": "error", "error": str(e)}

@app.get("/metrics/api/v1/query_range")
async def prometheus_query_range():
    """Prometheus query_range endpoint for range queries"""
    print("Prometheus query_range endpoint accessed")
    try:
        # Get current metric values properly
        cpu_value = SYSTEM_CPU_USAGE._value.get() if hasattr(SYSTEM_CPU_USAGE, '_value') else 0
        memory_value = SYSTEM_MEMORY_USAGE._value.get() if hasattr(SYSTEM_MEMORY_USAGE, '_value') else 0
        disk_value = SYSTEM_DISK_USAGE._value.get() if hasattr(SYSTEM_DISK_USAGE, '_value') else 0
        connections_value = ACTIVE_CONNECTIONS._value.get() if hasattr(ACTIVE_CONNECTIONS, '_value') else 0
        
        current_time = int(time.time())
        
        # Generate some sample data points for the last hour
        data_points = []
        for i in range(12):  # 12 points, 5 minutes apart
            timestamp = current_time - (11 - i) * 300  # 5 minutes = 300 seconds
            data_points.append([timestamp, str(cpu_value)])
        
        return {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"__name__": "system_cpu_usage_percent"},
                        "values": data_points
                    },
                    {
                        "metric": {"__name__": "system_memory_usage_percent"},
                        "values": [[current_time, str(memory_value)]]
                    },
                    {
                        "metric": {"__name__": "system_disk_usage_percent"},
                        "values": [[current_time, str(disk_value)]]
                    },
                    {
                        "metric": {"__name__": "websocket_active_connections"},
                        "values": [[current_time, str(connections_value)]]
                    }
                ]
            }
        }
    except Exception as e:
        print(f"Error in prometheus query_range: {e}")
        ERROR_COUNT.inc()
        return {"status": "error", "error": str(e)}

@app.get("/get_logs/")
async def get_logs():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        return {"logs": logs}
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

@app.get("/get_error_logs/")
async def get_error_logs():
    if os.path.exists(ERROR_LOG_FILE_PATH):
        with open(ERROR_LOG_FILE_PATH, "r") as file:
            error_logs = file.read()
        return {"error_logs": error_logs}
    else:
        return {"error": "Error log file not found", "path": ERROR_LOG_FILE_PATH}

@app.get("/summarize_logs/")
async def summarize_logs_endpoint():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        log_summary = analyze_logs_simple(logs)
        return {"summary": log_summary}
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

@app.get("/analyze_logs/")
async def analyze_logs_endpoint():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        return analyze_logs(logs)
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

def parse_logs(logs: str) -> List[str]:
    """
    Parse logs and return lines that contain 5xx errors.
    """
    error_logs = []
    for line in logs.splitlines():
        if re.search(r'\s5\d{2}\s', line):  # Match 5xx errors (server errors)
            error_logs.append(line)
    return error_logs

def analyze_logs_simple(logs: str) -> str:
    """
    Simple log analysis without external AI service.
    """
    lines = logs.splitlines()
    total_requests = len(lines)
    
    # Count status codes
    status_counts = {}
    error_requests = []
    
    for line in lines:
        # Extract status code from log line
        status_match = re.search(r'"\s(\d{3})\s', line)
        if status_match:
            status = status_match.group(1)
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Collect error requests (4xx and 5xx)
            if status.startswith('4') or status.startswith('5'):
                error_requests.append(line)
    
    # Create a simple summary
    summary = f"Log Analysis Summary:\n"
    summary += f"- Total requests: {total_requests}\n"
    summary += f"- Error requests: {len(error_requests)}\n"
    success_rate = ((total_requests - len(error_requests)) / total_requests * 100) if total_requests > 0 else 0
    summary += f"- Success rate: {success_rate:.1f}%\n"
    
    if error_requests:
        summary += f"- Most common error status codes: {', '.join([k for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True) if k.startswith('4') or k.startswith('5')][:3])}\n"
    
    return summary

def analyze_logs(logs: str) -> Dict:
    """
    Analyze logs and provide basic statistics.
    """
    lines = logs.splitlines()
    total_requests = len(lines)
    
    # Count status codes
    status_counts = {}
    error_requests = []
    
    for line in lines:
        # Extract status code from log line
        status_match = re.search(r'"\s(\d{3})\s', line)
        if status_match:
            status = status_match.group(1)
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Collect error requests (4xx and 5xx)
            if status.startswith('4') or status.startswith('5'):
                error_requests.append(line)
    
    return {
        "total_requests": total_requests,
        "status_code_distribution": status_counts,
        "error_count": len(error_requests),
        "success_rate": ((total_requests - len(error_requests)) / total_requests * 100) if total_requests > 0 else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

async def send_initial_data(websocket: WebSocket):
    """Send initial data when WebSocket connects."""
    try:
        print("Sending initial data...")
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r") as file:
                logs = file.read()
            
            # Send initial data with simple analysis
            data = {
                "type": "initial_data",
                "logs": logs,
                "analysis": analyze_logs(logs),
                "error_logs": parse_logs(logs),
                "summary": analyze_logs_simple(logs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(data))
            print("Initial data sent successfully")
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Log file not found: {LOG_FILE_PATH}"
            }))
    except Exception as e:
        print(f"Error sending initial data: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error loading initial data: {str(e)}"
        }))

async def check_for_updates(websocket: WebSocket):
    """Check for new logs and send updates."""
    try:
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r") as file:
                logs = file.read()
            
            # Send updated analysis
            data = {
                "type": "update",
                "analysis": analyze_logs(logs),
                "summary": analyze_logs_simple(logs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(data))
        else:
            # Log file doesn't exist, send empty update
            data = {
                "type": "update",
                "analysis": {
                    "total_requests": 0,
                    "status_code_distribution": {},
                    "error_count": 0,
                    "success_rate": 100.0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "summary": "No log file found",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(data))
    except Exception as e:
        print(f"Error checking for updates: {e}")
        # Don't break the connection, just log the error
        # The WebSocket will continue running

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    ACTIVE_CONNECTIONS.inc()
    
    try:
        print("WebSocket connection established, sending initial data...")
        await send_initial_data(websocket)
        print("Starting WebSocket update loop...")
        while True:
            await asyncio.sleep(5)
            try:
                print("Sending update...")
                await check_for_updates(websocket)
                print("Update sent successfully")
            except WebSocketDisconnect:
                print("WebSocket disconnected by client")
                break
            except Exception as e:
                print(f"WebSocket error during update: {e}")
                # Don't break the connection for minor errors, just continue
                continue
    except WebSocketDisconnect:
        print("WebSocket disconnected (client closed connection)")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
        ACTIVE_CONNECTIONS.dec()
        print("WebSocket cleanup complete.")

# New endpoints for external application integration
@app.post("/api/metrics/custom")
async def receive_custom_metrics(metrics: dict):
    """Receive custom metrics from external applications"""
    try:
        # Store or process custom metrics
        timestamp = datetime.utcnow().isoformat()
        metrics_data = {
            "timestamp": timestamp,
            "app_name": metrics.get("app_name", "unknown"),
            "metrics": metrics,
            "source": "external_app"
        }
        
        # You could store this in a database or process it
        print(f"Received custom metrics: {metrics_data}")
        
        # Update Prometheus metrics if needed
        if "response_time" in metrics:
            REQUEST_DURATION.observe(metrics["response_time"] / 1000.0)  # Convert to seconds
        
        if "status_code" in metrics:
            status = str(metrics["status_code"])
            REQUEST_COUNT.labels(method="POST", endpoint=metrics.get("endpoint", "/"), status=status).inc()
        
        return {"status": "success", "message": "Metrics received", "timestamp": timestamp}
    except Exception as e:
        ERROR_COUNT.inc()
        return {"status": "error", "message": str(e)}

@app.post("/api/logs")
async def receive_logs(log_data: dict):
    """Receive log entries from external applications"""
    try:
        logs = log_data.get("logs", [])
        app_name = log_data.get("app_name", "unknown")
        timestamp = datetime.utcnow().isoformat()
        
        # Process and store logs
        log_entries = []
        for log in logs:
            log_entries.append({
                "timestamp": timestamp,
                "app_name": app_name,
                "log_entry": log,
                "source": "external_app"
            })
        
        print(f"Received {len(log_entries)} log entries from {app_name}")
        
        # You could append to existing log files or store in database
        # For now, we'll just acknowledge receipt
        
        return {
            "status": "success", 
            "message": f"Received {len(log_entries)} log entries",
            "timestamp": timestamp
        }
    except Exception as e:
        ERROR_COUNT.inc()
        return {"status": "error", "message": str(e)}

@app.get("/api/applications")
async def list_connected_applications():
    """List all connected applications and their status"""
    # This would typically query a database
    # For now, return a mock response
    return {
        "applications": [
            {
                "name": "my-app",
                "status": "connected",
                "last_seen": datetime.utcnow().isoformat(),
                "metrics_count": 150,
                "logs_count": 1000
            }
        ],
        "total_applications": 1
    }

@app.get("/api/applications/{app_name}/metrics")
async def get_application_metrics(app_name: str):
    """Get metrics for a specific application"""
    # This would query stored metrics for the app
    return {
        "app_name": app_name,
        "metrics": {
            "total_requests": 1500,
            "error_rate": 2.1,
            "avg_response_time": 145.6,
            "active_connections": 25
        },
        "last_updated": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 