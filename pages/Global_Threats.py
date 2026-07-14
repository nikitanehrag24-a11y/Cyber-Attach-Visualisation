"""
Global Threats page component.
Displays threat trends, line/area charts, and year/country filter insights.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd
import plotly.express as px

from frontend.components import render_global_trend_chart
from frontend.layout import COLOR_PALETTE, PLOTLY_THEME_LAYOUT

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Global Threat trends page."""
    st.markdown("<h1>Global Threat & Incident Evolution</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Analyze how cyber attack volumes, frequencies, and vectors evolve over the years."
        "</p>",
        unsafe_allow_html=True
    )
    
    global_df = datasets["global_threats"]
    temporal_df = datasets["integrated_temporal"]
    
    if global_df.empty or temporal_df.empty:
        st.warning("No data matches the selected filters. Please adjust the sidebar choices.")
        return
        
    # 1. Side-by-side Trends & Economic Damage
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Annual Cyber Incidents Trends")
        fig_volume = render_global_trend_chart(temporal_df)
        st.plotly_chart(fig_volume, use_container_width=True)
    with col_t2:
        st.subheader("Economic Damage Impact")
        fig_loss = px.area(
            temporal_df[temporal_df["avg_financial_loss"] > 0],
            x="year", y="avg_financial_loss",
            labels={"avg_financial_loss": "Average Financial Loss (Millions USD)", "year": "Year"},
            color_discrete_sequence=['#9900FF']
        )
        fig_loss.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
        st.plotly_chart(fig_loss, use_container_width=True)
    
    # 2. Side-by-side comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attack Type Breakdown Over Time")
        if "year" in global_df.columns and "standard_attack_type" in global_df.columns:
            pivot_attacks = global_df.groupby(["year", "standard_attack_type"]).size().reset_index(name="Count")
            fig_types = px.line(
                pivot_attacks,
                x="year",
                y="Count",
                color="standard_attack_type",
                labels={"year": "Year", "Count": "Alerts"},
                title="Attack Vectors Timeline"
            )
            fig_types.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_types, use_container_width=True)
            
    with col2:
        st.subheader("Incidents by Security Vulnerability Vector")
        if "security_vulnerability_type" in global_df.columns:
            vuln_types = global_df.groupby("security_vulnerability_type").size().reset_index(name="Count")
            fig_vuln = px.bar(
                vuln_types,
                x="Count",
                y="security_vulnerability_type",
                orientation="h",
                color="Count",
                color_continuous_scale=[[0.0, "rgba(17, 25, 40, 0.6)"], [1.0, COLOR_PALETTE["secondary"]]],
                labels={"security_vulnerability_type": "Vector Type", "Count": "Incidents"},
                title="Primary Vulnerability Vectors"
            )
            fig_vuln.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_vuln, use_container_width=True)
            
    # 3. Trends & Insight Box
    st.subheader("Intelligence Insights")
    st.markdown(
        f"""
        <div class="metric-card">
            <ul>
                <li><strong>Current Filtered Dataset Size:</strong> Analyzing <strong>{len(global_df):,}</strong> global cyber threat alerts.</li>
                <li><strong>Peak Threat Period:</strong> Historically, years like 2017 and 2022 recorded the highest attack frequencies globally.</li>
                <li><strong>Prevalent Vector:</strong> <code>DDoS</code> and <code>Phishing</code> remain the most common attack vectors, constituting the majority of the alert logs.</li>
                <li><strong>Defense Performance:</strong> Incidents utilizing <code>Ai-Based Detection</code> and <code>Firewall</code> configurations reported faster resolution times than legacy antivirus methods.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


