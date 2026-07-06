import subprocess, os, sqlite3, json
from pathlib import Path
from backend.storage.setup import *

with open("config.json", "w") as f:
    pass # create config.json if it doesn't exist / wipe out config.json for each fresh run

name = input("Enter name of db file: ")
serial_port = input("Enter the Serial Port for monitoring: ")

config = {
        "db_name": name,
        "serial_port": serial_port
}

database = sqlite3.connect(f"backend/storage/data/{name}.db")
cursor = database.cursor()

phase_type = None
mode = None

try:
    # Look into sqlite_master to see if the 'ctrl' structural table exists yet
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ctrl';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Check if the columns 'phase' and 'mode' actually exist in the table schema
        cursor.execute("PRAGMA table_info(ctrl);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "phase" in columns and "mode" in columns:
            # Attempt to pull the most recent parameter state from the table rows
            cursor.execute("SELECT phase, mode FROM ctrl ORDER BY rowid DESC LIMIT 1;")
            result = cursor.fetchone()
            if result:
                phase_type, mode = result
                print(f"[INIT] Active database: Phase {phase_type} ({"SAT" if mode == 1 else "GND"})")
except sqlite3.Error as e:
    print(f"[WARN] Database lookup diagnostic failed: {e}")

# Fallback Prompts
if phase_type is None:
    phase_type = input("Which phase of experimentation is this file for? ")

if mode is None:
    mode = input("Enter 1 if this db for the 'satellite' and 0 if it is for the 'ground station': ")

# Execute Auto-Setup Framework
# This guarantees tables are initialized/updated before ingestion starts
setup(database, int(mode), int(phase_type))
database.close()

with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# import the rest of the modules
from backend.services.fetch import *

project_root = str(Path(__file__).resolve().parent)
env = os.environ.copy()
env["PYTHONPATH"]=project_root + os.pathsep + env.get("PYTHONPATH","")

subprocess.Popen(["streamlit","run","app/app.py"],
env=env
)

config=SerialConfig(serial_port, 921600, asyncio.Queue())
asyncio.run(fetchSerial(config))