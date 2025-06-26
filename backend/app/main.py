from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import json
import asyncio
from typing import List, Dict
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
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

# Log file path - pointing to the mounted nginx logs directory
LOG_FILE_PATH = "./nginx-logs/logs/access.log"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "autosre-backend", "timestamp": datetime.utcnow().isoformat()}

# Log parsing functions
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

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        print("WebSocket connection established, sending initial data...")
        await send_initial_data(websocket)
        while True:
            await asyncio.sleep(5)
            try:
                await check_for_updates(websocket)
            except Exception as e:
                print(f"WebSocket send error (likely client disconnected): {e}")
                break  # Exit the loop if sending fails
    except WebSocketDisconnect:
        print("WebSocket disconnected (client closed connection)")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
        print("WebSocket cleanup complete.")

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
    except Exception as e:
        print(f"Error checking for updates: {e}")
        # Don't try to send error message if WebSocket is closed
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Error updating data: {str(e)}"
            }))
        except:
            # WebSocket is closed, just log the error
            print(f"WebSocket closed, cannot send error message")

# Regular HTTP endpoints (for compatibility)
@app.get("/get_logs/")
async def get_logs():
    # Read logs from the mounted nginx logs directory
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        return {"logs": logs}
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

@app.get("/get_error_logs/")
async def get_error_logs():
    # Read logs and parse for errors
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        
        error_logs = parse_logs(logs)
        return {"error_logs": error_logs}
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

@app.get("/summarize_logs/")
async def summarize_logs_endpoint():
    # Read logs
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        
        # Use simple log analysis instead of Ollama
        log_summary = analyze_logs_simple(logs)
        return {"summary": log_summary}
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}

@app.get("/analyze_logs/")
async def analyze_logs_endpoint():
    # Read logs
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            logs = file.read()
        
        return analyze_logs(logs)
    else:
        return {"error": "Log file not found", "path": LOG_FILE_PATH}
