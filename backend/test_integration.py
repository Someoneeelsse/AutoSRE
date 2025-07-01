import pytest
import asyncio
import json
import time
import requests
import websockets
from datetime import datetime
from fastapi.testclient import TestClient
import subprocess
import os
import signal
import psutil

from main import app

client = TestClient(app)

class TestFullSystemIntegration:
    """Integration tests for the complete AutoSRE system"""
    
    def test_backend_startup(self):
        """Test that the backend starts and responds to health checks"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_all_api_endpoints_accessible(self):
        """Test that all API endpoints are accessible"""
        endpoints = [
            "/health",
            "/test", 
            "/api/metrics",
            "/metrics",
            "/metrics/api/v1/query?query=up",
            "/get_logs/",
            "/get_error_logs/",
            "/summarize_logs/",
            "/analyze_logs/"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    @pytest.mark.asyncio
    async def test_websocket_full_cycle(self):
        """Test complete WebSocket connection lifecycle"""
        with client.websocket_connect("/ws") as websocket:
            # Test initial data reception
            initial_data = websocket.receive_text()
            initial_message = json.loads(initial_data)
            
            assert initial_message["type"] == "initial_data"
            assert "analysis" in initial_message
            assert "logs" in initial_message
            assert "alerts" in initial_message
            
            # Test sending ping
            ping_message = {"type": "ping"}
            websocket.send_text(json.dumps(ping_message))
            
            # Connection should remain stable
            assert websocket.ready
            
            # Test receiving update (if available)
            try:
                update_data = websocket.receive_text()
                update_message = json.loads(update_data)
                assert update_message["type"] in ["update", "initial_data"]
            except:
                # No update received, which is fine
                pass
    
    def test_system_metrics_integration(self):
        """Test that system metrics are properly collected and returned"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "uptime" in data
        
        # Check data types and ranges
        assert isinstance(data["cpu"]["usage_percent"], (int, float))
        assert 0 <= data["cpu"]["usage_percent"] <= 100
        assert isinstance(data["cpu"]["core_count"], int)
        assert data["cpu"]["core_count"] > 0
        
        assert isinstance(data["memory"]["usage_percent"], (int, float))
        assert 0 <= data["memory"]["usage_percent"] <= 100
        
        assert isinstance(data["disk"]["usage_percent"], (int, float))
        assert 0 <= data["disk"]["usage_percent"] <= 100
    
    def test_prometheus_metrics_integration(self):
        """Test that Prometheus metrics are properly exposed"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        metrics_text = response.text
        
        # Check for key metrics
        assert "http_requests_total" in metrics_text
        assert "websocket_active_connections" in metrics_text
        assert "system_cpu_usage_percent" in metrics_text
        assert "system_memory_usage_percent" in metrics_text
        assert "system_disk_usage_percent" in metrics_text
    
    def test_log_analysis_integration(self):
        """Test that log analysis endpoints work with real data"""
        # Test analyze logs endpoint
        response = client.get("/analyze_logs/")
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        
        analysis = data["analysis"]
        assert "total_requests" in analysis
        assert "success_rate" in analysis
        assert "error_count" in analysis
        assert "status_code_distribution" in analysis
        
        # Test summarize logs endpoint
        response = client.get("/summarize_logs/")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert isinstance(data["summary"], str)
    
    def test_alert_system_integration(self):
        """Test that the alert system works with real metrics"""
        # Get current metrics
        response = client.get("/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        
        # Get current analysis
        response = client.get("/analyze_logs/")
        assert response.status_code == 200
        analysis_data = response.json()
        analysis = analysis_data["analysis"]
        
        # Check that alerts are properly structured
        # (Alerts are generated in the WebSocket updates)
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            
            if "alerts" in message:
                alerts = message["alerts"]
                for alert in alerts:
                    assert "id" in alert
                    assert "type" in alert
                    assert "title" in alert
                    assert "message" in alert
                    assert "timestamp" in alert

class TestPerformanceIntegration:
    """Performance and load testing"""
    
    def test_concurrent_websocket_connections(self):
        """Test multiple concurrent WebSocket connections"""
        connections = []
        
        try:
            # Create multiple connections
            for i in range(5):
                websocket = client.websocket_connect("/ws")
                connections.append(websocket)
                
                # Verify each connection receives initial data
                with websocket as ws:
                    data = ws.receive_text()
                    message = json.loads(data)
                    assert message["type"] == "initial_data"
        
        finally:
            # Clean up connections
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass
    
    def test_api_response_times(self):
        """Test that API endpoints respond within acceptable time"""
        endpoints = [
            "/health",
            "/api/metrics", 
            "/metrics",
            "/get_logs/",
            "/analyze_logs/"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0, f"Endpoint {endpoint} took {response_time:.2f}s"
    
    def test_websocket_message_throughput(self):
        """Test WebSocket message handling under load"""
        with client.websocket_connect("/ws") as websocket:
            # Send multiple ping messages rapidly
            for i in range(10):
                ping_message = {"type": "ping"}
                websocket.send_text(json.dumps(ping_message))
                time.sleep(0.1)
            
            # Connection should remain stable
            assert websocket.ready

class TestErrorHandlingIntegration:
    """Test error handling and edge cases"""
    
    def test_invalid_websocket_messages(self):
        """Test handling of invalid WebSocket messages"""
        with client.websocket_connect("/ws") as websocket:
            # Send invalid JSON
            websocket.send_text("invalid json")
            
            # Send malformed message
            websocket.send_text(json.dumps({"invalid": "message"}))
            
            # Connection should remain stable
            assert websocket.ready
    
    def test_missing_log_files(self):
        """Test handling when log files don't exist"""
        # These endpoints should handle missing files gracefully
        response = client.get("/get_logs/")
        assert response.status_code == 200
        
        response = client.get("/get_error_logs/")
        assert response.status_code == 200
    
    def test_prometheus_query_errors(self):
        """Test Prometheus query error handling"""
        # Test with invalid query
        response = client.get("/metrics/api/v1/query?query=invalid_metric")
        assert response.status_code == 200
        
        # Test with missing parameters
        response = client.get("/metrics/api/v1/query")
        assert response.status_code == 200

class TestDataConsistencyIntegration:
    """Test data consistency across different endpoints"""
    
    def test_metrics_consistency(self):
        """Test that metrics are consistent across endpoints"""
        # Get metrics from API endpoint
        api_response = client.get("/api/metrics")
        api_metrics = api_response.json()
        
        # Get metrics from Prometheus endpoint
        prom_response = client.get("/metrics")
        prom_text = prom_response.text
        
        # Check that CPU usage appears in both
        cpu_usage = api_metrics["cpu"]["usage_percent"]
        assert f"system_cpu_usage_percent {cpu_usage}" in prom_text
    
    def test_log_analysis_consistency(self):
        """Test that log analysis is consistent"""
        # Get analysis from dedicated endpoint
        analysis_response = client.get("/analyze_logs/")
        analysis_data = analysis_response.json()["analysis"]
        
        # Get analysis from WebSocket
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            ws_analysis = message["analysis"]
            
            # Key fields should be present in both
            assert "total_requests" in analysis_data
            assert "total_requests" in ws_analysis
            assert "success_rate" in analysis_data
            assert "success_rate" in ws_analysis

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 