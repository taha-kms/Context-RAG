from flask import Blueprint, render_template, request, redirect, url_for
from .services.files import list_documents
from .services.qa import ask_question
from .services.uploads import save_files
from .services.indexing import reindex as do_reindex
from werkzeug.exceptions import RequestEntityTooLarge


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
    docs = list_documents()
    try:
        answer, sources_raw, sources = ask_question(q)
        return render_template("home.html", docs=docs, question=q, answer=answer, sources_raw=sources_raw, sources=sources)
    except Exception as e:
        # Keep it generic for users; still useful
        return render_template("home.html", docs=docs, question=q, qa_error=str(e))

@bp.post("/upload")
def upload():
    files = request.files.getlist("files")
    subdir = (request.form.get("subdir") or "").strip().strip("/").replace("\\", "/")
    docs = list_documents()
    try:
        saved, skipped = save_files(files, subdir=subdir)
    except Exception as e:
        return render_template("home.html", docs=docs, upload_error=str(e))

    try:
        reidx = do_reindex()
    except Exception as e:
        # Show upload result even if reindex failed
        return render_template(
            "home.html",
            docs=list_documents(),
            upload_result={"saved": saved, "skipped": skipped, "subdir": subdir},
            reindex_error=str(e),
        )

    return render_template(
        "home.html",
        docs=list_documents(),
        upload_result={"saved": saved, "skipped": skipped, "subdir": subdir},
        reindex_result=reidx,
    )

@bp.post("/reindex")
def reindex():
    docs = list_documents()
    try:
        reidx = do_reindex()
        return render_template("home.html", docs=docs, reindex_result=reidx)
    except Exception as e:
        return render_template("home.html", docs=docs, reindex_error=str(e))


@bp.app_errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    docs = list_documents()
    return render_template("home.html", docs=docs, upload_error="File(s) too large. Max size is 50 MB."), 413