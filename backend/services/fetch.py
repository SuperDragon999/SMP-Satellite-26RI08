import asyncio
import websockets
import json
from backend.storage.db_commands import *

async def stream_telemetry():
    uri = "ws://192.168.4.1/telemetry"
    print(f"[+] Connecting to ground station at {uri}...")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("[+] Connected to ESP32!")
                async for message in websocket:
                    print(f"[+] Received: {message}")
                    data = json.loads(message)
                    addEntry(data["ID"], data["sensor"], data["latency"])
                    await asyncio.sleep(3)
        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            print(f"[-] Connection lost ({e}). Reconnecting in 2 seconds...")
            await asyncio.sleep(2)

# if __name__ == "__main__":
#     asyncio.run(stream_telemetry())