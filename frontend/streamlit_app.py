# ==========================================================
# Application Entry Point
# ==========================================================

import streamlit as st

import api
import styles
import sidebar
import layout


# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(

    page_title="OmniResearchAI",

    page_icon="🔎",

    layout="wide",

    initial_sidebar_state="expanded"

)


# ==========================================================
# Load Styles
# ==========================================================

styles.load_css()


# ==========================================================
# Sidebar
# ==========================================================

sidebar.render_sidebar()


# ==========================================================
# Backend Health Check
# ==========================================================

backend_connected = api.check_backend()


# ==========================================================
# Reset Backend on a Fresh Page Load
# ==========================================================

if backend_connected and "backend_reset_done" not in st.session_state:

    api.reset_knowledge_base()

    st.session_state.backend_reset_done = True


# ==========================================================
# Main Dashboard
# ==========================================================

layout.render_main(backend_connected)