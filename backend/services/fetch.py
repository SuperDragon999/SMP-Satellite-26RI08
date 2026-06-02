import asyncio
import websockets
import json
from backend.storage.db_commands import *

async def db_worker(queue):
    while True:
        job = await queue.get()
        try:
            data_type = job["Type"]
            if data_type == "Packet":
                await asyncio.to_thread(addEntry, job["ID"], job["sensor"], job["latency"], "PACKET")
            elif data_type == "ERR":
                print(f"PACKET DROP at packet {job['ID']}")
                await asyncio.to_thread(addEntry, job["ID"], 0, 0, "DROP")
        except Exception as e:
            print(f"[-] Database write error: {e}")
        finally:
            queue.task_done()

async def stream_telemetry(uri):
    print(f"[+] Connecting to ground station at {uri}...")
    logged = False
    while True:
        if not await asyncio.to_thread(get_record):
            if not logged:
                print("[IDLE] Recording is off, no query is being made.")
                logged = True
            await asyncio.sleep(0.1)
            continue

        print(f"[+] Recording activated! Initializing connection to {uri}...")
        queue = asyncio.Queue()
        worker_task = asyncio.create_task(db_worker(queue))
        
        while await asyncio.to_thread(get_record):
            try:
                async with websockets.connect(uri) as websocket:
                    print("[+] Connected to ESP32!")
                    async for message in websocket:
                        print(f"[+] Received: {message}")
                        data = json.loads(message)
                        await queue.put(data)
            except (websockets.exceptions.ConnectionClosed, OSError) as e:
                print(f"[-] Connection lost ({e}). Reconnecting in 3 seconds...")
                if not await asyncio.to_thread(get_record):
                    break
                await asyncio.sleep(3)
            finally:
                logged = False
        
        print(f"[-] Recording stopped by user.")
        await queue.join()
        worker_task.cancel()