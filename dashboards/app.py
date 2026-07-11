"""
CyberVision - Streamlit Dashboard
An interactive visual analytics platform implementing the proposal's key tasks.

Usage:
    streamlit run dashboards/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import urllib.request
import sys

# Setup base paths relative to dashboards/app.py
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Import layout themes and visual network elements from frontend modules
from frontend.layout import COLOR_PALETTE, PLOTLY_THEME_LAYOUT
from frontend.components import render_threat_network

@st.cache_data
def load_world_geojson():
    url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None

# Setup page configuration
st.set_page_config(
    page_title="CyberVision | Threat Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for premium dark mode aesthetics
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        /* Font and Background styling */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00FFCC, #0099FF, #9900FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            letter-spacing: -0.05rem;
        }
        .main-subtitle {
            font-size: 1.1rem;
            color: #8A99AD;
            margin-bottom: 2rem;
            font-weight: 300;
        }
        
        /* Custom card styling */
        .metric-card {
            background-color: #111827;
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s, border-color 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #3B82F6;
        }
        .metric-val {
            font-size: 2.2rem;
            font-weight: 700;
            color: #F3F4F6;
            margin-top: 0.5rem;
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
        }
    </style>
""", unsafe_allow_html=True)

# Define data paths
ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# Cache loaded data for performance
@st.cache_data
def load_data():
    spatial_df = pd.read_csv(PROCESSED_DIR / "integrated_spatial.csv") if (PROCESSED_DIR / "integrated_spatial.csv").exists() else pd.DataFrame()
    temporal_df = pd.read_csv(PROCESSED_DIR / "integrated_temporal.csv") if (PROCESSED_DIR / "integrated_temporal.csv").exists() else pd.DataFrame()
    threats_df = pd.read_csv(PROCESSED_DIR / "global_threats_clean.csv") if (PROCESSED_DIR / "global_threats_clean.csv").exists() else pd.DataFrame()
    vulnerabilities_df = pd.read_csv(PROCESSED_DIR / "vulnerabilities_clean.csv") if (PROCESSED_DIR / "vulnerabilities_clean.csv").exists() else pd.DataFrame()
    malmem_df = pd.read_csv(PROCESSED_DIR / "malmem_clean.csv") if (PROCESSED_DIR / "malmem_clean.csv").exists() else pd.DataFrame()
    return spatial_df, temporal_df, threats_df, vulnerabilities_df, malmem_df

_, temporal_df, threats_df, vulnerabilities_df, malmem_df = load_data()

def get_spatial_dynamic(df, w_freq, w_loss, w_time):
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby("country")
    counts = grouped.size().reset_index(name="attack_count")
    
    # Financial loss
    loss_col = "financial_loss_in_million_"
    if loss_col in df.columns:
        losses = grouped[loss_col].mean().reset_index(name="avg_financial_loss")
        total_loss = grouped[loss_col].sum().reset_index(name="total_financial_loss")
        metrics = pd.merge(counts, losses, on="country")
        metrics = pd.merge(metrics, total_loss, on="country")
    else:
        metrics = counts
        metrics["avg_financial_loss"] = 0.0
        metrics["total_financial_loss"] = 0.0
        
    # Resolution time
    time_col = "incident_resolution_time_in_hours"
    if time_col in df.columns:
        times = grouped[time_col].mean().reset_index(name="avg_resolution_time")
        metrics = pd.merge(metrics, times, on="country")
    else:
        metrics["avg_resolution_time"] = 0.0
        
    def minmax(s):
        min_v = s.min()
        max_v = s.max()
        return (s - min_v) / (max_v - min_v) if max_v != min_v else pd.Series(0.5, index=s.index)
        
    n_count = minmax(metrics["attack_count"])
    n_loss = minmax(metrics["avg_financial_loss"])
    n_time = minmax(metrics["avg_resolution_time"])
    
    metrics["risk_score"] = (w_freq * n_count + w_loss * n_loss + w_time * n_time) * 100.0
    metrics["risk_score"] = metrics["risk_score"].round(1)
    
    # Round other columns
    metrics["total_financial_loss"] = metrics["total_financial_loss"].round(2)
    metrics["avg_financial_loss"] = metrics["avg_financial_loss"].round(2)
    metrics["avg_resolution_time"] = metrics["avg_resolution_time"].round(1)
    return metrics

# Header Section
st.markdown('<div class="main-title">🛡️ CyberVision</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Unified Cyber Threat Intelligence & Visual Analytics System</div>', unsafe_allow_html=True)

