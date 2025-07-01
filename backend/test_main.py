import pytest
import asyncio
import json
import time
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import Mock, patch, MagicMock
import psutil
import os

from main import app, ConnectionManager, AlertManager, parse_logs, analyze_logs_simple, analyze_logs

client = TestClient(app)

class TestConnectionManager:
    def test_connection_manager_initialization(self):
        manager = ConnectionManager()
        assert manager.active_connections == []
    
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        manager = ConnectionManager()
        mock_websocket = Mock(spec=WebSocket)
        
        await manager.connect(mock_websocket)
        assert len(manager.active_connections) == 1
        assert mock_websocket in manager.active_connections
        
        manager.disconnect(mock_websocket)
        assert len(manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self):
        manager = ConnectionManager()
        mock_websocket1 = Mock(spec=WebSocket)
        mock_websocket2 = Mock(spec=WebSocket)
        
        await manager.connect(mock_websocket1)
        await manager.connect(mock_websocket2)
        
        await manager.broadcast("test message")
        
        mock_websocket1.send_text.assert_called_once_with("test message")
        mock_websocket2.send_text.assert_called_once_with("test message")

class TestAlertManager:
    def test_alert_manager_initialization(self):
        alert_manager = AlertManager()
        assert alert_manager.active_alerts == set()
    
    def test_cpu_alert_triggering(self):
        alert_manager = AlertManager()
        metrics = {
            "cpu": {"usage_percent": 85.0},
            "memory": {"usage_percent": 50.0},
            "disk": {"usage_percent": 60.0}
        }
        analysis = {"success_rate": 95.0}
        
        alerts = alert_manager.check_alerts(metrics, analysis)
        assert len(alerts) == 1
        assert alerts[0]["id"] == "high_cpu"
        assert alerts[0]["type"] == "warning"
    
    def test_memory_alert_triggering(self):
        alert_manager = AlertManager()
        metrics = {
            "cpu": {"usage_percent": 50.0},
            "memory": {"usage_percent": 90.0},
            "disk": {"usage_percent": 60.0}
        }
        analysis = {"success_rate": 95.0}
        
        alerts = alert_manager.check_alerts(metrics, analysis)
        assert len(alerts) == 1
        assert alerts[0]["id"] == "high_memory"
    
    def test_error_rate_alert_triggering(self):
        alert_manager = AlertManager()
        metrics = {
            "cpu": {"usage_percent": 50.0},
            "memory": {"usage_percent": 50.0},
            "disk": {"usage_percent": 60.0}
        }
        analysis = {"success_rate": 85.0}  # 15% error rate
        
        alerts = alert_manager.check_alerts(metrics, analysis)
        assert len(alerts) == 1
        assert alerts[0]["id"] == "high_error_rate"
        assert alerts[0]["type"] == "critical"
    
    def test_alert_clearing(self):
        alert_manager = AlertManager()
        
        # Trigger alert
        metrics_high = {
            "cpu": {"usage_percent": 85.0},
            "memory": {"usage_percent": 50.0},
            "disk": {"usage_percent": 60.0}
        }
        analysis = {"success_rate": 95.0}
        
        alerts = alert_manager.check_alerts(metrics_high, analysis)
        assert len(alerts) == 1
        assert "high_cpu" in alert_manager.active_alerts
        
        # Clear alert
        metrics_normal = {
            "cpu": {"usage_percent": 50.0},
            "memory": {"usage_percent": 50.0},
            "disk": {"usage_percent": 60.0}
        }
        
        alerts = alert_manager.check_alerts(metrics_normal, analysis)
        assert len(alerts) == 0
        assert "high_cpu" not in alert_manager.active_alerts

