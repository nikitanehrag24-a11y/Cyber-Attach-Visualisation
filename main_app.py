"""
CyberVision Dashboard Main Orchestrator.
Manages global state, sidebar filter inputs, data loader/filter pipelines,
and handles page routing based on sidebar navigation selection.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from frontend.layout import set_page_theme, inject_custom_css
from frontend.sidebar import render_sidebar
from backend.loader import load_all_datasets
from backend.integration import (
    get_integrated_global_threats,
    get_integrated_cfr_incidents,
    get_integrated_attack_signatures
)
from backend.filters import (
    filter_global_threats,
    filter_cfr_incidents,
    filter_vulnerabilities,
    filter_attack_signatures,
    filter_malmem
)
from backend.risk import get_country_risk_scores
from backend.analytics import get_kpis
from frontend.components import card_kpi

# Import page modules dynamically
import pages.Global_Threats as Global_Threats
import pages.Country_Map as Country_Map
import pages.Industry as Industry
import pages.Vulnerability as Vulnerability
import pages.Attack_Source as Attack_Source
import pages.Network as Network
import pages.Malware_Analytics as Malware_Analytics

def main():
    # 1. Setup Theme Configurations
    set_page_theme()
    inject_custom_css()
    
    # 2. Load Raw Datasets
    with st.spinner("Initializing Cyber Threat Intelligence Datasets..."):
        datasets = load_all_datasets()
        
    # 3. Integrate / Align Schemas
    global_threats_aligned = get_integrated_global_threats(datasets["global_threats"])
    cfr_aligned = get_integrated_cfr_incidents(datasets["cfr_incidents"])
    attack_sigs_aligned = get_integrated_attack_signatures(datasets["attack_signatures"])
    vulnerabilities = datasets["vulnerabilities"]
    malmem = datasets["malmem"]
    
    # 4. Extract Filter Values dynamically
    countries = sorted(list(set(
        global_threats_aligned["standard_country"].dropna().tolist() +
        cfr_aligned["standard_country"].dropna().tolist() +
        attack_sigs_aligned["standard_country"].dropna().tolist()
    )))
    
    attack_types = sorted(list(set(
        global_threats_aligned["standard_attack_type"].dropna().tolist() +
        cfr_aligned["standard_attack_type"].dropna().tolist() +
        attack_sigs_aligned["standard_attack_type"].dropna().tolist()
    )))
    
    industries = sorted(list(global_threats_aligned["target_industry"].dropna().unique()))
    severities = ["Low", "Moderate", "High", "Critical"]
    
    # 5. Render Sidebar Filters
    filters = render_sidebar(countries, attack_types, industries, severities)
    
    # 6. Apply Filter Values to Dataframes
    filtered_global_threats = filter_global_threats(
        global_threats_aligned,
        filters["countries"],
        filters["years"],
        filters["attack_types"],
        filters["industries"]
    )
    
    filtered_cfr = filter_cfr_incidents(
        cfr_aligned,
        filters["countries"],
        filters["years"],
        filters["attack_types"],
        filters["search_query"]
    )
    
    filtered_vuln = filter_vulnerabilities(
        vulnerabilities,
        filters["years"],
        filters["severities"],
        filters["search_query"]
    )
    
    filtered_sigs = filter_attack_signatures(
        attack_sigs_aligned,
        filters["countries"],
        filters["years"],
        filters["attack_types"],
        filters["severities"]
    )
    
    filtered_malmem = filter_malmem(malmem, filters["search_query"])
    
    # Pack filtered dataframes into a payload dict
    filtered_data = {
        "global_threats": filtered_global_threats,
        "cfr_incidents": filtered_cfr,
        "vulnerabilities": filtered_vuln,
        "attack_signatures": filtered_sigs,
        "malmem": filtered_malmem,
        "raw_global_threats": global_threats_aligned,  # Unfiltered reference for risk scoring baseline
        "integrated_temporal": datasets["integrated_temporal"]
    }
    
    # 7. Render Export CSV and GitHub Dataset Registry widgets in Sidebar
    w_freq, w_loss, w_time = filters.get("weights", (0.3, 0.4, 0.3))
    risk_df = get_country_risk_scores(filtered_global_threats, w_freq, w_loss, w_time)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export Datasets")
    st.sidebar.download_button(
        label="Download Spatial Risk Data (CSV)",
        data=risk_df.to_csv(index=False),
        file_name="integrated_spatial.csv",
        mime="text/csv",
        help="Export geographic risk index and averages."
    )
    st.sidebar.download_button(
        label="Download Temporal Trends Data (CSV)",
        data=datasets["integrated_temporal"].to_csv(index=False),
        file_name="integrated_temporal.csv",
        mime="text/csv",
        help="Export chronological timeline details."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("GitHub Dataset Registry")
    st.sidebar.markdown(f"""
    *   **Global Threat Logs:** `{len(datasets["global_threats"]):,} rows`
    *   **CFR Incidents Catalog:** `{len(datasets["cfr_incidents"]):,} rows`
    *   **Vulnerability Registry:** `{len(datasets["vulnerabilities"]):,} rows`
    *   **Malware Forensic Dumps:** `{len(datasets["malmem"]):,} rows`
    """)
    
    # 8. Render Global KPI Summary Cards at the top of every view (page-independent)
    st.markdown("<h1>CyberVision Command Center</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Unified Cybersecurity Threat Operations and Intel Analytics Platform."
        "</p>",
        unsafe_allow_html=True
    )
    
    kpis = get_kpis(filtered_global_threats, filtered_cfr, filtered_vuln)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card_kpi("Total Global Incidents", f"{kpis['total_attacks']:,}", icon="🚨")
    with col2:
        card_kpi("Estimated Loss in USD", f"${kpis['total_loss_million']:,.1f}M", icon="💰")
    with col3:
        card_kpi("Average Resolution Time", f"{kpis['avg_resolution_hours']:.1f} hrs", icon="⏱️")
    with col4:
        card_kpi("Users Impacted", f"{kpis['affected_users']:,}", icon="👥")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 9. Tab-Based Navigation: switches between the 7 analytical views
    tab_map, tab_trends, tab_industry, tab_vuln, tab_malware, tab_resolution, tab_network = st.tabs([
        "Country Threat Map", 
        "Global Threat Trends", 
        "Industry Risk Dashboard",
        "Vulnerability Explorer",
        "Malware Family Analytics",
        "Attack Source & Resolution",
        "Threat Relationship Network"
    ])
    
    with tab_map:
        Country_Map.render(filtered_data, filters)
    with tab_trends:
        Global_Threats.render(filtered_data, filters)
    with tab_industry:
        Industry.render(filtered_data, filters)
    with tab_vuln:
        Vulnerability.render(filtered_data, filters)
    with tab_malware:
        Malware_Analytics.render(filtered_data, filters)
    with tab_resolution:
        Attack_Source.render(filtered_data, filters)
    with tab_network:
        Network.render(filtered_data, filters)

if __name__ == "__main__":
    main()
