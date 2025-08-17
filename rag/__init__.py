"""
RAG (Retrieval-Augmented Generation) package.

This package provides modular components for:
- Loading and preprocessing documents (rag.io_utils, rag.loaders)
- Splitting text into chunks (rag.chunking)
- Creating embeddings (rag.embeddings)
- Storing and retrieving from vector databases (rag.storage, rag.retriever)
- Generating answers using LLMs (rag.generator)
- Orchestrating the full pipeline (rag.pipeline)

Typical usage:
    from rag.pipeline import build_index, ask

    # Build the index
    build_index()

    # Ask a question
    answer, sources = ask("What is the capital of France?")
    print(answer, sources)
"""

__version__ = "0.1.0"

# Expose main entry points at the package level
from .pipeline import build_index, ask

__all__ = ["build_index", "ask"]
