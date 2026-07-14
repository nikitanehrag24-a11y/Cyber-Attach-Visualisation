"""
Handles the sidebar UI component, including dataset filter controls
(Country, Year range, Attack Type, Industry, Severity) and page navigation.
"""

import streamlit as st
from typing import Dict, Any, List

def render_sidebar(
    available_countries: List[str],
    available_attack_types: List[str],
    available_industries: List[str],
    available_severities: List[str]
) -> Dict[str, Any]:
    """
    Renders the sidebar navigation and filter widgets.
    Returns a dictionary of selected filter options.
    """
    st.sidebar.markdown(
        "<h2 style='text-align: center; margin-bottom: 20px;'>CyberVision</h2>",
        unsafe_allow_html=True
    )
    
    # 1. Navigation Panel
    st.sidebar.subheader("Navigation")
    pages = {
        "Home": "Dashboard Home",
        "Global_Threats": "Global Threat Trends",
        "Country_Map": "Global Security Risk Map",
        "Industry": "Industry Impact Profile",
        "Vulnerability": "Vulnerability Severity Distribution",
        "Malware_Analytics": "Malware Family Analytics",
        "Attack_Source": "Threat Attribution & Resolution",
        "Network": "Geopolitical Relationship Network"
    }
    
    # We can use query parameters or session state to handle navigation in a single-app routing setup
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"
        
    selected_page_label = st.sidebar.radio(
        label="Select Page View",
        options=list(pages.values()),
        label_visibility="collapsed"
    )
    
    # Find key of selected page
    for k, v in pages.items():
        if v == selected_page_label:
            st.session_state["current_page"] = k
            break
            
    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")
    
    # 2. Country Selector
    country_options = ["All"] + sorted(available_countries)
    selected_countries = st.sidebar.multiselect(
        label="Filter by Country",
        options=country_options,
        default=["All"],
        help="Select specific countries to filter the visualizations."
    )
    
    # 3. Year Range Selector
    selected_years = st.sidebar.slider(
        label="Select Year Range",
        min_value=2005,
        max_value=2024,
        value=(2015, 2024),
        help="Select a range of years for trend analysis."
    )
    
    # 4. Attack Type Selector
    attack_options = ["All"] + sorted(available_attack_types)
    selected_attack_types = st.sidebar.multiselect(
        label="Filter by Attack Type",
        options=attack_options,
        default=["All"]
    )
    
    # 5. Industry Selector
    industry_options = ["All"] + sorted(available_industries)
    selected_industries = st.sidebar.multiselect(
        label="Filter by Target Industry",
        options=industry_options,
        default=["All"]
    )
    
    # 6. Severity Selector
    severity_options = ["All"] + sorted(available_severities)
    selected_severities = st.sidebar.multiselect(
        label="Filter by Severity Level",
        options=severity_options,
        default=["All"]
    )
    
    # 7. Text Search Query
    search_query = st.sidebar.text_input(
        label="Keyword Search",
        value="",
        placeholder="e.g. CVE, ransomware, APT...",
        help="Search titles, CVE summaries, and description fields."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Risk Index Calibration")
    w_freq = st.sidebar.slider(
        label="Frequency Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Weights the threat occurrence count."
    )
    w_loss = st.sidebar.slider(
        label="Financial Impact Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Weights average financial loss ($M)."
    )
    w_time = st.sidebar.slider(
        label="Resolution Time Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Weights average incident resolution hours."
    )
    
    # Normalize weights
    total_w = w_freq + w_loss + w_time
    if total_w > 0:
        w_freq_norm = w_freq / total_w
        w_loss_norm = w_loss / total_w
        w_time_norm = w_time / total_w
    else:
        w_freq_norm, w_loss_norm, w_time_norm = 0.3, 0.4, 0.3
        
    # Return filter configuration dictionary
    return {
        "countries": selected_countries,
        "years": selected_years,
        "attack_types": selected_attack_types,
        "industries": selected_industries,
        "severities": selected_severities,
        "search_query": search_query,
        "weights": (w_freq_norm, w_loss_norm, w_time_norm)
    }
