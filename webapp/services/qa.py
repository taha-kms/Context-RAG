# webapp/services/qa.py
from __future__ import annotations
from typing import List, Dict, Any
from rag.pipeline import ask as rag_ask
from rag.config import N_RESULTS

def _parse_sources(sources_str: str) -> List[Dict[str, Any]]:
    """
    Convert 'Sources: path#chunk1, other.pdf#chunk3' -> [{"source":..., "chunk":...}, ...]
    Mirrors the API helper logic. 
    """
    out: List[Dict[str, Any]] = []
    if not sources_str:
        return out
    parts = sources_str.split(":", 1)
    payload = parts[1].strip() if len(parts) == 2 else sources_str
    if payload.lower() == "(none)":
        return out
    for piece in [p.strip() for p in payload.split(",") if p.strip()]:
        if "#chunk" in piece:
            path, chunk_str = piece.split("#chunk", 1)
            try:
                out.append({"source": path, "chunk": int(chunk_str)})
            except ValueError:
                out.append({"source": path, "chunk": None})
        else:
            out.append({"source": piece, "chunk": None})
    return out

def ask_question(question: str, n_results: int = N_RESULTS):
    """
    Calls the RAG pipeline and returns (answer: str, sources_raw: str, sources_list: list).
    """
    answer, sources_raw = rag_ask(question, n_results=n_results, stream_handler=None)
    return answer, sources_raw, _parse_sources(sources_raw)