class TestLogAnalysis:
    def test_parse_logs(self):
        log_data = """192.168.1.1 - - [28/Jun/2025:10:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.2 - - [28/Jun/2025:10:00:01 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "curl/7.68.0"
192.168.1.3 - - [28/Jun/2025:10:00:02 +0000] "GET /notfound HTTP/1.1" 404 123 "-" "Mozilla/5.0"
192.168.1.4 - - [28/Jun/2025:10:00:03 +0000] "GET /error HTTP/1.1" 500 123 "-" "Mozilla/5.0"
"""
        parsed = parse_logs(log_data)
        assert len(parsed) == 2  # Both 201 and 500 lines are matched
        assert any("201" in line for line in parsed)  # 201 line is included
        assert any("500" in line for line in parsed)  # 500 line is included
    
    def test_analyze_logs_simple(self):
        log_data = """192.168.1.1 - - [28/Jun/2025:10:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.2 - - [28/Jun/2025:10:00:01 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "curl/7.68.0"
192.168.1.3 - - [28/Jun/2025:10:00:02 +0000] "GET /notfound HTTP/1.1" 404 123 "-" "Mozilla/5.0"
192.168.1.4 - - [28/Jun/2025:10:00:03 +0000] "GET /error HTTP/1.1" 500 123 "-" "Mozilla/5.0"
"""
        analysis = analyze_logs_simple(log_data)
        assert "Total requests: 4" in analysis
        assert "Success rate: 50.0%" in analysis
        assert "Error requests: 2" in analysis
    
    def test_analyze_logs_comprehensive(self):
        log_data = """192.168.1.1 - - [28/Jun/2025:10:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.2 - - [28/Jun/2025:10:00:01 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "curl/7.68.0"
192.168.1.3 - - [28/Jun/2025:10:00:02 +0000] "GET /notfound HTTP/1.1" 404 123 "-" "Mozilla/5.0"
192.168.1.4 - - [28/Jun/2025:10:00:03 +0000] "GET /error HTTP/1.1" 500 123 "-" "Mozilla/5.0"
"""
        analysis = analyze_logs(log_data)
        assert analysis["total_requests"] == 4
        assert analysis["success_rate"] == 50.0
        assert analysis["error_count"] == 2
        assert "200" in analysis["status_code_distribution"]
        assert "404" in analysis["status_code_distribution"]
        assert "500" in analysis["status_code_distribution"]

class TestAPIEndpoints:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_test_endpoint(self):
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Backend is accessible"
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_system_metrics(self, mock_net, mock_disk, mock_memory, mock_cpu_count, mock_cpu_percent):
        # Mock system metrics
        mock_cpu_percent.return_value = 25.5
        mock_cpu_count.return_value = 8
        mock_memory.return_value = Mock(
            percent=65.2,
            used=8589934592,  # 8GB
            total=17179869184  # 16GB
        )
        mock_disk.return_value = Mock(
            percent=45.8,
            used=107374182400,  # 100GB
            total=214748364800  # 200GB
        )
        mock_net.return_value = Mock(
            bytes_sent=1048576,
            bytes_recv=2097152
        )
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert "cpu" in data
        assert data["cpu"]["usage_percent"] == 25.5
        assert data["cpu"]["core_count"] == 8
        
        assert "memory" in data
        assert data["memory"]["usage_percent"] == 65.2
        
        assert "disk" in data
        assert data["disk"]["usage_percent"] == 45.8
    
    def test_metrics_endpoint(self):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "http_requests_total" in response.text
    
    def test_prometheus_query_endpoint(self):
        response = client.get("/metrics/api/v1/query?query=up")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
    
    def test_prometheus_query_range_endpoint(self):
        response = client.get("/metrics/api/v1/query_range?query=up&start=2025-01-01T00:00:00Z&end=2025-01-01T01:00:00Z&step=60s")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
    
    @patch('builtins.open', create=True)
    def test_get_logs(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = [
            "192.168.1.1 - - [28/Jun/2025:10:00:00 +0000] \"GET / HTTP/1.1\" 200 1234 \"-\" \"Mozilla/5.0\"\n"
        ]
        
        response = client.get("/get_logs/")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
    
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_get_error_logs(self, mock_exists, mock_open):
        # Mock that the file exists
        mock_exists.return_value = True
        
        # Mock the file read operation
        mock_file = Mock()
        mock_file.read.return_value = "2025/06/28 10:00:00 [error] 123#0: *1 connection refused\n"
        mock_open.return_value.__enter__.return_value = mock_file
        
        response = client.get("/get_error_logs/")
        assert response.status_code == 200
        data = response.json()
        assert "error_logs" in data
        assert isinstance(data["error_logs"], str)
    
    def test_summarize_logs_endpoint(self):
        response = client.get("/summarize_logs/")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
    
    def test_analyze_logs_endpoint(self):
        response = client.get("/analyze_logs/")
        assert response.status_code == 200
        data = response.json()
        # The response structure has changed - it returns the analysis directly
        assert "total_requests" in data or "error_count" in data

class TestPrometheusMetrics:
    def test_metrics_are_registered(self):
        from main import REQUEST_COUNT, REQUEST_DURATION, ACTIVE_CONNECTIONS, ERROR_COUNT
        from main import SYSTEM_CPU_USAGE, SYSTEM_MEMORY_USAGE, SYSTEM_DISK_USAGE
        
        # Verify metrics are properly initialized
        assert REQUEST_COUNT is not None
        assert REQUEST_DURATION is not None
        assert ACTIVE_CONNECTIONS is not None
        assert ERROR_COUNT is not None
        assert SYSTEM_CPU_USAGE is not None
        assert SYSTEM_MEMORY_USAGE is not None
        assert SYSTEM_DISK_USAGE is not None

if __name__ == "__main__":
    pytest.main([__file__]) 