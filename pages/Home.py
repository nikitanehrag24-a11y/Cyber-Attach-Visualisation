"""
Home page component.
Renders high-level KPI metric cards and introduces the platform's features and datasets.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from frontend.components import card_kpi, render_risk_choropleth
from backend.analytics import get_kpis
from backend.risk import get_country_risk_scores

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Home Dashboard View."""
    st.markdown("<h1>🛡️ CyberVision Intelligence Command</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Unified Cybersecurity Threat Operations and Intel Analytics Center."
        "</p>",
        unsafe_allow_html=True
    )
    
    # 1. Calculate KPI Metrics
    kpis = get_kpis(datasets["global_threats"], datasets["cfr_incidents"], datasets["vulnerabilities"])
    
    # 2. Render Metric cards in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card_kpi("Global Threat Alerts", f"{kpis['total_attacks']:,}", "🚨")
    with col2:
        card_kpi("Total Financial Impact", f"${kpis['total_loss_million']:,.1f}M", "💰")
    with col3:
        card_kpi("Avg Incident Resolution", f"{kpis['avg_resolution_hours']:.1f} Hrs", "⏳")
    with col4:
        card_kpi("Total Affected Users", f"{kpis['affected_users']:,}", "👥")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Main Dashboard section (Two Columns: Map Preview and Dataset Status)
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.subheader("Global Security Risk Preview")
        # Use full reference dataset for a nice map preview, or filtered if selected
        w_freq, w_loss, w_time = filters.get("weights", (0.3, 0.4, 0.3))
        risk_df = get_country_risk_scores(datasets["global_threats"], w_freq, w_loss, w_time)
        fig_map = render_risk_choropleth(risk_df)
        st.plotly_chart(fig_map, use_container_width=True)
        
        with st.expander("💡 How to Read the Risk Score & Map"):
            st.markdown(f"""
            *   **Risk Index Formulation:** The Risk Score is a normalized scale from **0 to 10** computed dynamically based on three metrics weighted by your sidebar settings:
                1.  **Incident Frequency** ({w_freq:.1%})
                2.  **Average Financial Loss** ({w_loss:.1%})
                3.  **Average Operational Resolution Time** ({w_time:.1%})
            *   **Map Interpretation:** Darker colors represent higher risk levels. You can hover over any country to see its actual incident counts, financial impact, and resolution metrics. Adjust the sliders in the sidebar to calibrate the index!
            """)
        
    with right_col:
        st.subheader("Integrated Data Catalogs")
        
        # HTML styled dataset info cards
        st.markdown(
            f"""
            <div class="metric-card" style="padding: 18px;">
                <span class="indicator indicator-green"></span>
                <strong>Global Cybersecurity Threats (2015-2024)</strong>
                <p style="margin: 5px 0 0 18px; font-size: 0.9rem; color: #8c9ba5;">
                    Contains 3,000 incident reports across 10 countries and 7 industries. Includes defense indicators and financial loss metrics.
                </p>
            </div>
            <div class="metric-card" style="padding: 18px;">
                <span class="indicator indicator-green"></span>
                <strong>CFR Cyber Operations Incidents</strong>
                <p style="margin: 5px 0 0 18px; font-size: 0.9rem; color: #8c9ba5;">
                    Tracked geopolitical state-sponsored cyber incidents (2005-2020) including target sectors and attribution details.
                </p>
            </div>
            <div class="metric-card" style="padding: 18px;">
                <span class="indicator indicator-green"></span>
                <strong>Security Vulnerabilities (CVE)</strong>
                <p style="margin: 5px 0 0 18px; font-size: 0.9rem; color: #8c9ba5;">
                    Software security vulnerabilities categorized by severity, CVE numbers, and year of publication.
                </p>
            </div>
            <div class="metric-card" style="padding: 18px;">
                <span class="indicator indicator-green"></span>
                <strong>Network Intrusion Signatures</strong>
                <p style="margin: 5px 0 0 18px; font-size: 0.9rem; color: #8c9ba5;">
                    Live network traffic metrics (~5,000 records) including protocols, anomaly scores, packet sizes, and action actions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
