#!/usr/bin/env python3
"""
Simple traffic generator for AutoSRE nginx server
"""

import requests
import time
import random
from datetime import datetime

def generate_traffic():
    """Generate realistic traffic to nginx endpoints"""
    base_url = "http://localhost:8080"
    endpoints = ["/", "/health", "/test", "/error", "/notfound"]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
    ]
    
    print(f"🚀 Starting traffic generator at {datetime.now()}")
    print(f"📡 Sending requests to {base_url}")
    
    try:
        while True:
            endpoint = random.choice(endpoints)
            user_agent = random.choice(user_agents)
            
            headers = {"User-Agent": user_agent}
            
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                print(f"✅ {response.status_code} - {endpoint}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error hitting {endpoint}: {e}")
            
            # Wait 10 seconds between requests
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Traffic generator stopped")

if __name__ == "__main__":
    generate_traffic() 