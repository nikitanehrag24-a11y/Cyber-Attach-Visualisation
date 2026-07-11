"""
Attack Source page component.
Renders vectors comparison charts and scatter plots from the intrusion signatures dataset.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd
import plotly.express as px

from frontend.components import render_attack_source_scatter
from frontend.layout import COLOR_PALETTE, PLOTLY_THEME_LAYOUT

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Attack Source Dashboard view."""
    st.markdown("<h1>⚔️ Intrusion & Vector Analysis</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Drill down into network traffic forensics, package characteristics, and threat source categories."
        "</p>",
        unsafe_allow_html=True
    )
    
    sigs_df = datasets["attack_signatures"]
    global_df = datasets["global_threats"]
    
    if sigs_df.empty:
        st.warning("No intrusion logs match the selected filters. Please adjust the sidebar choices.")
        return
        
    # 1. Main Network Forensics Scatter
    st.subheader("Network Packet Forensics Matrix")
    fig_scatter = render_attack_source_scatter(sigs_df)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 2. Side-by-Side: Vector counts and Protocol spreads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threat Sources compared to Resolution Time")
        if not global_df.empty:
            avg_times = global_df.groupby("attack_source")["incident_resolution_time_in_hours"].mean().reset_index(name="Avg Resolution Time")
            fig_vector_bar = px.bar(
                avg_times,
                x="attack_source",
                y="Avg Resolution Time",
                color="Avg Resolution Time",
                color_continuous_scale="Teal",
                labels={"attack_source": "Threat Vector", "Avg Resolution Time": "Resolution Time (Hrs)"},
                title="Avg Hours to Resolve by Actor Category"
            )
            fig_vector_bar.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_vector_bar, use_container_width=True)
        else:
            st.info("No global threats data matches filters to calculate resolution averages.")
            
    with col2:
        st.subheader("Network Protocol Distribution")
        if "protocol" in sigs_df.columns:
            proto_counts = sigs_df.groupby("protocol").size().reset_index(name="Log Count")
            fig_pie = px.pie(
                proto_counts,
                values="Log Count",
                names="protocol",
                color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"]],
                title="Intrusion Protocols Share"
            )
            fig_pie.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with st.expander("💡 Intrusion Forensics Insights"):
        st.markdown(f"""
        *   **Anomaly Scores vs Packet Length:** High anomaly scores paired with large packet sizes typically indicate payload-based exploits (like SQL Injection or Buffer Overflow attacks) or data exfiltration.
        *   **Protocol Distribution:** Compares the usage of standard network layers (TCP, UDP, ICMP) in intrusion logs.
        """)
