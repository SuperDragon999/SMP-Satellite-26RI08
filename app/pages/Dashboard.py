import streamlit as st
import json, sqlite3
import altair as alt
from backend.storage.db_commands import *
from backend.storage.setup import *
from pathlib import Path

st.title('Experiment Dashboard')

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.json"
data_dir = project_root / "backend" / "storage" / "data"
available_dbs = sorted([f.stem for f in data_dir.glob("*.db")]) if data_dir.exists() else []

state = get_record()
mode = get_mode()

with open(config_path, "r") as f:
    config = json.load(f)

active_db = config.get("db_name")
current_port = config.get("serial_port")

def get_db_meta(name):
    """Queries the internal DB layer directly for operational context."""
    conn = sqlite3.connect(data_dir / f"{name}.db")
    try:
        res = conn.execute("SELECT phase, mode FROM ctrl ORDER BY rowid DESC LIMIT 1").fetchone()
        return res if res else (None, None)
    except sqlite3.Error:
        return None, None
    finally:
        conn.close()

if not state:
    with st.expander("Database selector", expanded=True):
        selected_db = st.selectbox(
            "Select active database:", 
            options=available_dbs, 
            index=available_dbs.index(active_db) if active_db in available_dbs else 0
        )
        phase, mode = get_db_meta(selected_db)
        # If the target database is missing internal metadata, collect it inline
        if phase is None or mode is None:
            st.warning("Database parameters not initialized.")
            phase = st.selectbox("Experimental Phase:", [1, 2], key="p_sel")
            mode = st.radio("System Mode:", ["SAT", "GND"], key="m_sel")
            
            if st.button("Initialize"):
                conn = sqlite3.connect(data_dir / f"{selected_db}.db")
                setup(conn, 1 if mode == "SAT" else 0, phase)
                set_mode(mode)
                conn.close()
                
                # Commit new config.json
                with open(config_path, "w") as f:
                    json.dump({"db_name": selected_db, "serial_port": current_port}, f, indent=4)
                st.rerun()
            st.stop()

    if selected_db != active_db:
        with open(config_path, "w") as f:
            json.dump({"db_name": selected_db, "serial_port": current_port}, f, indent=4)
        st.rerun()

phase, mode = get_db_meta(active_db)
st.info(f"Connected: **{active_db}.db** | Phase: {phase} | Port: {current_port}")

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

total_packets = count(1, 1) # sql injection here to get the total packet number
def metrics(packets):
    scales_selection = alt.selection_interval(
        bind='scales',
        encodings=['x']
    )
    with st.container(horizontal=True, gap="medium"):
        if mode == 0:
            cols = st.columns(5, gap="medium", width=1500)
        elif mode == 1:
            cols = st.columns(3, gap="medium", width=1500)
        with cols[0]:
            st.metric(
                "Packets logged",
                f"{packets}",
            )

    if mode == 0:
        #df = getData(["ID", "snr"], 0) # we do not include failed packets here
        #avg_snr = getData(["snr"], 0)["snr"].mean()
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
        # with cols[4]:
        #     st.metric(
        #         "Average SNR",
        #         f"{avg_snr:.1f} dB"
        #     )
        # st.subheader("SNR Graph")
        # chart = alt.Chart(df).mark_line(color='#38bdf8').encode(
        #     x=alt.X(
        #         'ID:Q', 
        #         title='Frame ID',
        #         axis=alt.Axis(format='d', tickMinStep=1),
        #         scale=alt.Scale(
        #             domain=[df['ID'].min(), df['ID'].max()],            
        #             clamp=True)
        #     ),
        #     y=alt.Y(
        #         'snr:Q', 
        #         title='SNR (dB)',
        #         scale=alt.Scale(domain=[-15, 15], clamp=True)
        #     )
        # ).add_params(
        #     scales_selection
        # ).properties(
        #     width='container',
        #     height=350
        # )
        # st.altair_chart(chart, width="stretch")

    elif mode == 1:
        df = getData(["ID", "time"], 0) # no failed packets
        avg_processing_df = getData(["time"], 0)["time"]
        avg_processing = avg_processing_df.mean() if not avg_processing_df.empty else 0.0
        total_processing_df = getData(["time"], 0)["time"]
        total_processing = total_processing_df.sum() / 1000000 
        with cols[1]:
            st.metric(
                "Average Processing Time", 
                f"{avg_processing:.1f} μs"
            )
        with cols[2]:
            st.metric(
                "Total Processing Time",
                f"{total_processing} s"
            )
        st.subheader("Processing Time Graph")
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