

def format_sources(metas):
    if not metas:
        return "Sources: (none)"
    parts = [f"{m.get('source')}#chunk{m.get('chunk')}" for m in metas]
    return "Sources: " + ", ".join(parts)
