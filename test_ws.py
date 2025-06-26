#!/usr/bin/env python3
"""
Quick WebSocket test for AutoSRE backend
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    try:
        print(f"🔌 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Waiting for data...")
            
            # Wait for initial data
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"📨 Received message type: {data.get('type')}")
            if data.get('type') == 'initial_data':
                print("🎉 WebSocket is working perfectly!")
                analysis = data.get('analysis', {})
                print(f"📊 Total requests: {analysis.get('total_requests', 0)}")
                print(f"❌ Error count: {analysis.get('error_count', 0)}")
                print(f"📈 Success rate: {analysis.get('success_rate', 0):.1f}%")
            else:
                print(f"⚠️ Unexpected message type: {data}")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 