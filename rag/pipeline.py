from typing import Optional
from .config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, N_RESULTS, USE_HYBRID
from .io_utils import format_sources
from .loaders import load_documents
from .chunking import make_chunk_records
from .storage import get_collection, add_chunks, query_collection
from .retriever import dedupe_top_k
from .generator import answer_from_context
from .hybrid import build_bm25_index, bm25_search, rrf_fuse

def build_index(data_dir: Optional[str] = None, use_hybrid: Optional[bool] = None):
    data_dir = data_dir or DATA_DIR
    collection = get_collection()

    docs = load_documents(data_dir)
    if not docs:
         print("No documents found to index.")
         return collection
    chunked = []
    for d in docs:
         chunked.extend(make_chunk_records(d["id"], d["text"], CHUNK_SIZE, CHUNK_OVERLAP))
    add_chunks(chunked, collection)

    # Allow CLI to override hybrid mode at runtime
    hybrid = USE_HYBRID if use_hybrid is None else use_hybrid
    if hybrid:
        build_bm25_index(chunked)

    print(f"Indexed {len(chunked)} chunks from {len(docs)} files.")
    return collection

def ask(question: str, n_results: int = N_RESULTS, stream_handler=None):
    collection = get_collection()
    v_docs, v_metas = query_collection(collection, question, max(n_results, 20))

    if USE_HYBRID:
        b_docs, b_metas, _ = bm25_search(question, k=max(n_results, 20))
        fused = rrf_fuse(v_metas, b_metas, k=60)
        key_to_v = { (m.get("source"), m.get("chunk")): (d, m) for d, m in zip(v_docs, v_metas) }
        key_to_b = { (m.get("source"), m.get("chunk")): (d, m) for d, m in zip(b_docs, b_metas) }
        ranked_keys = sorted(fused.items(), key=lambda x: x[1], reverse=True)
        docs, metas = [], []
        for (key, _score) in ranked_keys:
            pair = key_to_v.get(key) or key_to_b.get(key)
            if pair:
                d, m = pair
                docs.append(d); metas.append(m)
            if len(docs) == n_results:
                break
    else:
        docs, metas = v_docs, v_metas

    docs, metas = dedupe_top_k(docs, metas, k=n_results)
    if not docs:
        return "No relevant information found.", "Sources: (none)"
    context = "\n\n---\n\n".join(docs)
    answer = answer_from_context(question, context, stream_handler=stream_handler)
    return answer, format_sources(metas)
