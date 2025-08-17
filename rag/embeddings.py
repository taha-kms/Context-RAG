from openai import OpenAI
from typing import List
from .config import OPENAI_API_KEY, EMBED_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Optional manual embedding. Not used if Chroma has an embedding_function."""
    resp = _client.embeddings.create(input=texts, model=EMBED_MODEL)
    return [d.embedding for d in resp.data]
