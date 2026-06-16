import subprocess
import os
from pathlib import Path
from backend.services.fetch import *

project_root = str(Path(__file__).resolve().parent)
env = os.environ.copy()
env["PYTHONPATH"]=project_root + os.pathsep + env.get("PYTHONPATH","")

subprocess.Popen(["streamlit","run","app/app.py"],
env=env
)

config=SerialConfig("COM10", 921600, asyncio.Queue())
asyncio.run(fetchSerial(config))