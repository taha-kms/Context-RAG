# webapp/routes.py
from flask import Blueprint, render_template

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    return render_template("home.html")