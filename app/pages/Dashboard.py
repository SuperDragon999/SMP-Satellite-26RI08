import streamlit as st
import pandas as pd
import altair as alt
from backend.storage.db_commands import *

st.title('TT&C Dashboard')

col1, col2 = st.columns([0.5, 0.5], vertical_alignment="center")
with col1:
    with st.container(border=True, height=200):
        state = get_record()
        st.write("Control data input")
        if state == 0:
            if st.button("Start Recording", type="primary", use_container_width=True):
                set_record(1)
                st.rerun()
        else:
            # Active State: Urgent Status Indicator & Stop Mechanism
            st.error("⏺ System is currently recording data...")
            
            with st.popover("Stop Recording", use_container_width=True):
                st.warning("This stop the current recording. Are you sure?")
                if st.button("Yes, stop recording", type="primary", use_container_width=True):
                    set_record(0)
                    st.rerun()
with col2:
    with st.container(border=True, height=200):
        options = ["SAT", "GND"]
        mode = "SAT" if get_mode() else "GND"
        if state == 0:
            selection = st.pills("Recording modes", options, selection_mode="single", default=mode, required=True)
        else:
            selection = st.pills("Recording modes", options, selection_mode="single", disabled=True)
            st.info("You cannot change the configuration while recording.")

total_packets = count(1, 1)
def metrics():
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(6, gap="medium", width=1500)
        with cols[0]:
            st.metric(
                "Packets logged",
                f"{total_packets}",
            )

    st.subheader("SNR Graph")
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
    total_packets = count(1, 1)
    if (total_packets > 0):
        metrics()
    else:
        st.info("No data available yet.")

checkData()