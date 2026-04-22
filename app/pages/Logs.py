import streamlit as st
import sqlite3
import pandas as pd
from backend.storage.db_commands import *

st.title("Logs")
tab1, tab2 = st.tabs(["Packets", "Commands"])
with tab1:
    df = readAllData()
    st.dataframe(df, hide_index=True)
with tab2:
    df = readAllCmd()
    st.dataframe(df, hide_index=True)