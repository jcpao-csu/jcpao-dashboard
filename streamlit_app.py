"""Main Streamlit page that runs all navigation for JCPAO Dashboard"""

import streamlit as st
from pathlib import Path

# --- Configure Streamlit page settings --- 

jcpao_logo = Path("assets/logo/jcpao_logo_750x750.png")

st.set_page_config(
    page_title="JCPAO Dashboard", # JCPAO staff-view
    page_icon=jcpao_logo, 
    layout="wide", # "centered" or "wide"
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "mailto:ujcho@jacksongov.org", # To report a bug, please email
        'About': "The JCPAO Dashboard was developed by Joseph Cho (Crime Analyst) and the Crime Strategies Unit (CSU) of the Jackson County Prosecuting Attorney's Office. For questions, suggestions, or bugs, please reach out to Joseph Cho at ujcho@jacksongov.org!"
    }
)

# --- JCPAO Streamlit page logo --- 
st.logo(jcpao_logo, size="large", link="https://www.jacksoncountyprosecutor.com")

# --- Steamlit sidebar --- 


# --- Page Navigation ---
pages = {
    "Prosecuting Cases": [
        st.Page("pages/case_pages/main_view.py", title="Overview"),
        # st.Page("pages/case_pages/rcvd_cases.py", title="Received Cases"),
        # st.Page("pages/case_pages/fld_cases.py", title="Filed Cases"),
        # st.Page("pages/case_pages/ntfld_cases.py", title="Not Filed Cases"),
        # st.Page("pages/case_pages/disp_cases.py", title="Disposed Cases")
    ],
    # "Violent Crime in KCMO": [
    #     st.Page("pages/violence_pages/shoot_review.py", title="Overview")
    # ],
    "Domestic Violence": [
        st.Page("pages/dv_pages/dv_main.py", title="Overview"), # pages/dv_pages/
        st.Page("pages/dv_pages/dv_cases.py", title="Domestic Assault Cases"),
        st.Page("pages/dv_pages/ipvi_cases.py", title="Intimate Partner Violence (IPV)"),
        # st.Page("pages/dv_pages/harassment_cases.py", title="Harassment Cases"),
        # st.Page("pages/dv_pages/stalking_cases.py", title="Stalking Cases")
    ],
    # "Other": [
    #     st.Page("pages/other_pages/blairs_law.py", title="Blair's Law"),
    #     st.Page("pages/other_pages/valentines_law.py", title="Valentine's Law")
    # ],
    "Resources": [
        st.Page("pages/resources_pages/about_jcpao.py", title="About the JCPAO"),
        st.Page("pages/resources_pages/learn_more.py", title="Process of a Case"),
        st.Page("pages/resources_pages/codes_glossary.py", title="Criminal Charge Codes")
        # st.page_link("https://jcpao-search.streamlit.app/", label="Police Report Search Tool", icon="🔎"),
        # st.page_link("https://jacksoncountyprosecutor.com", label="JCPAO Website")
    ],
}

pg = st.navigation(pages, position="top")
pg.run()
