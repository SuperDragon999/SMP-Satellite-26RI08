import subprocess
import os
from pathlib import Path
from backend.services.fetch import *
from backend.storage.setup import *

name = input("Enter name of db file: ")
database = sqlite3.connect(f"backend/storage/data/{name}.db")

setup2(database)
with open("config.txt", "w") as f:
    f.write(name)

project_root = str(Path(__file__).resolve().parent)
env = os.environ.copy()
env["PYTHONPATH"]=project_root + os.pathsep + env.get("PYTHONPATH","")

subprocess.Popen(["streamlit","run","app/app.py"],
env=env
)

config=SerialConfig("COM10", 921600, asyncio.Queue())
asyncio.run(fetchSerial(config))