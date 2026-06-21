<h1>26NUSDEEP12 Project - Evaluating Adaptive LoRa Hyperparameter Selection Algorithms for Doppler-robust Low-cost LEO Communication Links (UNDER DEVELOPMENT)</h1>
<br>
<h2>Research Question</h2>
How effectively can adaptive LoRa spreading factor and bandwidth selection improve performance under severe Doppler-induced frequency offset in low-cost LEO communication links?
<br>
<h2>Notes: </h2>
<ul>
  <li>Before running, start a Python virtual environment and install all required Python libraries</li>
  <li>Create a folder in backend/storage named "data", and a text file named "config.txt" (to save the database naming config) in the root directory.</li>
  <li>To load a new / existing database, simply type its name when running main.py</li>
  <li>A total of 2 ESP-32 S3 Devkit-C1 boards with the Core 1121-HF LoRa module are required, and this project is run in VS Code with the PlatformIO extension.</li>
  <li>Important! When flashing code onto the ESP-32 board, ensure the target file is in the src folder of the LoRa Satellite Simulation folder. In addition, make sure no other .cpp files are in the src folder.</li>
</ul>
