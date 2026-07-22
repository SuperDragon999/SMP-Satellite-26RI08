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

display()

mode = get_mode()
_, phase = get_runtime_db_context()
if mode == 0:
    if phase == 2:
        df_manage = getData(["ID", "type", "data1", "data2", "status"], 1) # Phase 2
    elif phase == 1:
        df_manage = getData(["ID", "type", "data1", "data2", "snr"], 1) # Phase 1
elif mode == 1:
    df_manage = getData(["ID", "time"], 1)

if not df_manage.empty:
    with st.container():
        if mode == 0:
            with st.container():
                st.subheader("Delete entry from GND data table.")
                st.warning("Deletion actions cannot be undone.")
                
                # Use columns to lay out the 5 parameters cleanly
                r1_col1, r1_col2 = st.columns(2)
                with r1_col1:
                    input_id = st.number_input("Enter Frame ID:", step=1, value=0, placeholder="Type ID...")
                with r1_col2:
                    # Select from the existing packet types in the DB to avoid typos
                    unique_types = list(df_manage["type"].unique())
                    input_type = st.selectbox("Select Packet Type:", options=unique_types, index=None, placeholder="Choose type...")
                
                r2_col1, r2_col2, r2_col3 = st.columns(3)
                with r2_col1:
                    input_d1 = st.number_input("Enter Data 1:", step=1, value=None, placeholder="Type data1...")
                with r2_col2:
                    input_d2 = st.number_input("Enter Data 2:", step=1, value=None, placeholder="Type data2...")
                with r2_col3:
                    if phase == 1:
                        input_status = st.number_input("Enter exact SNR", step=0.1, value=None, placeholder="Type snr...")
                    elif phase == 2:
                        input_status = st.number_input("Enter exact status", step = 1, value=None, placeholder="Type status...")
                
                # Explicit confirmation checkbox
                safety_lock = st.checkbox("I confirm I want to wipe this specific tracking data row from history.")
                
                # Evaluate if all fields are validly filled out
                all_fields_filled = all([
                    input_id is not None,
                    input_type is not None,
                    input_d1 is not None,
                    input_d2 is not None,
                    input_status is not None
                ])
                
                # The button is disabled unless every parameter is filled and the lock is checked
                if st.button("Execute Deletion Routine", type="primary", disabled=not (all_fields_filled and safety_lock)):
                    
                    # Query our local dataframe to see if this exact entry actually exists
                    match = df_manage[
                        (df_manage["ID"] == input_id) & 
                        (df_manage["type"] == input_type) & 
                        (df_manage["data1"] == input_d1) & 
                        (df_manage["data2"] == input_d2) &
                        (df_manage["status"] == input_status) if phase == 2 else (df_manage["snr"] == input_status) # type: ignore
                    ]
                    
                    if not match.empty:
                        # Execute database removal
                        rows_removed = deleteEntry(
                            int(input_id), 
                            input_type, 
                            int(input_d1), # type: ignore
                            int(input_d2), # type: ignore
                            float(input_status) if phase == 1 else int(input_status) # type: ignore
                        )
                        st.success(f"Success!")
                        st.rerun()
                    else:
                        st.error("Deletion Failed: No record in the database matches that exact combination of parameters. Verify your inputs.")
        elif mode == 1:
            with st.container():
                st.subheader("Delete entry from SAT ToA table.")
                st.warning("Deletion actions cannot be undone.")
                input_id = st.number_input("Enter Frame ID to verify:", step=1, value=None, placeholder="Type ID here...")
                input_time = st.number_input("Enter exact Time on Air (μs):", step=1, value=None, placeholder="Type ToA value here...")

                safety_lock = st.checkbox("I confirm I want to wipe this entry from the database.")
                
                # The button only executes if the inputs are filled and safety lock is ticked
                if st.button("Execute Deletion Routine", type="primary", disabled=not (input_id is not None and input_time is not None and safety_lock)):
                    
                    # Double check if the provided parameters actually exist
                    match = df_manage[(df_manage["ID"] == input_id) & (df_manage["time"] == input_time)]
                    
                    if not match.empty:
                        # Execute database removal
                        deleteToA(int(input_id), int(input_time)) # type: ignore

                        st.success(f"Success!")
                        st.rerun()
                    else:
                        st.error("Deletion Failed: No record in the database matches that exact ID and Time combination. Check your inputs.")

        with st.container():
            st.subheader("Clear table")
            st.warning("Are you sure you want to clear all logged data? This cannot be undone.")
            safety_lock = st.checkbox("I confirm I want to wipe this table.")
            if st.button("Yes, clear database", type="primary", disabled=not safety_lock):
                clearData()
                st.toast("Data table has been cleared", icon="🗑️")
else:
    st.info("Database controls are not shown as the table is currently empty.")