#!/usr/bin/env python3
"""
Comprehensive WebSocket test suite for AutoSRE backend
"""

import asyncio
import websockets
import json
import time
import sys
from typing import Dict, Any

class WebSocketTester:
    def __init__(self, uri: str = "ws://localhost:8000/ws"):
        self.uri = uri
        self.test_results = []

    async def test_connection(self) -> bool:
        """Test basic WebSocket connection"""
        try:
            async with websockets.connect(self.uri) as websocket:
                print(f"✅ Connected to {self.uri}")
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def test_initial_data(self) -> Dict[str, Any]:
        """Test initial data reception"""
        try:
            async with websockets.connect(self.uri) as websocket:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get('type') == 'initial_data':
                    print("✅ Initial data received successfully")
                    analysis = data.get('analysis', {})
                    print(f"📊 Total requests: {analysis.get('total_requests', 0)}")
                    print(f"❌ Error count: {analysis.get('error_count', 0)}")
                    print(f"📈 Success rate: {analysis.get('success_rate', 0):.1f}%")
                    return data
                else:
                    print(f"❌ Unexpected message type: {data.get('type')}")
                    return {}
        except Exception as e:
            print(f"❌ Initial data test failed: {e}")
            return {}

    async def test_reconnection(self) -> bool:
        """Test reconnection capability"""
        try:
            # First connection
            async with websockets.connect(self.uri) as websocket1:
                await websocket1.recv()
            
            # Second connection
            async with websockets.connect(self.uri) as websocket2:
                await websocket2.recv()
            
            print("✅ Reconnection test passed")
            return True
        except Exception as e:
            print(f"❌ Reconnection test failed: {e}")
            return False

    async def test_update_messages(self) -> bool:
        """Test that update messages are received"""
        try:
            async with websockets.connect(self.uri) as websocket:
                # Get initial data
                initial_response = await websocket.recv()
                initial_data = json.loads(initial_response)
                
                if initial_data.get('type') != 'initial_data':
                    print("❌ Expected initial_data message")
                    return False
                
                # Wait for update message (should come within 10 seconds)
                try:
                    update_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    update_data = json.loads(update_response)
                    
                    if update_data.get('type') == 'update':
                        print("✅ Update message received successfully")
                        return True
                    else:
                        print(f"❌ Unexpected update message type: {update_data.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    print("❌ No update message received within 10 seconds")
                    return False
                    
        except Exception as e:
            print(f"❌ Update message test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all WebSocket tests"""
        print("🧪 Starting WebSocket test suite...")
        print(f"🎯 Target: {self.uri}")
        print("="*50)
        
        tests = [
            ("Connection", self.test_connection),
            ("Initial Data", self.test_initial_data),
            ("Reconnection", self.test_reconnection),
            ("Update Messages", self.test_update_messages),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name} test...")
            result = await test_func()
            self.test_results.append((test_name, result))
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print("⚠️ Some tests failed!")
            sys.exit(1)

async def main():
    tester = WebSocketTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 