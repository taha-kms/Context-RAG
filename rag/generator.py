from __future__ import annotations
import time, random
from typing import Callable, Optional
from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError, ServiceUnavailableError

from .config import OPENAI_API_KEY, CHAT_MODEL, REQUEST_TIMEOUT, MAX_RETRIES, STREAM_ANSWERS

_client = OpenAI(api_key=OPENAI_API_KEY, timeout=REQUEST_TIMEOUT)

SYSTEM_PROMPT = (
    "You are a helpful assistant for question answering.\n"
    "Answer strictly using ONLY the provided context. "
    "If the answer is not present, say you don't know. "
    "Be concise (max three sentences)."
)

# --- internal: retry w/ exponential backoff ---
_RETRY_EXCS = (
    APITimeoutError,
    RateLimitError,
    APIConnectionError,
    ServiceUnavailableError,
    APIError,
)

def _with_retries(callable_fn):
    """
    Run callable_fn() with exponential backoff retries on transient failures.
    Total attempts = 1 + MAX_RETRIES.
    """
    attempt = 0
    while True:
        try:
            return callable_fn()
        except _RETRY_EXCS as e:
            if attempt >= MAX_RETRIES:
                raise
            # Exponential backoff with jitter (1, 2, 4, 8...) + [0,1)
            sleep_s = min(2 ** attempt, 8) + random.random()
            time.sleep(sleep_s)
            attempt += 1

# --- public API ---
def answer_from_context(
    question: str,
    context_docs: str,
    *,
    stream_handler: Optional[Callable[[str], None]] = None,
    timeout: Optional[float] = None
) -> str:
    """
    If stream_handler is provided or STREAM_ANSWERS=true, tokens are emitted to the handler as they arrive.
    Returns the full text either way.
    """
    user_msg = f"Context:\n{context_docs}\n\nQuestion:\n{question}"
    use_stream = STREAM_ANSWERS or (stream_handler is not None)

    if use_stream:
        # Streamed path
        def _do_stream():
            return _client.chat.completions.create(
                model=CHAT_MODEL,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                stream=True,
                timeout=timeout or REQUEST_TIMEOUT,
            )

        stream = _with_retries(_do_stream)
        parts: list[str] = []
        # The SDK yields chunks with delta content as they arrive
        for chunk in stream:
            delta = getattr(chunk.choices[0].delta, "content", None)
            if delta:
                parts.append(delta)
                if stream_handler:
                    stream_handler(delta)
        return "".join(parts).strip()

    # Non-streaming path
    def _do_call():
        return _client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            timeout=timeout or REQUEST_TIMEOUT,
        )

    resp = _with_retries(_do_call)
    return resp.choices[0].message.content.strip()
