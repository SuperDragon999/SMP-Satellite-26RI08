#Request from ESP32
import asyncio
import websockets
from backend.storage.db_commands import *

async def ingest_data():
    uri = "ws://192.168.50.44:81"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("Successfully connected to satellite!")
                while True:
                    message = await websocket.recv()
                    addTest(message)
                    await asyncio.sleep(5)
        except Exception as e:
            print(f"Connection lost. Retrying in 5s... Error: {e}")
            await asyncio.sleep(5)