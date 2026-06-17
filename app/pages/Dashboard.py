import streamlit as st
import pandas as pd
import altair as alt
from backend.storage.db_commands import *

st.title('TT&C Dashboard')
state = get_record()
mode = get_mode()

col1, col2 = st.columns([0.5, 0.5], vertical_alignment="center")
with col1:
    with st.container(border=True, height=200):
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
        current_mode = "SAT" if mode else "GND"
        if state == 0:
            selection = st.pills("Recording modes", options, selection_mode="single", default=current_mode, required=True)
            new_mode_val = 1 if selection == "SAT" else 0
            
            # If the user selected a different option than what is in the DB, update and refresh
            if new_mode_val != mode:
                set_mode(new_mode_val)
                st.rerun()
                
            st.write(f"Selected mode: {selection}")
        else:
            selection = st.pills("Recording modes", options, selection_mode="single", disabled=True)
            st.info("You cannot change the configuration while recording.")

total_packets = count(1, 1)
def metrics(packets):
    scales_selection = alt.selection_interval(
        bind='scales',
        encodings=['x']
    )
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(6, gap="medium", width=1500)
        with cols[0]:
            st.metric(
                "Packets logged",
                f"{packets}",
            )

    if mode == 0:
        df = getData(["ID", "snr"])
        pdr = (count("\"PACKET\"", "\"type\"") / packets * 100) if packets > 0 else 0.0
        corrupt = count("\"DATA_ERR\"", "\"type\"")
        dropped = count("\"LINK_ERR\"", "\"type\"")

        with cols[1]:
            st.metric(
                "PDR", 
                f"{pdr:.1f}%"
            )
        with cols[2]:
            st.metric(
                "Corrupted packets", 
                f"{corrupt}"
            )
        with cols[3]:
            st.metric(
                "Dropped packets", 
                f"{dropped}"
            )
        st.subheader("SNR Graph")
        chart = alt.Chart(df).mark_line(color='#38bdf8').encode(
            x=alt.X(
                'ID:Q', 
                title='Frame ID',
                axis=alt.Axis(format='d', tickMinStep=1),
                scale=alt.Scale(
                    domain=[df['ID'].min(), df['ID'].max()],            
                    clamp=True)
            ),
            y=alt.Y(
                'snr:Q', 
                title='SNR (dB)',
                scale=alt.Scale(domain=[0, df['snr'].max()*1.5], clamp=True)
            )
        ).add_params(
            scales_selection
        ).properties(
            width='container',
            height=350
        )
        st.altair_chart(chart, width="stretch")

    elif mode == 1:
        df = getData(["ID", "time"])
        st.subheader("ToA Graph")
        chart = alt.Chart(df).mark_line(color='#38bdf8').encode(
            x=alt.X(
                'ID:Q', 
                title='Frame ID',
                axis=alt.Axis(format='d', tickMinStep=1),
                scale=alt.Scale(
                    domain=[df['ID'].min(), df['ID'].max()],            
                    clamp=True)
            ),
            y=alt.Y(
                'time:Q', 
                title='Time on Air (μs)',
                scale=alt.Scale(domain=[0, df['time'].max()*1.5], clamp=True)
            )
        ).add_params(
            scales_selection
        ).properties(
            width='container',
            height=350
        )
        st.altair_chart(chart, width="stretch")


@st.fragment(run_every="1s")
def checkData():
    total_packets = count(1, 1)
    if (total_packets > 0):
        metrics(total_packets)
    else:
        st.info("No data available yet.")

checkData()