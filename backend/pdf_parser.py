# ==========================================================
# Responsibilities
#
# 1. Read one or multiple PDFs
# 2. Extract clean text
# 3. Return structured documents
#
# ==========================================================

import os

from langchain_community.document_loaders import PyPDFLoader


class PDFParser:

    def __init__(self):
        pass

    # ======================================================
    # Read a Single PDF
    # ======================================================

    def read_pdf(self, file_path):

        loader = PyPDFLoader(file_path)

        pages = loader.load()

        text = ""

        for page in pages:

            text += page.page_content + "\n"

        document = {

            "file_name": os.path.basename(file_path),

            "text": text

        }

        return document

    # ======================================================
    # Read Multiple PDFs
    # ======================================================

    def load_documents(self, file_paths):

        documents = []

        for file_path in file_paths:

            documents.append(

                self.read_pdf(file_path)

            )

        print(f"{len(documents)} PDF(s) loaded successfully.")

        return documents