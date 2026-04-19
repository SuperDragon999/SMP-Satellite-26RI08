import streamlit as st

st.set_page_config(layout="wide")

pages = {
    "Main": [st.Page("pages/Dashboard.py",  title = "Dashboard")],
    "Data Analysis": [
        st.Page("pages/Telemetry.py", title="Telemetry", icon="📈"),
        st.Page("pages/Logs.py", title="Logs"),
        st.Page("pages/Packet Inspector.py", title="Packet Inspector", icon="🔍"),
    ],
    "Commands": [
        st.Page("pages/Command And Control.py", title="Command and Control", icon="🕹️"),
    ]
}

pg = st.navigation(pages)

# Logic for the Common Navbar / Header
st.markdown("### NORBY | Status: ACTIVE | Last Packet: |")
st.divider()

# Run the selected page
pg.run()