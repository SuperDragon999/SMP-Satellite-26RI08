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

df_dist = pd.DataFrame({
    "Elapsed Second": np.arange(len(time_steps)),
    "Time Relative to Zenith (s)": time_steps,
    "Slant Range (m)": rho
})

chart_dist = alt.Chart(df_dist).mark_line(point=True).encode(
    x=alt.X("Elapsed Second:Q", title="Simulation Timeline (Seconds)"),
    y=alt.Y("Slant Range (m):Q", title="Slant Range (m)"),
    tooltip=["Elapsed Second:Q", "Time Relative to Zenith (s):Q", "Slant Range (m):Q"]
).properties(
    title="Slant Range Profile of an 800s LEO Satellite Pass",
    width=675,
    height=450
).interactive()

chart_dist.save("doppler/slant_range_curve.html")

formatted_dist_array = np.array2string(rho, max_line_width=80, separator=", ")
print(formatted_dist_array)