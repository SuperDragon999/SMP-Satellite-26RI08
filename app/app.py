import streamlit as st

st.set_page_config(layout="wide")

pages = {
    "Main": [st.Page("pages/Dashboard.py",  title = "Dashboard", icon = "🛰️")],
    "Data Analysis": [
        st.Page("pages/Logs.py", title="Logs", icon="💻"),
        st.Page("pages/Packet Inspector.py", title="Packet Inspector", icon="🔍"),
    ]
}

pg = st.navigation(pages)

# Run the selected page
pg.run()