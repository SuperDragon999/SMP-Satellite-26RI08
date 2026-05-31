import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from backend.storage.db_commands import *

st.title('Satellite TT&C')

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

total_packets = count("\"PACKET\"", "type") + count("\"DROP\"", "type")
def metrics():
    avg_latency = getAvg("latency")
    df = get_telemetry_df()
    floor_count = len(df[df['latency'] < 1500])
    retry_1_count = len(df[(df['latency'] >= 1500) & (df['latency'] < 2800)])
    retry_2_count = len(df[(df['latency'] >= 2800) & (df['latency'] < 4500)])
    critical_count = len(df[df['latency'] >= 4500])
    
    determinism_index = (floor_count / total_packets) * 100
    max_jitter = df['jitter'].max()
    avg_jitter = df['jitter'].mean()

    pdr = (1-(count("\"DROP\"", "type") / total_packets))*100
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(4, gap="medium", width=1000)
        with cols[0]:
            st.metric(
                "Average latency",
                f"{avg_latency:.1f} μs",
                width="content",
            )
        with cols[1]:
            st.metric(
                "Average jitter",
                f"{avg_jitter:.1f} μs",
               
                width = "content"
            )
        with cols[2]:
            st.metric(
                "Max jitter",
                f"{max_jitter:.1f} μs"
            )
        with cols[3]:
            st.metric(
                label="Baseline transmission percentage", 
                value=f"{determinism_index:.1f}%", 
                help="Percentage of frames completing on the absolute first attempt (<1.5μs)"
            )
        cols = st.columns(2, gap="medium", width=500)
        with cols[0]:
            st.metric(
                "Packet Delivery Ratio",
                f"{pdr:.1f} %",
                width="content",
            )
        with cols[1]:
            st.metric(
                "Packets logged",
                f"{total_packets}",
                width = "content"
            )

    graphs = st.columns(2, gap="medium")
    st.subheader("Latency graph")
    df2 = getData(["ID", "latency"])
    scales_selection = alt.selection_interval(
        bind='scales', 
        encodings=['x']
    )

    chart = alt.Chart(df2).mark_line(color='#38bdf8').encode(
        x=alt.X(
            'ID:Q', 
            title='Frame ID',
            axis=alt.Axis(format='d', tickMinStep=1),
            scale=alt.Scale(
                domain=[df2['ID'].min(), df2['ID'].max()],            
                clamp=True)
        ),
        y=alt.Y(
            'latency:Q', 
            title='Latency (μs)',
            scale=alt.Scale(domain=[0, 8000], clamp=True)
        )
    ).add_params(
        scales_selection
    ).properties(
        width='container',
        height=350
    )

    st.altair_chart(chart, use_container_width=True)
    with graphs[0]:
        categories = ['Base Floor (<1.5μs)', 'Retry Tier 1 (1.5-2.8μs)', 'Retry Tier 2 (2.8-4.5μs)', 'Critical (>4.5μs)']
        counts = [floor_count, retry_1_count, retry_2_count, critical_count]
        colors = ['#10b981', '#f59e0b', '#ef4444', '#7f1d1d']
        
        hist_df = pd.DataFrame({'Latency Category': categories, 'Packet Count': counts, 'Color': colors})
        
        fig_hist = px.bar(
            hist_df, 
            x='Latency Category', 
            y='Packet Count',
            color='Latency Category',
            color_discrete_sequence=colors,
            template="plotly_dark"
        )
        fig_hist.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=350)
        st.plotly_chart(fig_hist, use_container_width=True, key="hist")
    with graphs[1]:
        st.subheader("Discrete Packet-to-Packet Jitter Profile")
        
        fig_line = px.line(
            df, 
            x='ID', 
            y='jitter',
            labels={'ID': 'Frame ID', 'jitter': 'Jitter (μs)'},
            template="plotly_dark"
        )
        fig_line.update_traces(marker=dict(size=6, color='#38bdf8', opacity=0.7))
        fig_line.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
        st.plotly_chart(fig_line, use_container_width=True, key="jitter")

@st.fragment(run_every="1s")
def checkData():
    total_packets = count("\"PACKET\"", "type") + count("\"DROP\"", "type")
    if (total_packets > 0):
        metrics()
    else:
        st.info("No data available yet.")

checkData()