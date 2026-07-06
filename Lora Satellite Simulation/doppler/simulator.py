import altair as alt
import numpy as np
import pandas as pd

# Simulation constants
total_time = 560
f_carrier = 915e6
v_sat = 7800
c = 3e8
r_earth = 6371000
r_sat = r_earth + 500000

# Compute orbital angular velocity (rad/s)
omega = v_sat / r_sat

# np.arange eliminates floating-point interpolation stretch, giving 560 steps
time_steps = np.arange(-total_time // 2, total_time // 2, 1)

# Calculate slant range (rho) over the 1-second grid
rho = np.sqrt(r_sat**2 + r_earth**2 - 2 * r_sat * r_earth * np.cos(omega * time_steps))

# Calculate line-of-sight velocity component
v_los = (v_sat * r_earth * np.sin(omega * time_steps)) / rho

# Compute the final s-curve Doppler offsets
doppler_offsets = -(v_los / c) * f_carrier

# Compute Doppler rate
doppler_rate = np.gradient(doppler_offsets, 1.0)

df = pd.DataFrame({
    "Elapsed Second": np.arange(len(time_steps)),
    "Time Relative to Zenith (s)": time_steps,
    "Doppler Shift (Hz)": doppler_offsets,
    "Doppler Rate (Hz/s)": doppler_rate,
    "Slant Range (m)": rho
})

chart_doppler = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Doppler Shift (Hz):Q", title="Doppler Frequency Shift (Hz)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Doppler Shift (Hz):Q"]
).properties(
    title="Doppler Profile of a 560s LEO Satellite Pass",
    width=675, height=450
).interactive()
chart_doppler.save("doppler/doppler_curve.html")

chart_rate = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Doppler Rate (Hz/s):Q", title="Doppler Rate (Hz/s)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Doppler Rate (Hz/s):Q"]
).properties(
    title="Doppler Rate Profile of a 560s LEO Satellite Pass",
    width=675, height=450
).interactive()
chart_rate.save("doppler/doppler_rate_curve.html")

chart_dist = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Slant Range (m):Q", title="Slant Range (m)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Slant Range (m):Q"]
).properties(
    title="Slant Range Profile of a 560s LEO Satellite Pass",
    width=675, height=450
).interactive()
chart_dist.save("doppler/slant_range_curve.html")

print("// 1. DOPPLER FREQUENCY SHIFT ARRAY (Hz)")
print("\n")
formatted_doppler = np.array2string(
    doppler_offsets, 
    max_line_width=80, 
    separator=", ", 
    prefix="{",
    suffix="};",
    formatter={'float_kind': lambda x: f"{x:.4f}"}
)
print(formatted_doppler)
print("\n")

print("\n")
print("// 2. DOPPLER RATE ARRAY (Hz/s)")
print("\n")
formatted_rate = np.array2string(
    doppler_rate, 
    max_line_width=80, 
    separator=", ", 
    prefix="{",
    suffix="};",
    formatter={'float_kind': lambda x: f"{x:.4f}"}
)
print(formatted_rate)
print("\n")

print("\n")
print("// 3. SLANT RANGE ARRAY (m)")
print("\n")
formatted_dist = np.array2string(
    rho, 
    max_line_width=80, 
    separator=", ", 
    prefix="{",
    suffix="};",
    formatter={'float_kind': lambda x: f"{x:.2f}"}
)
print(formatted_dist)