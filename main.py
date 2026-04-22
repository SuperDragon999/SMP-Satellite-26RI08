#Main file to run project from
from backend.services.decode import fdecode_satellite_packet, rdecode_satellite_packet
import subprocess

# response = fd("")
# byte_form = response[0]
# raw_form = response[1]
# decoded = rdecode_satellite_packet(byte_form)
# fdecode_satellite_packet("backend/storage/raw/packet.bin")
subprocess.run(["streamlit", "run", "app/app.py"])