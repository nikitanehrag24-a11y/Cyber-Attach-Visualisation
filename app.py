"""
CyberVision Dashboard Main Orchestrator.
Manages global state, sidebar filter inputs, data loader/filter pipelines,
and handles page routing based on sidebar navigation selection.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve()))

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

# Import page modules dynamically
import pages.Home as Home
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
    severities = ["Low", "Medium", "High", "Critical"]
    
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
    
    filtered_malmem = malmem
    
    # Pack filtered dataframes into a payload dict
    filtered_data = {
        "global_threats": filtered_global_threats,
        "cfr_incidents": filtered_cfr,
        "vulnerabilities": filtered_vuln,
        "attack_signatures": filtered_sigs,
        "malmem": filtered_malmem,
        "raw_global_threats": global_threats_aligned  # Unfiltered reference for risk scoring baseline
    }
    
    # 7. Page Routing
    current_page = st.session_state.get("current_page", "Home")
    
    if current_page == "Home":
        Home.render(filtered_data, filters)
    elif current_page == "Global_Threats":
        Global_Threats.render(filtered_data, filters)
    elif current_page == "Country_Map":
        Country_Map.render(filtered_data, filters)
    elif current_page == "Industry":
        Industry.render(filtered_data, filters)
    elif current_page == "Vulnerability":
        Vulnerability.render(filtered_data, filters)
    elif current_page == "Attack_Source":
        Attack_Source.render(filtered_data, filters)
    elif current_page == "Network":
        Network.render(filtered_data, filters)
    elif current_page == "Malware_Analytics":
        Malware_Analytics.render(filtered_data, filters)

if __name__ == "__main__":
    main()
