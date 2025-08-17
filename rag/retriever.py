from typing import List, Dict, Tuple

def dedupe_top_k(docs: List[str], metas: List[Dict], k: int = 6) -> Tuple[List[str], List[Dict]]:
    """Remove duplicates by (source,chunk), keep order, cap at k."""
    seen, out_d, out_m = set(), [], []
    for d, m in zip(docs, metas):
        key = (m.get("source"), m.get("chunk"))
        if key not in seen:
            seen.add(key)
            out_d.append(d)
            out_m.append(m)
        if len(out_d) == k:
            break
    return out_d, out_m
