import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
db_path = project_root / "backend" / "storage" / "data" / "dataLogs.db"

st.title("Logs")
tab1, tab2 = st.tabs(["Packets", "Commands"])
with tab1:
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql_query("SELECT * FROM data", conn)
    st.write(df)
with tab2:
    pass