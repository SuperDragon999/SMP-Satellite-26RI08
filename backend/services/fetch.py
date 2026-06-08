import asyncio
import websockets
import serial_asyncio
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

class SerialJSONProtocol(asyncio.Protocol):
    def __init__(self, queue):
        self.buffer = ""
        self.queue = queue

    def connection_made(self, transport):
        self.transport = transport
        print("Serial connection established!")

    def data_received(self, data):
        text = data.decode(errors="ignore")
        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue
            try:
                obj = json.loads(line)
                self.handle_json(obj)
            except json.JSONDecodeError:
                print("Bad JSON:", line)
    def handle_json(self, obj):
        if not get_record():
            return
        else:
            self.queue.put_nowait(obj)

    def connection_lost(self, exc):
        print("Serial connection lost")
        asyncio.get_event_loop().stop()

async def fetchserial():
    port = "COM7"
    baud = 912600
    queue = asyncio.Queue()

    worker_task = asyncio.create_task(db_worker(queue))

    loop = asyncio.get_running_loop()

    def protocol_factory():
        return SerialJSONProtocol(queue)

    await serial_asyncio.create_serial_connection(
        loop,
        protocol_factory,
        port,
        baudrate=baud
    )

    await worker_task

#Websocket async monitor
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
                        if not await asyncio.to_thread(get_record):
                            break
                        else:
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