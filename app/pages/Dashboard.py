import streamlit as st
import pandas as pd
import altair as alt
from backend.storage.db_commands import *

st.title('Ground to Satellite Telemetry Dashboard')

state = get_record()
if state == 0:
    with st.status("Control data input", expanded=True) as status:
        if st.button("Start Recording"):
            set_record(1)
            status.update(
                label="Recording data...", state="running", expanded=False
            )
            st.rerun()
elif state == 1:
    with st.popover("Stop Recording"):
        st.warning("Are you sure you want to stop recording?")

        if st.button("Yes, stop", type="primary"):
            set_record(0)
            st.rerun()

def metrics():
    #Metrics
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(6, gap="medium", width=1500)
        with cols[0]:
            pass
            # st.metric(
            #     "Average latency",
            #     f"{avg_latency:.1f} μs",
            # )

    # st.subheader("Latency graph")
    # chart = alt.Chart(df2).mark_line(color='#38bdf8').encode(
    #     x=alt.X(
    #         'ID:Q', 
    #         title='Frame ID',
    #         axis=alt.Axis(format='d', tickMinStep=1),
    #         scale=alt.Scale(
    #             domain=[df2['ID'].min(), df2['ID'].max()],            
    #             clamp=True)
    #     ),
    #     y=alt.Y(
    #         'latency:Q', 
    #         title='Latency (μs)',
    #         scale=alt.Scale(domain=[0, df2['latency'].max()*1.5], clamp=True)
    #     )
    # ).add_params(
    #     scales_selection
    # ).properties(
    #     width='container',
    #     height=350
    # )
    # st.altair_chart(chart, width="stretch")    


@st.fragment(run_every="1s")
def checkData():
    total_packets = 0 # Edit to include packet count
    if (total_packets > 0):
        metrics()
    else:
        st.info("No data available yet.")

checkData()