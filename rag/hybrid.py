"""
Hybrid retrieval utilities:
- Build a BM25 index over chunk texts
- Run BM25 search
- Fuse BM25 + vector results via Reciprocal Rank Fusion (RRF)

Artifacts are saved under PERSIST_DIR so they persist across runs.
"""

from __future__ import annotations
import os
import json
import pickle
from typing import Dict, List, Tuple
from dataclasses import dataclass

from rank_bm25 import BM25Okapi  # in requirements

from .config import PERSIST_DIR

BM25_DIR = os.path.join(PERSIST_DIR, "bm25")
BM25_CORPUS_JSON = os.path.join(BM25_DIR, "corpus.json")   # texts + metas
BM25_MODEL_PKL   = os.path.join(BM25_DIR, "bm25.pkl")

@dataclass
class Bm25Index:
    bm25: BM25Okapi
    texts: List[str]
    metas: List[Dict]

def _tokenize(text: str) -> List[str]:
    # Simple whitespace + lower; good baseline, replace with smarter tokenization if needed
    return text.lower().split()

def build_bm25_index(chunks: List[Dict]) -> None:
    """
    chunks: [{"id": "...", "text": "...", "meta": {...}}, ...]
    """
    if not chunks:
        return
    os.makedirs(BM25_DIR, exist_ok=True)
    texts = [c["text"] for c in chunks]
    metas = [c["meta"] for c in chunks]
    tokenized = [_tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized)

    # Persist model + corpus/meta
    with open(BM25_MODEL_PKL, "wb") as f:
        pickle.dump(bm25, f)
    with open(BM25_CORPUS_JSON, "w", encoding="utf-8") as f:
        json.dump({"texts": texts, "metas": metas}, f)

def load_bm25_index() -> Bm25Index | None:
    if not (os.path.exists(BM25_MODEL_PKL) and os.path.exists(BM25_CORPUS_JSON)):
        return None
    with open(BM25_MODEL_PKL, "rb") as f:
        bm25 = pickle.load(f)
    with open(BM25_CORPUS_JSON, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return Bm25Index(bm25=bm25, texts=obj["texts"], metas=obj["metas"])

def bm25_search(query: str, k: int = 20) -> Tuple[List[str], List[Dict], List[float]]:
    idx = load_bm25_index()
    if not idx:
        return [], [], []
    tokenized_q = _tokenize(query)
    scores = idx.bm25.get_scores(tokenized_q)
    # rank top-k
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
    docs = [idx.texts[i] for i, _ in ranked]
    metas = [idx.metas[i] for i, _ in ranked]
    scs  = [float(s) for _, s in ranked]
    return docs, metas, scs

def rrf_fuse(
    a_metas: List[Dict],    # list of metas in rank order (method A)
    b_metas: List[Dict],    # list of metas in rank order (method B)
    k: int = 60
) -> Dict[Tuple, float]:
    """
    Classic RRF: score += 1 / (k + rank)
    Key: (source, chunk) so duplicates merge naturally.
    Returns dict mapping key -> fused_score
    """
    scores: Dict[Tuple, float] = {}
    def add(metas, base_rank):
        for r, m in enumerate(metas):
            key = (m.get("source"), m.get("chunk"))
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + r + 1)
    add(a_metas, 0)
    add(b_metas, 0)
    return scores
