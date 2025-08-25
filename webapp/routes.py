# webapp/routes.py
from flask import Blueprint, render_template
from .services.files import list_documents

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    docs = list_documents()
    return render_template("home.html", docs=docs)