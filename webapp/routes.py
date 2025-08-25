# webapp/routes.py
from flask import Blueprint

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    # Step 2 will render templates; for now, a placeholder
    return "Flask skeleton is up. UI coming next."
