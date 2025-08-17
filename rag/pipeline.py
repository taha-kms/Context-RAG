from typing import Optional
from .config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, N_RESULTS
from .io_utils import format_sources
from .loaders import load_documents
from .chunking import make_chunk_records
from .storage import get_collection, add_chunks, query_collection
from .retriever import dedupe_top_k
from .generator import answer_from_context

def build_index(data_dir: Optional[str] = None):
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
    print(f"Indexed {len(chunked)} chunks from {len(docs)} files.")
    return collection

def ask(question: str, n_results: int = N_RESULTS):
    collection = get_collection()
    docs, metas = query_collection(collection, question, n_results)
    docs, metas = dedupe_top_k(docs, metas, k=n_results)
    if not docs:
        return "No relevant information found.", "Sources: (none)"
    context = "\n\n---\n\n".join(docs)
    answer = answer_from_context(question, context)
    return answer, format_sources(metas)