# Sidebar / Filters
st.sidebar.markdown("## Global Filters")
st.sidebar.subheader("⚙️ Risk Index Calibration")
w_freq_slider = st.sidebar.slider("Frequency Weight", 0.0, 1.0, 0.3, 0.05, help="Weights the threat occurrence count.")
w_loss_slider = st.sidebar.slider("Financial Impact Weight", 0.0, 1.0, 0.4, 0.05, help="Weights average financial loss ($M).")
w_time_slider = st.sidebar.slider("Resolution Time Weight", 0.0, 1.0, 0.3, 0.05, help="Weights average incident resolution hours.")

total_w = w_freq_slider + w_loss_slider + w_time_slider
if total_w > 0:
    w_freq = w_freq_slider / total_w
    w_loss = w_loss_slider / total_w
    w_time = w_time_slider / total_w
else:
    w_freq, w_loss, w_time = 0.3, 0.4, 0.3

spatial_df = get_spatial_dynamic(threats_df, w_freq, w_loss, w_time)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Datasets")
st.sidebar.download_button(
    label="Download Spatial Risk Data (CSV)",
    data=spatial_df.to_csv(index=False),
    file_name="integrated_spatial.csv",
    mime="text/csv",
    help="Export geographic risk index and averages."
)
st.sidebar.download_button(
    label="Download Temporal Trends Data (CSV)",
    data=temporal_df.to_csv(index=False),
    file_name="integrated_temporal.csv",
    mime="text/csv",
    help="Export chronological timeline details."
)

if not threats_df.empty:
    selected_countries = st.sidebar.multiselect(
        "Filter by Country",
        options=sorted(threats_df["country"].unique()),
        default=[]
    )
else:
    selected_countries = []

# Apply filters to threats_df
filtered_threats_df = threats_df.copy()
if selected_countries:
    filtered_threats_df = filtered_threats_df[filtered_threats_df["country"].isin(selected_countries)]

