# webapp/services/uploads.py
from __future__ import annotations
import os
from typing import Iterable, Tuple, List, Dict
from werkzeug.utils import secure_filename
from rag.config import DATA_DIR
from rag.loaders import SUPPORTED_EXTS

ALLOWED_EXTS = set(SUPPORTED_EXTS)

def _is_allowed(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTS

def save_files(files: Iterable, subdir: str = "") -> Tuple[List[Dict], List[Dict]]:
    """
    Save uploaded files into DATA_DIR[/subdir].
    Returns (saved, skipped), where each item is:
      {"name": original, "saved_as": rel_path OR None, "reason": "... (for skipped)"}
    """
    base = os.path.abspath(DATA_DIR)
    target_dir = os.path.abspath(os.path.join(base, subdir or ""))

    # prevent path traversal outside DATA_DIR
    if not target_dir.startswith(base):
        target_dir = base

    os.makedirs(target_dir, exist_ok=True)

    saved, skipped = [], []
    for f in files:
        if not f or not getattr(f, "filename", ""):
            continue
        original = f.filename
        if not _is_allowed(original):
            skipped.append({"name": original, "saved_as": None, "reason": "unsupported extension"})
            continue

        safe_name = secure_filename(original)
        # avoid collisions by adding numeric suffix if needed
        dest = os.path.join(target_dir, safe_name)
        name, ext = os.path.splitext(safe_name)
        n = 1
        while os.path.exists(dest):
            candidate = f"{name}_{n}{ext}"
            dest = os.path.join(target_dir, candidate)
            n += 1

        f.save(dest)
        rel_path = os.path.relpath(dest, base).replace(os.sep, "/")
        saved.append({"name": original, "saved_as": rel_path, "reason": None})
    return saved, skipped
