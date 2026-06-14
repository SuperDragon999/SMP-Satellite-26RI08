import altair as alt
import numpy as np
import pandas as pd

# Simulation constants
total_time = 800
f_carrier = 915e6
v_sat = 7800
c = 3e8
r_earth = 6371000
r_sat = r_earth + 500000

# Compute orbital angular velocity (rad/s)
omega = v_sat / r_sat

# np.arange eliminates floating-point interpolation stretch, giving exactly 800 steps
time_steps = np.arange(-total_time // 2, total_time // 2, 1)

# Calculate slant range (rho) over the 1-second grid
rho = np.sqrt(r_sat**2 + r_earth**2 - 2 * r_sat * r_earth * np.cos(omega * time_steps))

# Calculate line-of-sight velocity component
v_los = (v_sat * r_earth * np.sin(omega * time_steps)) / rho

# Compute the final s-curve Doppler offsets
doppler_offsets = -(v_los / c) * f_carrier

# Compile into a DataFrame for visualization
df = pd.DataFrame({
    "Elapsed Second": np.arange(len(time_steps)),
    "Time Relative to Zenith (s)": time_steps,
    "Doppler Shift (Hz)": doppler_offsets
})

# Generate interactive Altair plot
chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Doppler Shift (Hz):Q", title="Doppler Frequency Shift (Hz)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Doppler Shift (Hz):Q"]
).properties(
    title="Doppler Profile of a 800s LEO satellite Pass",
    width=675,
    height=450
).interactive()

chart.save("doppler/doppler_curve.html")

# Format output as a clean C++ array block
formatted_array = np.array2string(doppler_offsets, max_line_width=80, separator=", ")
print(formatted_array)