# webapp/services/files.py
from __future__ import annotations
import os
from typing import List, Dict, Optional
from rag.config import DATA_DIR
from rag.loaders import SUPPORTED_EXTS  # reuse repo’s allowed types

def list_documents(root: Optional[str] = None) -> List[Dict]:
    """
    Return a list of files under DATA_DIR (or `root`) that match SUPPORTED_EXTS.
    Each item: {"path": "rel/path.ext", "size": 12345}
    """
    base = os.path.abspath(root or DATA_DIR)
    items: List[Dict] = []
    if not os.path.exists(base):
        return items
    for dirpath, _, filenames in os.walk(base):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in SUPPORTED_EXTS:
                abs_path = os.path.join(dirpath, fn)
                rel_path = os.path.relpath(abs_path, base).replace(os.sep, "/")
                try:
                    size = os.path.getsize(abs_path)
                except OSError:
                    size = 0
                items.append({"path": rel_path, "size": size})
    # stable, human-friendly order
    items.sort(key=lambda x: x["path"].lower())
    return items
