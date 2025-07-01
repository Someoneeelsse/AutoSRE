#!/usr/bin/env python3
"""
AutoSRE Client Library
======================

A Python client library for integrating applications with AutoSRE monitoring platform.

Usage:
    from autosre_client import AutoSREClient
    
    # Initialize client
    autosre = AutoSREClient("http://localhost:8000", "my-app")
    
    # Send metrics
    autosre.send_metrics({
        "endpoint": "/api/users",
        "response_time": 150,
        "status_code": 200,
        "user_count": 1000
    })
    
    # Send logs
    autosre.send_logs([
        "User login successful",
        "Database query completed"
    ])
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

class AutoSREClient:
    """Client for integrating applications with AutoSRE monitoring platform."""
    
    def __init__(self, base_url: str = "http://localhost:8000", app_name: str = "unknown"):
        """
        Initialize AutoSRE client.
        
        Args:
            base_url: AutoSRE backend URL
            app_name: Name of your application
        """
        self.base_url = base_url.rstrip('/')
        self.app_name = app_name
        self.session = requests.Session()
        self.logger = logging.getLogger(f"autosre_client.{app_name}")
        
        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.logger.info(f"Successfully connected to AutoSRE at {self.base_url}")
            else:
                self.logger.warning(f"AutoSRE health check failed: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to connect to AutoSRE: {e}")
    
    def send_metrics(self, metrics: Dict, endpoint: str = "/api/metrics/custom") -> Dict:
        """
        Send custom metrics to AutoSRE.
        
        Args:
            metrics: Dictionary containing your application metrics
            endpoint: AutoSRE endpoint to send metrics to
            
        Returns:
            Response from AutoSRE
        """
        try:
            # Add app name and timestamp
            payload = {
                "app_name": self.app_name,
                "timestamp": datetime.utcnow().isoformat(),
                **metrics
            }
            
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Successfully sent metrics: {metrics}")
                return response.json()
            else:
                self.logger.error(f"Failed to send metrics: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error sending metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_logs(self, logs: List[str], endpoint: str = "/api/logs") -> Dict:
        """
        Send log entries to AutoSRE.
        
        Args:
            logs: List of log entries (strings)
            endpoint: AutoSRE endpoint to send logs to
            
        Returns:
            Response from AutoSRE
        """
        try:
            payload = {
                "app_name": self.app_name,
                "logs": logs,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Successfully sent {len(logs)} log entries")
                return response.json()
            else:
                self.logger.error(f"Failed to send logs: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error sending logs: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_request_metric(self, endpoint: str, method: str = "GET", 
                           response_time: int = None, status_code: int = None,
                           user_id: str = None, **kwargs) -> Dict:
        """
        Send HTTP request metrics to AutoSRE.
        
        Args:
            endpoint: API endpoint that was called
            method: HTTP method (GET, POST, etc.)
            response_time: Response time in milliseconds
            status_code: HTTP status code
            user_id: User ID (optional)
            **kwargs: Additional metrics
            
        Returns:
            Response from AutoSRE
        """
        metrics = {
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "status_code": status_code,
            "user_id": user_id,
            **kwargs
        }
        
        return self.send_metrics(metrics)
    
    def send_error_log(self, error_message: str, error_type: str = "ERROR", 
                      stack_trace: str = None, **kwargs) -> Dict:
        """
        Send error log to AutoSRE.
        
        Args:
            error_message: Error message
            error_type: Type of error (ERROR, WARNING, etc.)
            stack_trace: Stack trace (optional)
            **kwargs: Additional error context
            
        Returns:
            Response from AutoSRE
        """
        log_entry = f"[{error_type}] {error_message}"
        if stack_trace:
            log_entry += f"\n{stack_trace}"
        
        if kwargs:
            context = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            log_entry += f" | Context: {context}"
        
        return self.send_logs([log_entry])
    
    def get_application_metrics(self, app_name: str = None) -> Dict:
        """
        Get metrics for your application from AutoSRE.
        
        Args:
            app_name: Application name (defaults to self.app_name)
            
        Returns:
            Application metrics from AutoSRE
        """
        try:
            app = app_name or self.app_name
            response = self.session.get(
                f"{self.base_url}/api/applications/{app}/metrics",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get metrics: {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    def list_applications(self) -> Dict:
        """
        List all applications connected to AutoSRE.
        
        Returns:
            List of applications and their status
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/applications",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to list applications: {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error listing applications: {e}")
            return {"status": "error", "message": str(e)}


# Convenience functions for quick integration
def quick_metrics(base_url: str, app_name: str, metrics: Dict) -> Dict:
    """Quick function to send metrics without creating a client instance."""
    client = AutoSREClient(base_url, app_name)
    return client.send_metrics(metrics)


def quick_logs(base_url: str, app_name: str, logs: List[str]) -> Dict:
    """Quick function to send logs without creating a client instance."""
    client = AutoSREClient(base_url, app_name)
    return client.send_logs(logs)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    client = AutoSREClient("http://localhost:8000", "example-app")
    
    # Send some test metrics
    result = client.send_metrics({
        "endpoint": "/api/test",
        "response_time": 125,
        "status_code": 200,
        "user_count": 500
    })
    print(f"Metrics result: {result}")
    
    # Send some test logs
    result = client.send_logs([
        "Application started successfully",
        "Database connection established",
        "User authentication completed"
    ])
    print(f"Logs result: {result}")
    
    # Send a request metric
    result = client.send_request_metric(
        endpoint="/api/users",
        method="POST",
        response_time=150,
        status_code=201,
        user_id="user123"
    )
    print(f"Request metric result: {result}")
    
    # Send an error log
    result = client.send_error_log(
        error_message="Database connection timeout",
        error_type="ERROR",
        stack_trace="Traceback (most recent call last):\n  File...",
        database="postgresql",
        timeout=30
    )
    print(f"Error log result: {result}") 