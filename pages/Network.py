"""
Network page component.
Renders the interactive NetworkX threat actor relationship graph.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from frontend.components import render_threat_network

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the threat actor relationship network page."""
    st.markdown("<h1>Geopolitical Relationship Network</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Map relational connections between threat actors, target industries, and geographic destinations."
        "</p>",
        unsafe_allow_html=True
    )
    
    global_df = datasets["global_threats"]
    
    if global_df.empty:
        st.warning("No data matches the selected filters. Please adjust the sidebar choices to populate the network.")
        return
        
    # 1. Render Network Graph
    fig_network = render_threat_network(global_df)
    st.plotly_chart(fig_network, use_container_width=True)
    
    # 2. Information Card on Graph Mechanics
    st.subheader("Network Node & Edge Key")
    st.markdown(
        """
        <div class="metric-card">
            <h4 style="margin-top:0;">Graph Semantics</h4>
            <p>This network maps associations between entities extracted from recorded attack alerts:</p>
            <ul>
                <li><span style="color:#ff0055; font-weight:bold;">● Neon Pink Nodes:</span> Represents the <strong>Threat Source</strong> (e.g. Nation-State, Insider, Hacker Group).</li>
                <li><span style="color:#00f2fe; font-weight:bold;">● Neon Blue Nodes:</span> Represents the <strong>Country</strong> target location.</li>
                <li><span style="color:#00ff87; font-weight:bold;">● Neon Green Nodes:</span> Represents the affected <strong>Target Industry</strong>.</li>
                <li><strong>Edge Connections:</strong> Represents documented attack trails. Double-click or scroll on the graph to zoom and hover over nodes to view connection indices in real-time.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Reference Report Plot
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Show Static Reference Report Plot"):
        st.image("images/threat_network.png", caption="Figure 4.7: Threat actor relationship network mapping connections between threat vectors and sectors", use_container_width=True)
