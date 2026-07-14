# ==========================================================
# FastAPI Backend
#
# Responsibilities
#
# 1. Upload PDFs
# 2. Store PDFs
# 3. Ask Questions
# 4. Reset Knowledge Base
#
# ==========================================================

import os
import shutil

from typing import Annotated

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

from pydantic import BaseModel

from pdf_parser import PDFParser
from agents import AgentOrchestrator
from config import COLLECTION_NAME, CHROMA_DB_PATH, PARENT_STORE_PATH


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(

    title="OmniResearch AI",

    version="2.0.0"

)


# ==========================================================
# Upload Folder
# ==========================================================

UPLOAD_FOLDER = "uploads"


# ==========================================================
# Clear Folder Contents (folder itself is kept)
# ==========================================================

def clear_directory_contents(path):

    os.makedirs(path, exist_ok=True)

    for entry in os.listdir(path):

        entry_path = os.path.join(path, entry)

        if os.path.isdir(entry_path):

            shutil.rmtree(entry_path)

        else:

            os.remove(entry_path)


# =============
# Startup Wipe 
# =============

clear_directory_contents(UPLOAD_FOLDER)

# ==========================================================
# Initialize Core Components
# ==========================================================


pdf_parser = PDFParser()

orchestrator = AgentOrchestrator()


# ==========================================================
# Request Model
# ==========================================================

class QuestionRequest(BaseModel):

    question: str

    use_web: bool = True


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")

def health():

    return {

        "status": "running"

    }


# ==========================================================
# Upload PDFs
# ==========================================================

@app.post("/upload")

async def upload_documents(

    files: Annotated[list[UploadFile], File(...)]

):

    try:

        file_paths = []

        for file in files:

            if not file.filename.lower().endswith(".pdf"):

                raise HTTPException(

                    status_code=400,

                    detail=f"{file.filename} is not a PDF."

                )

            save_path = os.path.join(

                UPLOAD_FOLDER,

                file.filename

            )

            with open(save_path, "wb") as f:

                shutil.copyfileobj(

                    file.file,

                    f

                )

            file_paths.append(save_path)

        documents = pdf_parser.load_documents(

            file_paths

        )

        orchestrator.rag.ingest_documents(

            documents

        )

        orchestrator.uploaded_documents = sorted(set(
            orchestrator.uploaded_documents +
            [os.path.basename(path) for path in file_paths]
        ))

        return {

            "status": "success",

            "uploaded_files": [

                os.path.basename(path)

                for path in file_paths

            ]

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Ask Question
# ==========================================================

@app.post("/ask")

async def ask_question(request: QuestionRequest):

    try:

        response = orchestrator.run(

            question=request.question,

            use_web=request.use_web

        )

        return response

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Reset Knowledge Base
# ==========================================================

@app.post("/reset")
async def reset_database():

    try:

        # Reset ChromaDB collection
        try:
            orchestrator.rag.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

        orchestrator.rag.collection = orchestrator.rag.client.create_collection(
            name=COLLECTION_NAME
        )

        print("Reset: ChromaDB collection recreated.")

        # Reset parent store
        with open(PARENT_STORE_PATH, "w", encoding="utf-8") as f:
            f.write("{}")

        orchestrator.rag.parent_store = {}

        # Reset uploaded documents
        orchestrator.uploaded_documents = []

        # Clear conversation memory
        orchestrator.memory.clear()

        # Clear uploaded PDFs
        clear_directory_contents(UPLOAD_FOLDER)

        return {
            "status": "success",
            "message": "Knowledge base reset successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )