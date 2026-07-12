# ==========================================================
#
# Project Configuration
#
# 1. API Keys
# 2. LLM Settings
# 3. Embedding Model
# 4. Parent-Child Chunking
# 5. Retrieval
# 6. ChromaDB
#
# ==========================================================

from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv(

    Path(__file__).resolve().parent.parent / ".env"

)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ==========================================================
# Gemini Configuration
# ==========================================================

GEMINI_MODEL = "gemini-3.5-flash"

TEMPERATURE = 0.2

# ==========================================================
# Embedding Model
# ==========================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ==========================================================
# Parent Chunk Configuration
# ==========================================================

PARENT_CHUNK_SIZE = 1500

PARENT_CHUNK_OVERLAP = 200

# ==========================================================
# Child Chunk Configuration
# ==========================================================

CHILD_CHUNK_SIZE = 350

CHILD_CHUNK_OVERLAP = 75

# ==========================================================
# Retrieval Configuration
# ==========================================================

TOP_K_CHILDREN = 30

MAX_PARENT_CONTEXT = 6

# ==========================================================
# ChromaDB
# ==========================================================

CHROMA_DB_PATH = "./chromadb"

COLLECTION_NAME = "research_documents"