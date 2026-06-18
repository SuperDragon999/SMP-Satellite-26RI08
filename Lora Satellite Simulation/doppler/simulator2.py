import altair as alt
import numpy as np
import pandas as pd

total_time = 800
f_carrier = 915e6
v_sat = 7800
c = 3e8
r_earth = 6371000
r_sat = r_earth + 500000

omega = v_sat / r_sat
time_steps = np.arange(-total_time // 2, total_time // 2, 1)

rho = np.sqrt(r_sat**2 + r_earth**2 - 2 * r_sat * r_earth * np.cos(omega * time_steps))
v_los = (v_sat * r_earth * np.sin(omega * time_steps)) / rho
doppler_offsets = -(v_los / c) * f_carrier

doppler_rate = np.gradient(doppler_offsets, 1.0)

df_rate = pd.DataFrame({
    "Elapsed Second": np.arange(len(time_steps)),
    "Time Relative to Zenith (s)": time_steps,
    "Doppler Rate (Hz/s)": doppler_rate
})

chart_rate = alt.Chart(df_rate).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Doppler Rate (Hz/s):Q", title="Doppler Rate (Hz/s)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Doppler Rate (Hz/s):Q"]
).properties(
    title="Doppler Rate Profile of an 800s LEO Satellite Pass",
    width=675,
    height=450
).interactive()

chart_rate.save("doppler/doppler_rate_curve.html")

formatted_rate_array = np.array2string(doppler_rate, max_line_width=80, separator=", ")
print(formatted_rate_array)