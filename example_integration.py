#!/usr/bin/env python3
"""
Example Integration with AutoSRE
================================

This example shows how to integrate an unfinished application with AutoSRE
for monitoring and observability.

Run this example to see how your application can send metrics and logs
to AutoSRE for monitoring.
"""

from autosre_client import AutoSREClient
import time
import random
import threading
from datetime import datetime

class ExampleApplication:
    """Example unfinished application that integrates with AutoSRE."""
    
    def __init__(self, app_name: str = "my-unfinished-app"):
        self.app_name = app_name
        self.autosre = AutoSREClient("http://localhost:8000", app_name)
        self.running = False
        
        # Simulate application state
        self.user_count = 0
        self.request_count = 0
        self.error_count = 0
        
    def start(self):
        """Start the example application."""
        print(f"🚀 Starting {self.app_name}...")
        self.running = True
        
        # Send startup log
        self.autosre.send_logs([
            f"Application {self.app_name} started successfully",
            f"Initializing database connections...",
            f"Loading configuration files...",
            f"Starting background workers..."
        ])
        
        # Start background threads
        threading.Thread(target=self.simulate_user_activity, daemon=True).start()
        threading.Thread(target=self.simulate_api_requests, daemon=True).start()
        threading.Thread(target=self.simulate_errors, daemon=True).start()
        threading.Thread(target=self.send_periodic_metrics, daemon=True).start()
        
        print(f"✅ {self.app_name} is now running and sending data to AutoSRE")
        print("📊 Check the AutoSRE dashboard at http://localhost:3000")
        print("📈 Check Grafana at http://localhost:3001")
        print("🔌 Press Ctrl+C to stop")
        
    def stop(self):
        """Stop the example application."""
        print(f"\n🛑 Stopping {self.app_name}...")
        self.running = False
        
        # Send shutdown log
        self.autosre.send_logs([
            f"Application {self.app_name} shutting down gracefully",
            f"Final stats: {self.request_count} requests, {self.error_count} errors",
            f"Application stopped"
        ])
        
    def simulate_user_activity(self):
        """Simulate user registration and activity."""
        while self.running:
            try:
                # Simulate user registration
                if random.random() < 0.3:  # 30% chance
                    self.user_count += 1
                    response_time = random.randint(50, 200)
                    
                    # Send user registration metric
                    self.autosre.send_request_metric(
                        endpoint="/api/users/register",
                        method="POST",
                        response_time=response_time,
                        status_code=201,
                        user_id=f"user_{self.user_count}",
                        user_count=self.user_count
                    )
                    
                    # Send log
                    self.autosre.send_logs([
                        f"New user registered: user_{self.user_count}"
                    ])
                
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                self.autosre.send_error_log(
                    f"Error in user activity simulation: {e}",
                    error_type="ERROR"
                )
    
    def simulate_api_requests(self):
        """Simulate API requests to various endpoints."""
        endpoints = [
            ("/api/users", "GET"),
            ("/api/users/profile", "GET"),
            ("/api/posts", "GET"),
            ("/api/posts", "POST"),
            ("/api/comments", "GET"),
            ("/api/comments", "POST"),
            ("/api/search", "GET"),
            ("/api/notifications", "GET")
        ]
        
        while self.running:
            try:
                endpoint, method = random.choice(endpoints)
                self.request_count += 1
                
                # Simulate response time and status
                response_time = random.randint(20, 500)
                status_code = random.choices(
                    [200, 201, 400, 401, 404, 500],
                    weights=[70, 10, 5, 5, 5, 5]
                )[0]
                
                # Send request metric
                self.autosre.send_request_metric(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=status_code,
                    request_count=self.request_count
                )
                
                # Send log for errors
                if status_code >= 400:
                    self.autosre.send_logs([
                        f"API request failed: {method} {endpoint} - {status_code}"
                    ])
                
                time.sleep(random.uniform(0.5, 2))
                
            except Exception as e:
                self.autosre.send_error_log(
                    f"Error in API request simulation: {e}",
                    error_type="ERROR"
                )
    
    def simulate_errors(self):
        """Simulate various application errors."""
        error_types = [
            "Database connection timeout",
            "Redis connection failed",
            "External API timeout",
            "Memory allocation failed",
            "File not found",
            "Permission denied",
            "Invalid JSON format",
            "Rate limit exceeded"
        ]
        
        while self.running:
            try:
                # Simulate occasional errors
                if random.random() < 0.1:  # 10% chance of error
                    error_message = random.choice(error_types)
                    self.error_count += 1
                    
                    # Send error log
                    self.autosre.send_error_log(
                        error_message=error_message,
                        error_type="ERROR",
                        error_count=self.error_count,
                        timestamp=datetime.utcnow().isoformat()
                    )
                
                time.sleep(random.uniform(5, 15))
                
            except Exception as e:
                print(f"Error in error simulation: {e}")
    
    def send_periodic_metrics(self):
        """Send periodic application metrics."""
        while self.running:
            try:
                # Send comprehensive metrics every 30 seconds
                metrics = {
                    "total_users": self.user_count,
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "error_rate": (self.error_count / max(self.request_count, 1)) * 100,
                    "active_connections": random.randint(10, 100),
                    "memory_usage": random.uniform(30, 80),
                    "cpu_usage": random.uniform(20, 60),
                    "disk_usage": random.uniform(40, 70)
                }
                
                self.autosre.send_metrics(metrics)
                
                # Send status log
                self.autosre.send_logs([
                    f"Periodic metrics sent: {self.request_count} requests, {self.error_count} errors"
                ])
                
                time.sleep(30)
                
            except Exception as e:
                self.autosre.send_error_log(
                    f"Error sending periodic metrics: {e}",
                    error_type="ERROR"
                )


def main():
    """Main function to run the example application."""
    print("=" * 60)
    print("🔗 AutoSRE Integration Example")
    print("=" * 60)
    print()
    print("This example shows how to integrate your application with AutoSRE.")
    print("Make sure AutoSRE is running (docker-compose up -d) before starting.")
    print()
    
    # Create and start the example application
    app = ExampleApplication("my-unfinished-app")
    
    try:
        app.start()
        
        # Keep the main thread alive
        while app.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Received interrupt signal")
        app.stop()
        print("✅ Example application stopped")
        print("=" * 60)
    
    except Exception as e:
        print(f"❌ Error running example: {e}")
        app.stop()


if __name__ == "__main__":
    main() 