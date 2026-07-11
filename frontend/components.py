"""
Defines reusable frontend components, metrics cards, and Plotly visualization builders.
Includes line trends, choropleths, treemaps, heatmaps, scatter plots, and network graphs.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import networkx as nx
import json
import urllib.request
from typing import Dict, Any, List

from frontend.layout import COLOR_PALETTE, PLOTLY_THEME_LAYOUT

@st.cache_data
def load_world_geojson():
    url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None

def card_kpi(label: str, value: str, icon: str = "⚡"):
    """Renders a single glassmorphic card with a KPI metric."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_global_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Generates an interactive line/area chart showing attacks over the years."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data matching filters.", showarrow=False)
        return fig
        
    yearly = df.groupby("year").size().reset_index(name="Attack Count")
    
    fig = px.area(
        yearly,
        x="year",
        y="Attack Count",
        labels={"year": "Year", "Attack Count": "Number of Attacks"},
        color_discrete_sequence=[COLOR_PALETTE["primary"]]
    )
    
    fig.update_layout(
        **PLOTLY_THEME_LAYOUT,
        margin={"t": 30, "b": 30, "l": 30, "r": 30},
        height=400,
        title="Global Attack Volume Trend (2015-2024)"
    )
    fig.update_traces(
        line=dict(width=3, color=COLOR_PALETTE["primary"]),
        fillcolor="rgba(0, 242, 254, 0.15)"
    )
    return fig

def render_risk_choropleth(country_risk_df: pd.DataFrame) -> go.Figure:
    """Generates a world choropleth map colored by Country Risk Score."""
    if country_risk_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No country risk data available.", showarrow=False)
        return fig
        
    # Map country names to ISO-3 codes for standard map loading
    iso_alpha = {
        "Usa": "USA", "Uk": "GBR", "China": "CHN", "Russia": "RUS", "India": "IND",
        "Germany": "DEU", "Japan": "JPN", "France": "FRA", "Australia": "AUS", "Brazil": "BRA",
        "Iran": "IRN", "North Korea": "PRK", "Syria": "SYR", "Canada": "CAN"
    }
    
    df_map = country_risk_df.copy()
    df_map["iso_code"] = df_map["standard_country"].map(iso_alpha)
    
    geojson_data = load_world_geojson()
    
    if geojson_data:
        fig = px.choropleth(
            df_map,
            geojson=geojson_data,
            locations="iso_code",
            featureidkey="properties.ISO3166-1-Alpha-3",
            color="risk_score",
            hover_name="standard_country",
            hover_data={"incident_count": True, "avg_loss": ":.2f", "avg_resolution_time": ":.1f", "risk_score": ":.2f"},
            color_continuous_scale=[
                [0.0, "rgba(0, 242, 254, 0.2)"],
                [0.5, "rgba(79, 172, 254, 0.6)"],
                [0.8, "rgba(127, 0, 255, 0.85)"],
                [1.0, COLOR_PALETTE["neon_pink"]]
            ],
            labels={"risk_score": "Risk Index"},
            title="Global Security Risk Map (Scale 0-10)"
        )
    else:
        fig = px.choropleth(
            df_map,
            locations="iso_code",
            color="risk_score",
            hover_name="standard_country",
            hover_data={"incident_count": True, "avg_loss": ":.2f", "avg_resolution_time": ":.1f", "risk_score": ":.2f"},
            color_continuous_scale=[
                [0.0, "rgba(0, 242, 254, 0.2)"],
                [0.5, "rgba(79, 172, 254, 0.6)"],
                [0.8, "rgba(127, 0, 255, 0.85)"],
                [1.0, COLOR_PALETTE["neon_pink"]]
            ],
            labels={"risk_score": "Risk Index"},
            title="Global Security Risk Map (Scale 0-10)"
        )
    
    fig.update_layout(
        **PLOTLY_THEME_LAYOUT,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            landcolor="#0e1420",
            lakecolor="#06090e"
        ),
        margin={"t": 40, "b": 10, "l": 10, "r": 10},
        height=500
    )
    return fig

def render_industry_treemap(industry_df: pd.DataFrame) -> go.Figure:
    """Generates an interactive Treemap representing financial losses across industries."""
    if industry_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No industry statistics available.", showarrow=False)
        return fig
        
    fig = px.treemap(
        industry_df,
        path=["target_industry"],
        values="total_loss",
        color="avg_loss",
        color_continuous_scale=[[0.0, "rgba(17, 25, 40, 0.6)"], [1.0, COLOR_PALETTE["primary"]]],
        labels={"total_loss": "Total Loss ($M)", "avg_loss": "Avg Loss ($M)"},
        title="Industry Impact Profile (Size = Total Loss, Color = Avg Loss)"
    )
    
    fig.update_layout(
        **PLOTLY_THEME_LAYOUT,
        margin={"t": 40, "b": 10, "l": 10, "r": 10},
        height=450
    )
    return fig
 
