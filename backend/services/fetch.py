import asyncio
import serial_asyncio
import json
from backend.storage.db_commands import *

async def gnd_worker(queue):
    while True:
        job = await queue.get()
        try:
            data_type = job["type"]
            if data_type == "PACKET":
                await asyncio.to_thread(addEntry, job["ID"], job["type"], job["data1"], job["data2"], job["snr"])
            elif data_type == "DATA_ERR":
                print("CORRUPT PACKET \n")
                await asyncio.to_thread(addEntry, job["ID"], job["type"], job["data1"], job["data2"], job["snr"])
            elif data_type == "LINK_ERR":
                print("DROPPED PACKET \n")
                await asyncio.to_thread(addEntry, job["ID"], job["type"], job["data1"], job["data2"], job["snr"])
        except Exception as e:
            print(f"[-] Database write error: {e}")
        finally:
            queue.task_done()

async def sat_worker(queue):
    while True:
        job = await queue.get()
        try:
            await asyncio.to_thread(addToA, job["ID"], job["time"])
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

async def fetchserial(port, baud):
    queue = asyncio.Queue()

    worker_task = asyncio.create_task(gnd_worker(queue))

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

class SerialConfig:
    def __init__(self, port, baudrate, queue):
        self.port = port
        self.baudrate = baudrate
        self.queue = queue
    def handle_json(self,obj):
        if not get_record():
            return
        else:
            self.queue.put_nowait(obj)

async def fetchSerial(config: SerialConfig):
    logged = False
    queue = config.queue
    worker_task = None
    
    try:
        while True:
            if not await asyncio.to_thread(get_record):
                if not logged:
                    print("[IDLE] Recording is off, no query is being made.")
                    logged = True
                await asyncio.sleep(0.1)
                continue
            
            logged = False
            
            # Start the worker loop
            if worker_task is None or worker_task.done():
                if get_mode() == 0:
                    worker_task = asyncio.create_task(gnd_worker(queue))
                elif get_mode() == 1:
                    worker_task = asyncio.create_task(sat_worker(queue))
                print(f"[+] Initialized {"GND" if get_mode() == 0 else "SAT"} worker task.")
            
            print(f"[+] Connecting to serial port at {config.port}")
            try:
                reader, writer = await serial_asyncio.open_serial_connection(
                    url=config.port,
                    baudrate=config.baudrate
                )
                print("[+] Serial connection established!")
                
                while True:
                    raw = await reader.readline()
                    line = raw.decode("utf-8").strip()
                    if not line:
                        continue
                    print(f"[SERIAL] {line}")
        
                    # Verify record status
                    if not await asyncio.to_thread(get_record):
                        break
                    try:
                        packet = json.loads(line)
                        await queue.put(packet)
                    except json.JSONDecodeError:
                        print(f"[-] Invalid JSON packet: {line}")
                        
            except Exception as e:
                print(f"[-] Serial hardware/connection error: {e}")
                print("[*] Reconnecting in 3 seconds...")
                if not await asyncio.to_thread(get_record):
                    break
                await asyncio.sleep(3)
            finally:
                # Ensure the network/serial sockets are closed properly on break/exit
                try:
                    writer.close()
                    await writer.wait_closed()
                except NameError:
                    pass
                
            # If we exited the inner read loop because recording stopped
            if not await asyncio.to_thread(get_record):
                print("[-] Recording stopped by user.")
                break

    finally:
        # Global cleanup when fetchSerial completely exits
        if worker_task and not worker_task.done():
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                print("[*] Ground worker successfully terminated.")