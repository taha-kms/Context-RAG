"""
Multi-format document loaders for the RAG pipeline.

Supported:
- .txt       Plain text
- .md        Markdown -> HTML -> plain text
- .pdf       Text-based PDFs via pypdf
- .docx      Word documents via python-docx
- .html/.htm HTML via BeautifulSoup
- .csv       Tabular -> flattened text via pandas

Each loader returns a list of {"id": <relative-path>, "text": <string>} dicts.

Notes:
- Binary/scanned PDFs are not OCR'd.
- CSVs are flattened conservatively to keep things readable.
"""

from __future__ import annotations
import os
from typing import Dict, List, Iterable, Tuple

# Optional deps are already in requirements; import guarded so repo still imports gracefully
try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore

try:
    import docx  # python-docx  # type: ignore
except Exception:  # pragma: no cover
    docx = None  # type: ignore

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

try:
    import markdown as md_lib  # type: ignore
except Exception:  # pragma: no cover
    md_lib = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


TEXT_EXTS = {".txt"}
MD_EXTS = {".md", ".markdown"}
PDF_EXTS = {".pdf"}
DOCX_EXTS = {".docx"}
HTML_EXTS = {".html", ".htm"}
CSV_EXTS = {".csv"}

SUPPORTED_EXTS = TEXT_EXTS | MD_EXTS | PDF_EXTS | DOCX_EXTS | HTML_EXTS | CSV_EXTS


def _iter_paths(root: str) -> Iterable[Tuple[str, str]]:
    """Yield (abs_path, rel_id) for supported files under root (recursive)."""
    if not os.path.exists(root):
        print(f"Warning: Directory {root} does not exist.")
        return
    for base, _, files in os.walk(root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in SUPPORTED_EXTS:
                abs_path = os.path.join(base, fn)
                rel_id = os.path.relpath(abs_path, root).replace(os.sep, "/")
                yield abs_path, rel_id


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _load_txt(path: str) -> str:
    return _read_text(path)


def _load_md(path: str) -> str:
    raw = _read_text(path)
    if md_lib is None or BeautifulSoup is None:
        # Fallback: return raw markdown if deps are missing
        return raw
    html = md_lib.markdown(raw, output_format="html5")
    soup = BeautifulSoup(html, "lxml") if BeautifulSoup else None
    return soup.get_text(separator="\n").strip() if soup else raw


def _load_pdf(path: str) -> str:
    if PdfReader is None:
        print("Warning: pypdf not installed; skipping PDF:", path)
        return ""
    try:
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            txt = page.extract_text() or ""
            if txt:
                parts.append(txt)
        return "\n".join(parts).strip()
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""


def _load_docx(path: str) -> str:
    if docx is None:
        print("Warning: python-docx not installed; skipping DOCX:", path)
        return ""
    try:
        d = docx.Document(path)
        paras = [p.text for p in d.paragraphs if p.text and p.text.strip()]
        return "\n".join(paras).strip()
    except Exception as e:
        print(f"Error reading DOCX {path}: {e}")
        return ""


def _load_html(path: str) -> str:
    raw = _read_text(path)
    if BeautifulSoup is None:
        print("Warning: beautifulsoup4 not installed; returning raw HTML:", path)
        return raw
    try:
        soup = BeautifulSoup(raw, "lxml")
        # Remove script/style
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        return soup.get_text(separator="\n").strip()
    except Exception as e:
        print(f"Error parsing HTML {path}: {e}")
        return raw


def _load_csv(path: str, max_rows: int = 5000) -> str:
    if pd is None:
        print("Warning: pandas not installed; skipping CSV:", path)
        return ""
    try:
        df = pd.read_csv(path)
        if len(df) > max_rows:
            df = df.iloc[:max_rows].copy()
        # Flatten: "col1: v1 | col2: v2"
        cols = list(map(str, df.columns))
        rows = []
        for _, row in df.iterrows():
            cells = []
            for c in cols:
                val = row[c]
                # Cast cleanly and collapse newlines/tabs
                sval = str(val).replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
                cells.append(f"{c}: {sval}")
            rows.append(" | ".join(cells))
        return "\n".join(rows).strip()
    except Exception as e:
        print(f"Error reading CSV {path}: {e}")
        return ""


def _load_one(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTS:
        return _load_txt(path)
    if ext in MD_EXTS:
        return _load_md(path)
    if ext in PDF_EXTS:
        return _load_pdf(path)
    if ext in DOCX_EXTS:
        return _load_docx(path)
    if ext in HTML_EXTS:
        return _load_html(path)
    if ext in CSV_EXTS:
        return _load_csv(path)
    return ""


def load_documents(directory_path: str) -> List[Dict[str, str]]:
    """
    Load all supported documents under directory_path (recursively).

    Returns: [{"id": "<relative/path.ext>", "text": "..."}]
    """
    docs: List[Dict[str, str]] = []
    for abs_path, rel_id in _iter_paths(directory_path) or []:
        try:
            text = _load_one(abs_path)
            if text and text.strip():
                docs.append({"id": rel_id, "text": text})
            else:
                print(f"Warning: no text extracted from {abs_path}")
        except Exception as e:
            print(f"Error loading {abs_path}: {e}")
    if not docs:
        print(f"No supported documents found in {directory_path}.")
    return docs
