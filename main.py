import subprocess
import os
import sys
from pathlib import Path
from backend.services.fetch import *

project_root = str(Path(__file__).resolve().parent)
env = os.environ.copy()
env["PYTHONPATH"]=project_root + os.pathsep + env.get("PYTHONPATH","")

subprocess.Popen(["streamlit","run","app/app.py"],
env=env
)

#Pyserial Code
config=SerialConfig("COM10", 921600, asyncio.Queue())
asyncio.run(fetchSerial(config))

# Websocket code
# uri = "ws://192.168.4.1/telemetry"
# asyncio.run(stream_telemetry(uri))