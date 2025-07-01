#!/usr/bin/env python3
"""
Advanced traffic generator for AutoSRE nginx server
"""

import requests
import time
import random
import argparse
import signal
import sys
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class TrafficConfig:
    base_url: str
    endpoints: List[str]
    user_agents: List[str]
    interval: float
    duration: int
    concurrent: int

class TrafficGenerator:
    def __init__(self, config: TrafficConfig):
        self.config = config
        self.session = requests.Session()
        self.running = True
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now(),
            'status_codes': {}
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.print_stats()
        sys.exit(0)

    def make_request(self) -> Dict:
        """Make a single request"""
        endpoint = random.choice(self.config.endpoints)
        user_agent = random.choice(self.config.user_agents)
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        try:
            response = self.session.get(
                f"{self.config.base_url}{endpoint}", 
                headers=headers, 
                timeout=5
            )
            self.stats['successful_requests'] += 1
            
            # Track status codes
            status_code = str(response.status_code)
            self.stats['status_codes'][status_code] = self.stats['status_codes'].get(status_code, 0) + 1
            
            return {
                'status_code': response.status_code,
                'endpoint': endpoint,
                'success': True
            }
        except requests.exceptions.RequestException as e:
            self.stats['failed_requests'] += 1
            return {
                'status_code': None,
                'endpoint': endpoint,
                'success': False,
                'error': str(e)
            }

    def print_stats(self):
        """Print current statistics"""
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        rps = self.stats['total_requests'] / duration if duration > 0 else 0
        success_rate = (self.stats['successful_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
        
        print(f"\n📊 Traffic Generator Statistics:")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Total Requests: {self.stats['total_requests']}")
        print(f"   Successful: {self.stats['successful_requests']}")
        print(f"   Failed: {self.stats['failed_requests']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Requests/sec: {rps:.2f}")
        
        if self.stats['status_codes']:
            print(f"   Status Codes: {dict(self.stats['status_codes'])}")

    def generate_traffic(self):
        """Generate traffic according to configuration"""
        print(f"🚀 Starting traffic generator at {datetime.now()}")
        print(f"📡 Target: {self.config.base_url}")
        print(f"⏱️  Interval: {self.config.interval}s")
        print(f"⏰ Duration: {self.config.duration}s")
        print(f"🔄 Concurrent: {self.config.concurrent}")
        print(f"🎯 Endpoints: {', '.join(self.config.endpoints)}")
        print("-" * 50)
        
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.config.duration:
            # Make requests
            for _ in range(self.config.concurrent):
                result = self.make_request()
                self.stats['total_requests'] += 1
                
                if result['success']:
                    print(f"✅ {result['status_code']} - {result['endpoint']}")
                else:
                    print(f"❌ Error - {result['endpoint']}: {result['error']}")
            
            time.sleep(self.config.interval)

def main():
    parser = argparse.ArgumentParser(description='Generate traffic for AutoSRE')
    parser.add_argument('--url', default='http://localhost:8080', help='Target URL')
    parser.add_argument('--interval', type=float, default=1.0, help='Request interval (seconds)')
    parser.add_argument('--duration', type=int, default=300, help='Duration (seconds)')
    parser.add_argument('--concurrent', type=int, default=1, help='Concurrent requests')
    parser.add_argument('--endpoints', nargs='+', 
                       default=["/", "/health", "/test", "/error", "/notfound"],
                       help='Endpoints to hit')
    
    args = parser.parse_args()
    
    config = TrafficConfig(
        base_url=args.url,
        endpoints=args.endpoints,
        user_agents=[
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
        ],
        interval=args.interval,
        duration=args.duration,
        concurrent=args.concurrent
    )
    
    generator = TrafficGenerator(config)
    generator.generate_traffic()

if __name__ == "__main__":
    main() 