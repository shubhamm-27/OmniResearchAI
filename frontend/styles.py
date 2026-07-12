# ==========================================================
# Loads and injects the global stylesheet.
# ==========================================================

from pathlib import Path

import streamlit as st


# ==========================================================
# Color Tokens (kept in sync with styles.css)
# ==========================================================

COLORS = {

    "primary": "#2563EB",
    "background": "#F7F9FC",
    "card": "#FFFFFF",
    "text": "#111827",
    "text_secondary": "#6B7280",
    "border": "#E5E7EB",
    "success": "#16A34A",
    "danger": "#DC2626",

}


# ==========================================================
# Inject CSS
# ==========================================================

def load_css():

    css_path = Path(__file__).parent / "styles.css"

    css = css_path.read_text(encoding="utf-8")

    st.markdown(

        f"<style>{css}</style>",

        unsafe_allow_html=True

    )