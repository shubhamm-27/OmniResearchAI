# ==========================================================
# Reusable UI building blocks
#
# 1. Sidebar widgets
# 2. Hero
# 3. Metric cards
# 4. Upload card
# 5. Search card
# 6. Answer card
# 7. Summary card
# 8. References card
# 9. Pipeline card
# ==========================================================

import streamlit as st


# ==========================================================
# Icons (inline SVG, currentColor so CSS controls the fill)
# ==========================================================

GITHUB_ICON = """<svg viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23a11.5 11.5 0 013.003-.404c1.02.005 2.047.138 3.006.404 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222 0 1.606-.014 2.898-.014 3.293 0 .322.216.694.825.576C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>"""

LINKEDIN_ICON = """<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>"""

EMAIL_ICON = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>"""


# ==========================================================
# Sidebar Widgets
# ==========================================================

def render_sidebar_header(name):

    st.markdown(

        f"""
        <div class="sb-brand-box">
            <p class="sb-title">{name}</p>
        </div>
        <hr class="sb-divider">
        """,

        unsafe_allow_html=True

    )


def render_sidebar_section(heading, body_html):

    st.markdown(

        f"""
        <p class="sb-heading">{heading}</p>
        {body_html}
        <hr class="sb-divider">
        """,

        unsafe_allow_html=True

    )


def render_tech_stack(heading, technologies):

    tags = "".join(f'<span class="sb-tag">{tech}</span>' for tech in technologies)

    st.markdown(

        f"""
        <p class="sb-heading">{heading}</p>
        <div class="sb-tag-row">{tags}</div>
        <hr class="sb-divider">
        """,

        unsafe_allow_html=True

    )


def render_developer_card(heading, name, github_url, linkedin_url, email):

    st.markdown(

        f"""
        <p class="sb-heading">{heading}</p>
        <p class="sb-dev-name">{name}</p>
        <div class="sb-links">
            <a class="sb-link" href="mailto:{email}">{EMAIL_ICON}Email</a>
            <span class="sb-link-sep"></span>
            <a class="sb-link" href="{linkedin_url}" target="_blank">{LINKEDIN_ICON}LinkedIn</a>
            <span class="sb-link-sep"></span>
            <a class="sb-link" href="{github_url}" target="_blank">{GITHUB_ICON}GitHub</a>
            
        </div>
        """,

        unsafe_allow_html=True

    )


# ==========================================================
# Hero
# ==========================================================

def render_hero(backend_connected):

    badge_class = "badge-connected" if backend_connected else "badge-disconnected"

    badge_text = "Backend Connected" if backend_connected else "Backend Unreachable"

    st.markdown(

        f"""
        <div class="hero">
            <div>
                <h1 class="hero-title">Omni<span>Research</span>AI</h1>
                <p class="hero-subtitle">Multi-Agent RAG Research Assistant</p>
            </div>
            <div class="badge {badge_class}">
                <span class="badge-dot"></span>{badge_text}
            </div>
        </div>
        """,

        unsafe_allow_html=True

    )


# ==========================================================
# Knowledge Base Metrics
# ==========================================================

def render_kb_metrics(pdf_count, chunk_count, document_count):

    st.markdown(

        """
        <div class="section-title">
            <span class="section-icon">&#128218;</span>Knowledge Base
        </div>
        """,

        unsafe_allow_html=True

    )

    metrics = [

        ("Uploaded PDFs", pdf_count),

        ("Indexed Chunks", chunk_count),

        ("Documents", document_count),

    ]

    columns = st.columns(3)

    for column, (label, value) in zip(columns, metrics):

        with column:

            with st.container(border=True):

                st.markdown(

                    f"""
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                    """,

                    unsafe_allow_html=True

                )


# ==========================================================
# Upload Card
# ==========================================================

def render_upload_card():

    with st.container(border=True):

        st.markdown(

            """
            <div class="section-title">
                <span class="section-icon">&#8593;</span>Upload PDFs
            </div>
            <div class="section-caption">Drag and drop one or more PDFs to add to the knowledge base</div>
            """,

            unsafe_allow_html=True

        )

        files = st.file_uploader(

            "Upload PDFs",

            type=["pdf"],

            accept_multiple_files=True,

            label_visibility="collapsed",

            key="omni_file_uploader"

        )

        col1, col2 = st.columns([2, 1])

        with col1:

            upload_clicked = st.button(

                "Upload & Index",

                use_container_width=True,

                type="primary",

                key="omni_upload_button"

            )

        with col2:

            reset_clicked = st.button(

                "Reset",

                use_container_width=True,

                type="secondary",

                key="omni_reset_button"

            )

    return files, upload_clicked, reset_clicked


# ==========================================================
# Search Card
# ==========================================================

def render_search_card():

    with st.container(border=True):

        st.markdown(

            """
            <div class="section-title">
                <span class="section-icon">&#128269;</span>Ask a Research Question
            </div>
            <div class="section-caption">Answers are grounded in your PDFs and, optionally, live web search</div>
            """,

            unsafe_allow_html=True

        )

        question = st.text_area(

            "Question",

            placeholder="e.g. What are the key findings on solid-state batteries?",

            label_visibility="collapsed",

            height=100,

            key="omni_question_input"

        )

        use_web = st.toggle(

            "Enable live web search",

            value=True,

            key="omni_use_web_toggle"

        )

        ask_clicked = st.button(

            "Ask Question",

            use_container_width=True,

            type="primary",

            key="omni_ask_button"

        )

    return question, use_web, ask_clicked


# ==========================================================
# Generated Answer Card
# ==========================================================

def render_answer_card(answer):

    with st.container(border=True):

        st.markdown(

            """
            <div class="section-title">
                <span class="section-icon">&#129302;</span>Generated Answer
            </div>
            """,

            unsafe_allow_html=True

        )

        st.markdown(f'<div class="answer-body">', unsafe_allow_html=True)

        st.markdown(answer)

        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# Research Summary Card
# ==========================================================

def render_summary_card(summary_text):

    with st.container(border=True):

        st.markdown(

            f"""
            <div class="section-title">
                <span class="section-icon">&#128203;</span>Research Summary
            </div>
            <p class="summary-text">{summary_text}</p>
            """,

            unsafe_allow_html=True

        )


# ==========================================================
# References Card
# ==========================================================

def render_references_card(pdf_sources, web_sources):

    with st.container(border=True):

        st.markdown(

            """
            <div class="section-title">
                <span class="section-icon">&#128278;</span>References
            </div>
            """,

            unsafe_allow_html=True

        )

        if not pdf_sources and not web_sources:

            st.markdown(

                '<div class="ref-empty">No sources were used for this answer.</div>',

                unsafe_allow_html=True

            )

            return

        if pdf_sources:

            badges = "".join(

                f'<span class="ref-badge">&#128196; {source}</span>'

                for source in pdf_sources

            )

            st.markdown(

                f'<p class="ref-group-label">PDF Sources</p><div class="ref-badges">{badges}</div>',

                unsafe_allow_html=True

            )

        if web_sources:

            badges = "".join(

                f'<span class="ref-badge">&#127760; '
                f'<a href="{source.get("url", "#")}" target="_blank">{source.get("title", "Untitled")}</a>'
                f'</span>'

                for source in web_sources

            )

            st.markdown(

                f'<p class="ref-group-label">Web Sources</p><div class="ref-badges">{badges}</div>',

                unsafe_allow_html=True

            )


# ==========================================================
# Pipeline Information Card
# ==========================================================

def render_pipeline_card(used_pdf, used_web, router_reason):

    with st.container(border=True):

        st.markdown(

            """
            <div class="section-title">
                <span class="section-icon">&#9881;</span>Pipeline Information
            </div>
            """,

            unsafe_allow_html=True

        )

        def status_html(label, used):

            state_class = "on" if used else "off"

            state_text = "Used" if used else "Not Used"

            return (

                f'<div class="pipeline-item">'
                f'<div class="pipeline-item-label">{label}</div>'
                f'<div class="pipeline-status {state_class}">'
                f'<span class="status-dot"></span>{state_text}'
                f'</div></div>'

            )

        st.markdown(

            f"""
            <div class="pipeline-grid">
                {status_html("PDF Agent", used_pdf)}
                {status_html("Web Agent", used_web)}
            </div>
            <div class="pipeline-decision-label">Router Decision</div>
            <div class="pipeline-decision-box">{router_reason}</div>
            """,

            unsafe_allow_html=True

        )


# ==========================================================
# Empty State
# ==========================================================

def render_empty_state():

    with st.container(border=True):

        st.markdown(

            """
            <div class="empty-state">
                Ask a research question above to see the generated answer,
                research summary, references, and pipeline details here.
            </div>
            """,

            unsafe_allow_html=True

        )