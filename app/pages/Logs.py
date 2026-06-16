import streamlit as st
import pandas as pd
from backend.storage.db_commands import *

st.title("Logs")
@st.fragment(run_every="1s")
def display():
    df = readAllData()
    st.dataframe(df, hide_index=True)

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

with st.popover("Clear Data"):
    st.warning("Are you sure you want to clear all logged data? This cannot be undone.")

    if st.button("Yes, clear database", type="primary"):
        clearData()
        st.toast("Data table has been cleared", icon="🗑️")

display()