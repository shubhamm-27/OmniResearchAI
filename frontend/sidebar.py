# ==========================================================
# Fixed Sidebar
#
# 1. Title
# 2. Project Information
# 3. Technology Stack
# 4. Developed By
# ==========================================================

import streamlit as st

import components


# ==========================================================
# Content
# ==========================================================

DEVELOPER_NAME = "Shubham Sharma"

GITHUB_URL = "https://github.com/shubhamm-27"

LINKEDIN_URL = "https://www.linkedin.com/in/shubhammm27"

EMAIL = "shubham789keeds@gmail.com"

PROJECT_DESCRIPTION = (

    "A multi-agent RAG assistant that analyzes PDFs, retrieves relevant "

    "context, optionally searches the live web, and generates "

    "citation-backed answers."

)

TECH_STACK = [

    "Python",
    "FastAPI",
    "Streamlit",
    "Gemini 3.5 Flash",
    "LangChain",
    "ChromaDB",
    "Sentence Transformers",
    "Tavily",

]


# ==========================================================
# Render Sidebar
# ==========================================================

def render_sidebar():

    with st.sidebar:

        components.render_sidebar_header(

            name="OmniResearchAI"

        )

        components.render_sidebar_section(

            heading="Project Information",

            body_html=f'<p class="sb-text">{PROJECT_DESCRIPTION}</p>'

        )

        components.render_tech_stack(

            heading="Technology Stack",

            technologies=TECH_STACK

        )

        components.render_developer_card(

            heading="Developed By",

            name=DEVELOPER_NAME,

            github_url=GITHUB_URL,

            linkedin_url=LINKEDIN_URL,

            email=EMAIL

        )