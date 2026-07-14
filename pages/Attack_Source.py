"""
Threat Attribution & Resolution page component.
Renders threat vector analysis, defense mechanism comparisons, and attribution pie charts.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd
import plotly.express as px

from frontend.layout import COLOR_PALETTE, PLOTLY_THEME_LAYOUT

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Threat Attribution & Resolution page."""
    st.markdown("<h1>Threat Attribution & Resolution</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Correlate threat actors, defense controls, and containment times to evaluate security resolution efficiency."
        "</p>",
        unsafe_allow_html=True
    )
    
    global_df = datasets["global_threats"]
    sigs_df = datasets["attack_signatures"]
    
    if global_df.empty:
        st.warning("No global threats data matches the selected filters. Please adjust the sidebar choices.")
        return
        
    # 1. Main Strip Plot: Resolution Time by Defense Strategy (Matches Figure 4.6 & Section 4.7 of Report)
    st.subheader("Resolution Time by Defense Strategy")
    fig_strip = px.strip(
        global_df,
        x="defense_mechanism_used" if "defense_mechanism_used" in global_df.columns else None,
        y="incident_resolution_time_in_hours" if "incident_resolution_time_in_hours" in global_df.columns else None,
        color="attack_type" if "attack_type" in global_df.columns else None,
        labels={
            "defense_mechanism_used": "Defense Strategy",
            "incident_resolution_time_in_hours": "Resolution Time (Hours)",
            "attack_type": "Attack Vector"
        },
        color_discrete_sequence=[
            COLOR_PALETTE["primary"], 
            COLOR_PALETTE["secondary"], 
            COLOR_PALETTE["accent"], 
            COLOR_PALETTE["neon_pink"],
            COLOR_PALETTE["neon_green"],
            COLOR_PALETTE["neon_yellow"]
        ]
    )
    fig_strip.update_layout(**PLOTLY_THEME_LAYOUT, height=450, margin={"t": 40, "b": 30, "l": 30, "r": 30})
    st.plotly_chart(fig_strip, use_container_width=True)
    
    # 2. Side-by-Side: Threat Actor Attribution and Network Protocol Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threat Actor Attribution")
        if "attack_source" in global_df.columns:
            source_counts = global_df["attack_source"].value_counts().reset_index()
            fig_source = px.pie(
                source_counts,
                names="attack_source",
                values="count",
                hole=0.4,
                color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"]]
            )
            fig_source.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_source, use_container_width=True)
        else:
            st.info("No threat actor data available.")
            
    with col2:
        st.subheader("Network Intrusion Protocols Share")
        if not sigs_df.empty and "protocol" in sigs_df.columns:
            proto_counts = sigs_df.groupby("protocol").size().reset_index(name="Log Count")
            fig_pie = px.pie(
                proto_counts,
                values="Log Count",
                names="protocol",
                color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"]],
                hole=0.4
            )
            fig_pie.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No network protocol logs match current filters.")
            
    with st.expander("Threat Containment & Attribution Insights"):
        st.markdown(f"""
        *   **Resolution Times vs Defense Controls:** The strip plot demonstrates the operational resolution hours across different defense configurations. Notice the dense clusters indicating how containment time is distributed across attack types.
        *   **Attribution share:** Nation-state groups and advanced insider threats typically represent distinct risk profiles in financial damage per security event.
        """)

    # 3. Reference Report Plot
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Show Static Reference Report Plot"):
        st.image("images/attack_source.png", caption="Figure 4.6: Resolution time (hours) by defense strategy, colored by attack vector", use_container_width=True)
