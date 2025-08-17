import os
from typing import List, Dict

def load_txt_documents(directory_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(directory_path):
        print(f"Warning: Directory {directory_path} does not exist.")
        return []
    docs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            path = os.path.join(directory_path, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs.append({"id": filename, "text": f.read()})
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return docs

def format_sources(metas):
    if not metas:
        return "Sources: (none)"
    parts = [f"{m.get('source')}#chunk{m.get('chunk')}" for m in metas]
    return "Sources: " + ", ".join(parts)
