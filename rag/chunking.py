from typing import List, Dict
import re

def split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Sentence-aware chunking with overlap; overlap must be < chunk_size."""
    if not text:
        return []
    chunk_overlap = max(0, min(chunk_overlap, max(0, chunk_size - 1)))
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, curr = [], ""
    for s in sents:
        if curr and len(curr) + len(s) + 1 > chunk_size:
            chunks.append(curr)
            curr = (curr[-chunk_overlap:] if chunk_overlap else "")
        curr = (curr + " " + s).strip() if curr else s
    if curr:
        chunks.append(curr)
    return chunks

def make_chunk_records(doc_id: str, text: str, chunk_size: int, chunk_overlap: int) -> List[Dict]:
    chunks = split_text(text, chunk_size, chunk_overlap)
    return [
        {
            "id": f"{doc_id}_chunk{i+1}",
            "text": chunk,
            "meta": {"source": doc_id, "chunk": i + 1}
        }
        for i, chunk in enumerate(chunks)
    ]
