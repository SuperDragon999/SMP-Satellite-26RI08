import streamlit as st
from backend.storage.db_commands import *

st.set_page_config(layout="wide")

pages = {
    "Main": [st.Page("pages/Dashboard.py",  title = "Dashboard", icon = "🛰️")],
    "Data Analysis": [
        st.Page("pages/Logs.py", title="Logs", icon="💻"),
        st.Page("pages/Packet Inspector.py", title="Packet Inspector", icon="🔍"),
    ]
}

pg = st.navigation(pages)

col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")
with col1:
    st.subheader("Recording status:")

with col2:
    if get_record():
        st.badge("Recording", color="red", width=100)
    else:
        st.badge("Idle", color="blue", width=100)
st.divider()
# Run the selected page
pg.run()