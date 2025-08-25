# webapp/services/indexing.py
from __future__ import annotations
import time
from typing import Optional, Dict, Any
from rag.pipeline import build_index
from rag.config import USE_HYBRID

def reindex(use_hybrid: Optional[bool] = None) -> Dict[str, Any]:
    """
    Rebuild the index from DATA_DIR and (optionally) BM25 hybrid sidecar.
    Returns metadata for the UI.
    """
    t0 = time.perf_counter()
    # If use_hybrid is None, the pipeline will default to config.USE_HYBRID
    build_index(use_hybrid=use_hybrid)
    t1 = time.perf_counter()
    return {
        "elapsed_seconds": round(t1 - t0, 2),
        "hybrid": USE_HYBRID if use_hybrid is None else bool(use_hybrid),
        # Note: build_index() prints counts but doesn't return them; we keep time + mode. :contentReference[oaicite:2]{index=2}
    }
