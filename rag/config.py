"""
Configuration for the RAG system.

Loads settings from environment variables (via .env if present),
and provides sane defaults for general-purpose usage.
"""

import os
from dotenv import load_dotenv

# Load variables from .env if available
load_dotenv()

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment or .env file")

# === Data paths ===
# Folder where your documents are stored (can contain .txt, .pdf, .md, .docx, etc.)
DATA_DIR = os.getenv("DATA_DIR", "./data")

# Persistent storage location for ChromaDB
PERSIST_DIR = os.getenv("PERSIST_DIR", "./storage/chroma")

# Name of the collection inside the vector database
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_collection")

# === Model settings ===
# Embedding model (used for vector search)
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# Chat model (used for generating final answers)
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# === Chunking parameters ===
# Size of text chunks (in characters if not using token-aware splitter)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))

# Overlap between chunks (to preserve context continuity)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# === Retrieval parameters ===
# Default number of results to fetch from the vector store
N_RESULTS = int(os.getenv("N_RESULTS", "6"))

# === Optional toggles ===
# Enable hybrid retrieval (BM25 + vector search)
USE_HYBRID = os.getenv("USE_HYBRID", "false").lower() in ("true", "1", "yes")

# Enable debug logging
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
