import streamlit as st
import sqlite3
import pandas as pd
from backend.storage.db_commands import *

st.title("Logs")
@st.fragment(run_every="1s")
def display():
    tab1, tab2 = st.tabs(["Packets", "Tests"])
    with tab1:
        df = readAllData()
        st.dataframe(df, hide_index=True)
    with tab2:
        df = testRead()
        st.dataframe(df, hide_index=True)
        
display()