# Top summary KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_incidents = len(filtered_threats_df) if not filtered_threats_df.empty else 0
total_loss = filtered_threats_df["financial_loss_in_million_"].sum() if not filtered_threats_df.empty else 0
total_users = filtered_threats_df["number_of_affected_users"].sum() if not filtered_threats_df.empty else 0
avg_resolution = filtered_threats_df["incident_resolution_time_in_hours"].mean() if not filtered_threats_df.empty else 0

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Global Incidents</div>
        <div class="metric-val">{total_incidents:,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Estimated Loss (M USD)</div>
        <div class="metric-val">${total_loss:,.1f}M</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Users Impacted</div>
        <div class="metric-val">{total_users:,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Resolution Time</div>
        <div class="metric-val">{avg_resolution:.1f} hrs</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs Navigation
tab_map, tab_trends, tab_industry, tab_vuln, tab_malware, tab_network = st.tabs([
    "🗺️ Country Threat Map", 
    "📈 Global Trend Analysis", 
    "🏢 Industry Risk Dashboard",
    "🛡️ Vulnerability Explorer",
    "🦠 Malware Family Analytics",
    "🕸️ Threat Relationship Network"
])

# ----------------- Tab 1: Country Threat Map (Task 4.2) -----------------
with tab_map:
    st.header("Global Cyber Risk Mapping")
    
    if not spatial_df.empty:
        iso_alpha = {
            "Australia": "AUS", "Brazil": "BRA", "China": "CHN", "France": "FRA",
            "Germany": "DEU", "India": "IND", "Japan": "JPN", "Russia": "RUS",
            "United Kingdom": "GBR", "United States": "USA", "Canada": "CAN", "Iran": "IRN",
            "North Korea": "PRK", "Syria": "SYR", "Uk": "GBR", "Usa": "USA"
        }
        spatial_df["iso_code"] = spatial_df["country"].map(iso_alpha)
        
        geojson_data = load_world_geojson()
        
        if geojson_data:
            fig_map = px.choropleth(
                spatial_df,
                geojson=geojson_data,
                locations="iso_code",
                featureidkey="properties.ISO3166-1-Alpha-3",
                color="risk_score",
                hover_name="country",
                hover_data={
                    "risk_score": True,
                    "attack_count": True,
                    "total_financial_loss": True,
                    "avg_resolution_time": True
                },
                color_continuous_scale=px.colors.sequential.Sunsetdark,
                title="Interactive Global Cyber Risk Map (Normalized 0-100 Score)"
            )
        else:
            fig_map = px.choropleth(
                spatial_df,
                locations="country",
                locationmode="country names",
                color="risk_score",
                hover_name="country",
                hover_data={
                    "risk_score": True,
                    "attack_count": True,
                    "total_financial_loss": True,
                    "avg_resolution_time": True
                },
                color_continuous_scale=px.colors.sequential.Sunsetdark,
                title="Interactive Global Cyber Risk Map (Normalized 0-100 Score)"
            )
            
        fig_map.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_colorbar=dict(title="Risk Score")
        )
        st.plotly_chart(fig_map, use_container_width=True)

        with st.expander("💡 Global Security Risk Map Insights"):
            st.markdown(f"""
            *   **Dynamic Calibration:** The risk leaderboard is recalculated in real-time based on the sidebar weights (Incident Frequency: {w_freq:.0%}, Financial Impact: {w_loss:.0%}, Operational Resolution: {w_time:.0%}).
            *   **Geopolitics & Hotspots:** Industrial hubs like the USA, Germany, and Australia show elevated risk indexes due to higher incident reporting frequencies and significant economic damage per breach.
            *   **Boundary & Mapping Note:** Geopolitical boundaries (including the complete boundaries of India incorporating Jammu & Kashmir) are mapped using standardized international high-resolution GeoJSON geometries to ensure correct territorial representation.
            """)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top High-Risk Countries")
            top_countries = spatial_df.sort_values("risk_score", ascending=False).head(10)
            fig_rank = px.bar(
                top_countries,
                x="risk_score",
                y="country",
                orientation='h',
                color="risk_score",
                color_continuous_scale=px.colors.sequential.Sunsetdark,
                labels={"risk_score": "Risk Score", "country": "Country"}
            )
            fig_rank.update_layout(**PLOTLY_THEME_LAYOUT, yaxis={'categoryorder':'total ascending'}, showlegend=False, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_rank, use_container_width=True)
            
        with col2:
            st.subheader("Risk Data Registry")
            st.dataframe(
                spatial_df.sort_values("risk_score", ascending=False),
                column_config={
                    "country": "Country",
                    "attack_count": "Incidents",
                    "total_financial_loss": "Total Loss (M)",
                    "avg_financial_loss": "Avg Loss (M)",
                    "avg_resolution_time": "Avg Resolution (hrs)",
                    "risk_score": "Risk Score"
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.warning("Spatial integrated data is missing.")

# ----------------- Tab 2: Global Trend Analysis (Task 4.1 & 4.6) -----------------
with tab_trends:
    st.header("Global Threat & Incident Evolution")

    if not temporal_df.empty:
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.subheader("Annual Cyber Incidents Trends")
            # Line chart showing CFR vs Global threats
            fig_trends = go.Figure()
            fig_trends.add_trace(go.Scatter(
                x=temporal_df["year"], y=temporal_df["global_incidents"],
                mode='lines+markers', name='Global Threats (2015-2024)',
                line=dict(color='#00FFCC', width=3)
            ))
            fig_trends.add_trace(go.Scatter(
                x=temporal_df["year"], y=temporal_df["cfr_incidents"],
                mode='lines+markers', name='CFR Historical (2005-2020)',
                line=dict(color='#FF8F00', width=2, dash='dash')
            ))
            
            # Predictive threat forecasting (Task 4.1 prediction extension)
            import numpy as np
            years = temporal_df["year"].values
            global_incidents = temporal_df["global_incidents"].values
            valid_mask = (years >= 2015) & (years <= 2023) & (global_incidents > 0)
            X = years[valid_mask]
            y = global_incidents[valid_mask]
            
            if len(X) > 2:
                poly = np.polyfit(X, y, 1)
                forecast_years = np.array([2023, 2024, 2025, 2026])
                forecast_values = np.polyval(poly, forecast_years)
                forecast_values = np.clip(forecast_values, 0, None)
                
                fig_trends.add_trace(go.Scatter(
                    x=forecast_years, y=forecast_values,
                    mode='lines+markers', name='Linear Forecast (2023-2026)',
                    line=dict(color='#FF00FF', width=2, dash='dot')
                ))
                
            fig_trends.update_layout(
                **PLOTLY_THEME_LAYOUT,
                xaxis_title="Year", 
                yaxis_title="Incident Count",
                margin={"t": 30, "b": 30, "l": 30, "r": 30},
                height=350
            )
            st.plotly_chart(fig_trends, use_container_width=True)

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

        st.markdown("---")
        st.subheader("Incident Resolution vs. Severity Analysis")
        
        if not filtered_threats_df.empty:
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                # Scatter plot of Resolution Time vs Severity
                fig_scatter = px.box(
                    filtered_threats_df,
                    x="defense_mechanism_used" if "defense_mechanism_used" in filtered_threats_df.columns else None,
                    y="incident_resolution_time_in_hours",
                    color="attack_type",
                    points="all",
                    labels={
                        "defense_mechanism_used": "Defense Mechanism",
                        "incident_resolution_time_in_hours": "Resolution Time (Hours)",
                        "attack_type": "Attack Type"
                    },
                    title="Resolution Efficiency by Defense Strategy and Threat Vector"
                )
                fig_scatter.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
                st.plotly_chart(fig_scatter, use_container_width=True)
            with col_s2:
                # Attack Source Breakdown
                st.subheader("Attack Source Attribution")
                source_counts = filtered_threats_df["attack_source"].value_counts().reset_index()
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
        st.warning("Temporal integrated data is missing.")

# ----------------- Tab 3: Industry Risk Dashboard (Task 4.3) -----------------
with tab_industry:
    st.header("Industry Vulnerability & Risk Profiles")

    if not filtered_threats_df.empty:
        col_ind1, col_ind2 = st.columns(2)

        with col_ind1:
            st.subheader("Financial Loss Distribution by Sector")
            fig_tree = px.treemap(
                filtered_threats_df,
                path=["target_industry", "attack_type"],
                values="financial_loss_in_million_",
                color="financial_loss_in_million_",
                color_continuous_scale=[
                    [0.0, "rgba(17, 25, 40, 0.6)"],
                    [0.5, "rgba(79, 172, 254, 0.8)"],
                    [1.0, COLOR_PALETTE["primary"]]
                ],
                labels={"financial_loss_in_million_": "Loss (M USD)"}
            )
            fig_tree.update_layout(**PLOTLY_THEME_LAYOUT)
            st.plotly_chart(fig_tree, use_container_width=True)

        with col_ind2:
            st.subheader("Industry Severity Profile")
            fig_ind_bar = px.histogram(
                filtered_threats_df,
                x="target_industry",
                color="attack_type",
                barmode="stack",
                labels={"target_industry": "Industry Sector", "count": "Incidents"},
                color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"], COLOR_PALETTE["neon_pink"]]
            )
            fig_ind_bar.update_layout(**PLOTLY_THEME_LAYOUT)
            st.plotly_chart(fig_ind_bar, use_container_width=True)
            
        with st.expander("💡 Sector Risk & Loss Insights"):
            st.markdown(f"""
            *   **Treemap Hierarchy:** The size of each sector represents the **Total Financial Loss ($M)** incurred, while the color shade represents the **Average Loss per Incident**.
            *   **Critical Sectors:** Sectors like Healthcare and Finance typically show large dimensions due to substantial breach response costs (e.g. data restoration and regulatory penalties).
            *   **Weight Calibrator:** Changing your sidebar weights (Frequency: {w_freq:.0%}, Loss: {w_loss:.0%}, Operational: {w_time:.0%}) shifts the Risk Index values in the leaderboard in real-time.
            """)
    else:
        st.warning("Global threats dataset is missing.")

# ----------------- Tab 4: Vulnerability Explorer (Task 4.4) -----------------
with tab_vuln:
    st.header("Software & CVE Vulnerability Analysis")

    if not vulnerabilities_df.empty:
        v_col1, v_col2 = st.columns([1, 2])

        with v_col1:
            st.subheader("Severity Breakdown")
            sev_counts = vulnerabilities_df["severity"].value_counts().reset_index()
            fig_sev = px.pie(
                sev_counts,
                names="severity",
                values="count",
                color="severity",
                color_discrete_map={"Critical": "#EF4444", "High": "#F97316", "Medium": "#EAB308", "Low": "#10B981", "Unrated": "#6B7280"},
                hole=0.4
            )
            fig_sev.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_sev, use_container_width=True)

        with v_col2:
            st.subheader("Vulnerability Disclosures Trend")
            if "year" in vulnerabilities_df.columns:
                vuln_year = vulnerabilities_df.groupby("year").size().reset_index(name="count")
                fig_v_trend = px.line(
                    vuln_year,
                    x="year",
                    y="count",
                    markers=True,
                    labels={"count": "CVE Disclosures", "year": "Year"},
                    color_discrete_sequence=[COLOR_PALETTE["neon_pink"]]
                )
                fig_v_trend.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
                st.plotly_chart(fig_v_trend, use_container_width=True)

        with st.expander("💡 Vulnerability Density Insights"):
            st.markdown(f"""
            *   **Distribution Matrix:** Highlights the volume of software vulnerabilities published per year categorized by severity. Notice the proportion of Critical and High vulnerabilities.
            *   **Registry Search:** Use the Keyword Search below to filter specific CVE titles or summaries dynamically.
            """)

        st.subheader("Vulnerabilities Search Registry")
        search_q = st.text_input("Search vulnerabilities (title or summary)", placeholder="e.g. Remote Code Execution")
        
        display_vuln = vulnerabilities_df.copy()
        if search_q:
            display_vuln = display_vuln[
                display_vuln["title"].str.contains(search_q, case=False, na=False) |
                display_vuln["summary"].str.contains(search_q, case=False, na=False)
            ]
        
        st.dataframe(
            display_vuln[["title", "severity", "date", "summary"]],
            column_config={
                "title": "Advisory Title",
                "severity": "Severity",
                "date": "Publish Date",
                "summary": "Technical Summary"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Vulnerability dataset is missing.")

# ----------------- Tab 5: Malware Family Analytics (Task 4.5) -----------------
with tab_malware:
    st.header("Malware Memory Forensics (CIC-MalMem-2022)")

    if not malmem_df.empty:
        m_col1, m_col2 = st.columns(2)

        with m_col1:
            st.subheader("Dataset Class Balance (Benign vs. Malicious)")
            
            # Map categories to Malicious vs Benign
            malmem_df["class"] = malmem_df["category"].apply(lambda x: "Benign" if x == "Benign" else "Malicious")
            class_counts = malmem_df["class"].value_counts().reset_index()
            
            fig_class = px.pie(
                class_counts,
                names="class",
                values="count",
                color="class",
                color_discrete_map={"Benign": COLOR_PALETTE["neon_green"], "Malicious": COLOR_PALETTE["neon_pink"]},
                hole=0.4
            )
            fig_class.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_class, use_container_width=True)

        with m_col2:
            st.subheader("Malicious Category Distribution")
            malicious_df = malmem_df[malmem_df["category"] != "Benign"]
            cat_counts = malicious_df["category"].value_counts().reset_index()
            
            fig_cat = px.bar(
                cat_counts,
                x="count",
                y="category",
                orientation='h',
                color="category",
                color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"]]
            )
            fig_cat.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 30, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_cat, use_container_width=True)

        st.subheader("Specific Malware Family Breakdown")
        family_counts = malicious_df["family"].value_counts().reset_index()
        fig_fam = px.bar(
            family_counts,
            x="family",
            y="count",
            color="family",
            color_discrete_sequence=[COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"], COLOR_PALETTE["neon_green"]]
        )
        fig_fam.update_layout(**PLOTLY_THEME_LAYOUT, height=400, margin={"t": 30, "b": 30, "l": 30, "r": 30})
        st.plotly_chart(fig_fam, use_container_width=True)

        with st.expander("💡 Malware Forensics Analysis Insights"):
            st.markdown(f"""
            *   **Class Balance:** The pie chart represents the ratio of Benign (normal memory signatures) to Malicious samples loaded in the forensics model.
            *   **Category Analysis:** Identifies memory evasion families (Trojans, Spyware, Ransomware) showing their prevalence in infected operating systems.
            *   **Family breakdown:** Highlights specific threat variants (e.g. Zeus, Shade, Conti) targeted during binary payload analysis.
            """)
    else:
        st.warning("Malware memory dataset is missing.")

# ----------------- Tab 6: Threat Relationship Network (Task 4.7) -----------------
with tab_network:
    st.header("Threat Actor & Sector Relationship Network")
    st.markdown("""
    This topological network represents relationships between **Threat Actors**, **Source Nations**, and **Targeted Industry Sectors**.
    It illustrates how national state-sponsored groups prioritize specific corporate and infrastructure targets.
    """)

    if not threats_df.empty:
        fig_net = render_threat_network(threats_df)
        st.plotly_chart(fig_net, use_container_width=True)
        
        with st.expander("💡 Network Topology Insights"):
            st.markdown("""
            *   **Node Colors:** **Cyan nodes** represent source nations/threat groups, **magenta nodes** represent industry targets, and **yellow nodes** represent attack tactics.
            *   **Edge Thickness:** Thicker connections indicate a higher volume of recorded attacks linking that actor/nation to that targeted sector.
            *   **Defensive Strategy:** Highly connected nodes represent critical hubs where joint security monitoring and perimeter firewalls should be prioritized.
            """)
    else:
        st.warning("Global threats dataset is missing to build network graph.")
