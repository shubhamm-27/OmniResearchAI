# ==========================================================
# Backend API Client
#
# 1. Health check
# 2. Upload PDFs
# 3. Ask question
# 4. Reset knowledge base
# ==========================================================

import os

import requests


# ==========================================================
# Backend Base URL
# ==========================================================

BASE_URL = os.getenv("OMNI_BACKEND_URL", "http://localhost:8000")


# ==========================================================
# Health Check
# ==========================================================

def check_backend():

    try:

        response = requests.get(f"{BASE_URL}/health", timeout=3)

        return response.status_code == 200

    except requests.exceptions.RequestException:

        return False


# ==========================================================
# Upload PDFs
# ==========================================================

UPLOAD_TIMEOUT_PER_FILE = 300  # seconds


def upload_pdfs(files):

    uploaded_files = []

    for file in files:

        try:

            file.seek(0)

            response = requests.post(

                f"{BASE_URL}/upload",

                files=[

                    ("files", (file.name, file.getvalue(), "application/pdf"))

                ],

                timeout=UPLOAD_TIMEOUT_PER_FILE

            )

            response.raise_for_status()

            data = response.json()

            uploaded_files.extend(data.get("uploaded_files", []))

        except requests.exceptions.RequestException as e:

            # Report what succeeded before the failure, plus which
            # file broke it, instead of silently losing partial progress.

            partial = (

                {"status": "partial", "uploaded_files": uploaded_files}

                if uploaded_files else None

            )

            return partial, f"Failed uploading '{file.name}': {e}"

    return {"status": "success", "uploaded_files": uploaded_files}, None


# ==========================================================
# Ask Question
# ==========================================================

def ask_question(question, use_web=True):

    try:

        payload = {

            "question": question,

            "use_web": use_web

        }

        response = requests.post(

            f"{BASE_URL}/ask",

            json=payload,

            timeout=300

        )

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.RequestException as e:

        return None, str(e)


# ==========================================================
# Reset Knowledge Base
# ==========================================================

def reset_knowledge_base():

    try:

        response = requests.post(f"{BASE_URL}/reset", timeout=30)

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.RequestException as e:

        return None, str(e)