def render_vulnerability_heatmap(vuln_df: pd.DataFrame) -> go.Figure:
    """Generates an interactive Heatmap showing Severity trends over years."""
    if vuln_df.empty or "severity" not in vuln_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No vulnerability data available.", showarrow=False)
        return fig
        
    pivot_df = vuln_df.groupby(["year", "severity"]).size().unstack(fill_value=0)
    
    # Ensure correct ordering of severities
    ordered_cols = [c for c in ["Low", "Medium", "High", "Critical"] if c in pivot_df.columns]
    pivot_df = pivot_df[ordered_cols]
    
    fig = px.imshow(
        pivot_df.T,
        labels=dict(x="Year", y="Severity", color="CVE Count"),
        color_continuous_scale=[[0.0, "rgba(17, 25, 40, 0.6)"], [1.0, COLOR_PALETTE["accent"]]],
        title="Vulnerability Severity Density Matrix"
    )
    
    fig.update_layout(
        **PLOTLY_THEME_LAYOUT,
        margin={"t": 40, "b": 30, "l": 30, "r": 30},
        height=400
    )
    return fig

def render_attack_source_scatter(df: pd.DataFrame) -> go.Figure:
    """Generates a scatter plot comparing packet lengths, anomaly scores, and resolution time."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No attack signature logs available.", showarrow=False)
        return fig
        
    fig = px.scatter(
        df.head(1000),  # Limit to 1000 items to guarantee smooth performance
        x="anomaly_scores",
        y="packet_length",
        color="severity_level",
        size="source_port",  # Using source port size dynamically
        hover_data=["protocol", "action_taken", "standard_country"],
        color_discrete_sequence=[COLOR_PALETTE["neon_green"], COLOR_PALETTE["secondary"], COLOR_PALETTE["accent"], COLOR_PALETTE["neon_pink"]],
        title="Intrusion Signatures: Anomaly Level vs. Packet Length"
    )
    
    fig.update_layout(
        **PLOTLY_THEME_LAYOUT,
        margin={"t": 40, "b": 30, "l": 30, "r": 30},
        height=450
    )
    return fig

def render_threat_network(global_threats_df: pd.DataFrame) -> go.Figure:
    """
    Builds a NetworkX graph connecting Threat Sources, Countries, and Industries,
    and returns a Plotly scatter line figure representing the relationship network.
    """
    if global_threats_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No threat network data available.", showarrow=False)
        return fig
        
    G = nx.Graph()
    
    # Select top rows to avoid cluttering the visual
    sample_df = global_threats_df.head(150)
    
    # 1. Add nodes and edges
    for _, row in sample_df.iterrows():
        row_dict = row.to_dict()
        actor = row_dict.get("attack_source", "Unknown")
        country = row_dict.get("standard_country", row_dict.get("country", "Unknown"))
        industry = row_dict.get("target_industry", "Unknown")
        
        # Color coding designations
        G.add_node(actor, type="Actor", color=COLOR_PALETTE["neon_pink"])
        G.add_node(country, type="Country", color=COLOR_PALETTE["primary"])
        G.add_node(industry, type="Industry", color=COLOR_PALETTE["neon_green"])
        
        G.add_edge(actor, country)
        G.add_edge(country, industry)
        
    # 2. Get Node Positions
    pos = nx.spring_layout(G, seed=42, k=0.35)
    
    # 3. Create Edge Traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="rgba(255, 255, 255, 0.15)"),
        hoverinfo="none",
        mode="lines"
    )
    
    # 4. Create Node Traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_type = G.nodes[node]["type"]
        degree = G.degree(node)
        node_text.append(f"<b>{node}</b><br>Type: {node_type}<br>Connections: {degree}")
        node_colors.append(G.nodes[node]["color"])
        
        # Scale size dynamically based on connection degree
        node_sizes.append(15 + degree * 2)
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[n if G.degree(n) > 2 else "" for n in G.nodes()],  # Only show names for highly connected nodes
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line=dict(width=1.5, color=COLOR_PALETTE["card"])
        )
    )
    
    # 5. Build Figure safely without parameter collisions
    layout_args = {
        "title": "Interactive Threat Actor Relationship Network",
        "showlegend": False,
        "hovermode": "closest",
        "margin": dict(b=20, l=5, r=5, t=40),
        "xaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
        "yaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
        "height": 550
    }
    for k, v in PLOTLY_THEME_LAYOUT.items():
        if k not in ["xaxis", "yaxis"]:
            layout_args[k] = v

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(**layout_args)
    )
    return fig
