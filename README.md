<h1>26NUSDEEP12 Project - An End-to-End TT&C and Payload Data Processing Framework for High-Altitude Balloon Platforms and Satellites</h1>
<br>
<h2>Introduction (Research Question)</h2>
During satellite missions, continuous telemetry monitoring is essential for ensuring system health and mission success. Communication delays or data loss can affect mission operations. This project simulates a simplified telemetry communication system between a satellite node and a ground station using ESP32 devices and ESP-NOW protocol to study reliable wireless data transmission and visualization.
<br>
<h2>Notes: </h2>
<ul>
  <li>There is a secrets.ini file in the /satellite folder which needs to be created in order to compile this project. Check below for the exact format.</li>
  <li>Before running, start a Python virtual environment and install all required PIP modules.</li>
  <li>A total of 2 ESP-32 modules are required, and this project is run in VS Code with the PlatformIO extension.</li>
</ul>

Format of secrets.ini file:
```
[secrets]
build_flags =
    -D WIFI_SSID=\"XXXX\"
    -D WIFI_PASS=\"XXXXX\"
```
