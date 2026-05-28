import streamlit as st
import pandas as pd
import numpy as np
import time
from backend.storage.db_commands import *
from backend.services.fetch import stream_telemetry

st.title('Satellite TT&C')

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
st.write("-1 reading means a packet drop.")
#Graphs of data, ping, etc. go here
@st.fragment(run_every="1s")
def showData():
    df = readAllData()
    st.bar_chart(df, x="ID", y=["sensor", "latency"])
    df2 = getData(["ID", "latency"])
    st.line_chart(df2, x="ID")
    df3 = getData(["ID", "sensor"])
    st.line_chart(df3, x="ID")

showData()