import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Tuple
from .config import OPENAI_API_KEY, EMBED_MODEL, PERSIST_DIR, COLLECTION_NAME

def get_collection():
    os.makedirs(PERSIST_DIR, exist_ok=True)
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY, model_name=EMBED_MODEL
    )
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=ef
    )

def add_chunks(chunks: List[Dict], collection) -> None:
    if not chunks:
        return
    ids = [c["id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metas = [c["meta"] for c in chunks]
    # Let Chroma handle embeddings via the collection's embedding_function
    collection.add(ids=ids, documents=docs, metadatas=metas)

def query_collection(collection, question: str, n_results: int) -> Tuple[List[str], List[Dict]]:
    res = collection.query(query_texts=[question], n_results=n_results)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return docs, metas
