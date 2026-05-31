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
                    if get_record():
                        print(f"[+] Received: {message}")
                        data = json.loads(message)
                        if data["Type"] == "Packet":
                            addEntry(data["ID"], data["sensor"], data["latency"], "PACKET")
                        elif data["Type"] == "ERR":
                            print(f"PACKET DROP at packet {data['ID']}")
                            addEntry(data["ID"], 0, 0, "DROP")
                    else:
                        print(f"[IDLE] Recording is off, no query is being made")
        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            print(f"[-] Connection lost ({e}). Reconnecting...")