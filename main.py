import subprocess, os, sqlite3, json
from pathlib import Path

with open("config.json", "w") as f:
    pass # create config.json if it doesn't exist

name = input("Enter name of db file: ")
phase_type = input("Which phase of experimentation is this file for? ")
serial_port = input("Enter the Serial Port for monitoring: ")
baud_rate = input("Enter the baud rate of the ESP-32: ")

config = {
        "db_name": name,
        "phase": phase_type,
        "serial_port": serial_port,
        "baud_rate": baud_rate
}

with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

database = sqlite3.connect(f"backend/storage/data/{name}.db")

# import the rest of the modules
from backend.services.fetch import *
from backend.storage.setup import *

setup(database, phase_type)

project_root = str(Path(__file__).resolve().parent)
env = os.environ.copy()
env["PYTHONPATH"]=project_root + os.pathsep + env.get("PYTHONPATH","")

subprocess.Popen(["streamlit","run","app/app.py"],
env=env
)

config=SerialConfig(serial_port, baud_rate, asyncio.Queue())
asyncio.run(fetchSerial(config))