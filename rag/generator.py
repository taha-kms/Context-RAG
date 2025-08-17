from openai import OpenAI
from .config import OPENAI_API_KEY, CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful assistant for question answering.\n"
    "Answer strictly using ONLY the provided context. "
    "If the answer is not present, say you don't know. "
    "Be concise (max three sentences)."
)

def answer_from_context(question: str, context_docs: str) -> str:
    user_msg = f"Context:\n{context_docs}\n\nQuestion:\n{question}"
    resp = _client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp.choices[0].message.content.strip()
