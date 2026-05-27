import streamlit as st
import sqlite3
import pandas as pd
from backend.storage.db_commands import *

st.title("Logs")
@st.fragment(run_every="1s")
def display():
    df = readAllData()
    st.dataframe(df, hide_index=True)

with st.popover("Clear Data"):
    st.warning("Are you absolutely sure you want to clear all logged data? This cannot be undone.")

    if st.button("Yes, clear database", type="primary"):
        clearData()
        st.toast("Data table has been cleared", icon="🗑️")
display()