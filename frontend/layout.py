# ==========================================================
# Main Screen Layout
#
# Above the fold
#   1. Hero + Backend Connected badge
#   2. Knowledge Base metrics
#   3. Upload card + Search card
#
# Below the fold
#   4. Generated Answer
#   5. Research Summary
#   6. References
#   7. Pipeline Information
# ==========================================================

import io

import streamlit as st

from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter

import api
import components


# ==========================================================
# Chunking constants
# ==========================================================

CHUNK_SIZE = 500

CHUNK_OVERLAP = 100


# ==========================================================
# Session State
# ==========================================================

def _init_session_state():

    st.session_state.setdefault("uploaded_pdfs", [])

    st.session_state.setdefault("indexed_chunks", 0)

    st.session_state.setdefault("last_result", None)


# ==========================================================
# Chunk Estimation (local, mirrors backend chunking config)
# ==========================================================

def _count_chunks(files):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP

    )

    total_chunks = 0

    for file in files:

        try:

            reader = PdfReader(io.BytesIO(file.getvalue()))

            text = " ".join(

                (page.extract_text() or "")

                for page in reader.pages

            )

            text = " ".join(text.split())

            total_chunks += len(splitter.split_text(text)) if text else 0

        except Exception:

            continue

    return total_chunks


# ==========================================================
# Upload Handling
# ==========================================================

def _handle_upload(files, upload_clicked):

    if not upload_clicked:

        return

    if not files:

        st.warning("Select at least one PDF before uploading.")

        return

    with st.spinner("Indexing documents..."):

        response, error = api.upload_pdfs(files)

        chunk_delta = _count_chunks(files)

    if error:

        st.error(f"Upload failed: {error}")

        return

    new_files = response.get("uploaded_files", [])

    for filename in new_files:

        if filename not in st.session_state.uploaded_pdfs:

            st.session_state.uploaded_pdfs.append(filename)

    st.session_state.indexed_chunks += chunk_delta

    st.success(f"Indexed {len(new_files)} PDF(s) successfully.")


# ==========================================================
# Reset Handling
# ==========================================================

def _handle_reset(reset_clicked):

    if not reset_clicked:

        return

    with st.spinner("Resetting knowledge base..."):

        response, error = api.reset_knowledge_base()

    if error:

        st.error(f"Reset failed: {error}")

        return

    st.session_state.uploaded_pdfs = []

    st.session_state.indexed_chunks = 0

    st.session_state.last_result = None

    st.success("Knowledge base reset successfully.")

    st.rerun()


# ==========================================================
# Ask Handling
# ==========================================================

def _handle_ask(question, use_web, ask_clicked):

    if not ask_clicked:

        return

    if not question or not question.strip():

        st.warning("Enter a research question before searching.")

        return

    with st.spinner("Running the multi-agent research pipeline..."):

        response, error = api.ask_question(question.strip(), use_web=use_web)

    if error:

        st.error(f"Search failed: {error}")

        return

    st.session_state.last_result = response


# ==========================================================
# Research Summary Text
# ==========================================================

def _build_summary(result):

    used_pdf = result.get("used_pdf", False)

    used_web = result.get("used_web", False)

    references = result.get("references", {})

    pdf_count = len(references.get("pdf_sources", []))

    web_count = len(references.get("web_sources", []))

    if used_pdf and used_web:

        source_line = (

            f"This answer draws on {pdf_count} document source(s) "

            f"and {web_count} live web result(s)."

        )

    elif used_pdf:

        source_line = f"This answer draws on {pdf_count} document source(s)."

    elif used_web:

        source_line = f"This answer draws on {web_count} live web result(s)."

    else:

        source_line = "This answer was generated without additional retrieved context."

    return f"{source_line} {result.get('router_reason', '')}"


# ==========================================================
# Above the Fold
# ==========================================================

def _render_above_fold(backend_connected):

    components.render_hero(backend_connected)

    components.render_kb_metrics(

        pdf_count=len(st.session_state.uploaded_pdfs),

        chunk_count=st.session_state.indexed_chunks,

        document_count=len(st.session_state.uploaded_pdfs)

    )

    st.write("")

    upload_col, search_col = st.columns(2, gap="medium")

    with upload_col:

        files, upload_clicked, reset_clicked = components.render_upload_card()

    with search_col:

        question, use_web, ask_clicked = components.render_search_card()

    _handle_upload(files, upload_clicked)

    _handle_reset(reset_clicked)

    _handle_ask(question, use_web, ask_clicked)


# ==========================================================
# Below the Fold
# ==========================================================

def _render_below_fold():

    st.write("")
    st.write("")

    result = st.session_state.last_result

    if not result:

        components.render_empty_state()

        return

    components.render_answer_card(result.get("answer", ""))

    components.render_summary_card(_build_summary(result))

    references = result.get("references", {})

    components.render_references_card(

        pdf_sources=references.get("pdf_sources", []),

        web_sources=references.get("web_sources", [])

    )

    components.render_pipeline_card(

        used_pdf=result.get("used_pdf", False),

        used_web=result.get("used_web", False),

        router_reason=result.get("router_reason", "")

    )


# ==========================================================
# Render Main
# ==========================================================

def render_main(backend_connected):

    _init_session_state()

    _render_above_fold(backend_connected)

    _render_below_fold()