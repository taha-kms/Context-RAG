# webapp/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from .services.files import list_documents
from .services.qa import ask_question

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    docs = list_documents()
    return render_template("home.html", docs=docs)


@bp.post("/ask")
def ask():
    q = (request.form.get("question") or "").strip()
    if not q:
        return redirect(url_for("main.home") + "#ask")
    answer, sources_raw, sources = ask_question(q)
    docs = list_documents()
    return render_template(
        "home.html",
        docs=docs,
        question=q,
        answer=answer,
        sources_raw=sources_raw,
        sources=sources,
    )