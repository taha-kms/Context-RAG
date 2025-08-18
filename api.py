# api.py
from __future__ import annotations

import json
import queue
import time
from typing import Generator, List, Optional

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from rag.pipeline import build_index, ask
from rag.config import N_RESULTS

# ---------- FastAPI app & middleware ----------

app = FastAPI(title="Context Hub RAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class ReindexRequest(BaseModel):
    data_dir: Optional[str] = Field(
        default=None,
        description="Folder containing documents to index (overrides DATA_DIR for this request)",
    )
    use_hybrid: Optional[bool] = Field(
        default=None,
        description="Override hybrid retrieval for this (re)index; True enables BM25 build",
    )

class ReindexResponse(BaseModel):
    status: str = "ok"

class AskRequest(BaseModel):
    question: str = Field(..., description="User query")
    n_results: int = Field(default=N_RESULTS, ge=1, le=50, description="Retrieval depth after de-dup")
    stream: bool = Field(default=False, description="If true, returns Server-Sent Events (SSE)")
    use_hybrid: Optional[bool] = Field(
        default=None,
        description="Override hybrid retrieval for answering this request (does not rebuild indexes)",
    )
    # NOTE: If you want to let the user point to another data dir at query time,
    # you'd need to reindex; that belongs in /reindex, not here.

class SourceItem(BaseModel):
    source: str
    chunk: Optional[int] = None

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceItem]
    elapsed_seconds: float
    streamed: bool

# ---------- Utilities ----------

def _parse_sources(sources_str: str) -> List[SourceItem]:
    """
    Convert 'Sources: path#chunk1, other.pdf#chunk3' into structured items.
    """
    out: List[SourceItem] = []
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
                out.append(SourceItem(source=path, chunk=int(chunk_str)))
            except ValueError:
                out.append(SourceItem(source=path, chunk=None))
        else:
            out.append(SourceItem(source=piece, chunk=None))
    return out

# ---------- Routes ----------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reindex", response_model=ReindexResponse)
def reindex(body: ReindexRequest = Body(default=ReindexRequest())):
    """
    (Re)build the index. If use_hybrid=True, also (re)build the BM25 sidecar.
    Safe to run repeatedly; Chroma persists to disk.
    """
    try:
        build_index(data_dir=body.data_dir, use_hybrid=body.use_hybrid)
        return ReindexResponse()
    except Exception as e:
        # Surface a readable error; avoid leaking stack traces in production
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}") from e

@app.post("/ask", response_model=AskResponse)
def ask_route(body: AskRequest):
    """
    Answer a question using the current index. If stream=true, returns SSE (text/event-stream).
    """
    # Non-streamed JSON response
    if not body.stream:
        t0 = time.perf_counter()
        # Note: use_hybrid override applies only if your pipeline respects a runtime switch.
        # Current pipeline uses global USE_HYBRID; to support per-request, you could add a param.
        answer, sources_str = ask(body.question, n_results=body.n_results, stream_handler=None)
        t1 = time.perf_counter()
        return AskResponse(
            question=body.question,
            answer=answer,
            sources=_parse_sources(sources_str),
            elapsed_seconds=round(t1 - t0, 3),
            streamed=False,
        )

    # Streamed SSE response
    # We push tokens via a thread-safe queue from the generator's stream_handler.
    q: "queue.Queue[Optional[str]]" = queue.Queue()

    def stream_tokens() -> Generator[bytes, None, None]:
        """
        Server-Sent Events:
          event: token  -> individual token chunks
          event: done   -> final payload (JSON with answer, sources, elapsed)
        """
        t0 = time.perf_counter()
        try:
            # Stream handler called by the generator while producing tokens
            def _handler(tok: str):
                q.put(tok)

            # Kick off the generation (blocking) in this same request thread;
            # tokens will be put into the queue as they arrive.
            answer, sources_str = ask(
                body.question,
                n_results=body.n_results,
                stream_handler=_handler
            )

            # Signal end of token stream
            q.put(None)

            # Drain queue while sending SSE token events
            while True:
                tok = q.get()
                if tok is None:
                    break
                yield f"event: token\ndata: {tok}\n\n".encode("utf-8")

            # Send final 'done' event with metadata
            t1 = time.perf_counter()
            done_payload = AskResponse(
                question=body.question,
                answer=answer,
                sources=_parse_sources(sources_str),
                elapsed_seconds=round(t1 - t0, 3),
                streamed=True,
            ).model_dump()
            yield f"event: done\ndata: {json.dumps(done_payload, ensure_ascii=False)}\n\n".encode("utf-8")

        except Exception as e:
            # In SSE, send an error event the client can handle
            err = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(err)}\n\n".encode("utf-8")

    return StreamingResponse(stream_tokens(), media_type="text/event-stream")
