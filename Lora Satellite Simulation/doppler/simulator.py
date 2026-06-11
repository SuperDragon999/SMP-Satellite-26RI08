import altair as alt
import numpy as np
import pandas as pd

total_time = 800
f_carrier = 433e6
v_sat = 7500
c = 3e8
max_doppler = (v_sat / c) * f_carrier # ~10,825 Hz

time_steps = np.linspace(-400, 400, 100)

# Distance calculations in meters
distance_traveled = v_sat * time_steps
altitude_meters = 600000 

# True geometric Doppler calculation
doppler_offsets = -max_doppler * (distance_traveled / np.sqrt(distance_traveled**2 + altitude_meters**2))

df = pd.DataFrame({
    "Time Step (s)": time_steps,
    "Doppler Shift (Hz)": doppler_offsets,
    "Array Index": np.arange(len(time_steps))
})

chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("Time Step (s):Q", title="Time Relative to Zenith (seconds)"),
    y=alt.Y("Doppler Shift (Hz):Q", title="Doppler Frequency Shift (Hz)"),
    tooltip=["Array Index:Q", "Time Step (s):Q", "Doppler Shift (Hz):Q"]
).properties(
    title="S-Curve: Simulated LEO Satellite Doppler (433 MHz)",
    width=600,
    height=400
).interactive()

chart.save("doppler/doppler_curve.html")