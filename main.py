#Main file to run project from
import subprocess
import os
import sys
from pathlib import Path

# Get the absolute path to the SMP root
project_root = str(Path(__file__).resolve().parent)

# Get the current environment variables and add SMP to PYTHONPATH
env = os.environ.copy()
env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

# Launch the subprocess with the updated environment
subprocess.Popen(
    ["streamlit", "run", "app/app.py"], 
    env=env
)