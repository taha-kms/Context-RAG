import argparse, json, os, sys, time
from typing import Optional

from rag.pipeline import build_index, ask
from rag.config import STREAM_ANSWERS

ANSI = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "reset": "\033[0m",
}

def c(text: str, *styles: str, use_color: bool = True) -> str:
    if not use_color or not sys.stdout.isatty():
        return text
    seq = "".join(ANSI[s] for s in styles if s in ANSI)
    return f"{seq}{text}{ANSI['reset']}"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="RAG over your local documents (Chroma + OpenAI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--reindex", action="store_true", help="(Re)build/append the index from data dir")
    p.add_argument("--question", type=str, help="Ask a question against the index")
    p.add_argument("--n_results", type=int, default=6, help="Retrieval depth (top-k after de-dup)")
    p.add_argument("--data_dir", type=str, default=None, help="Override DATA_DIR for this run")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--hybrid", action="store_true", help="Enable BM25+vector hybrid (this run)")
    group.add_argument("--no-hybrid", action="store_true", help="Disable BM25 hybrid (this run)")
    p.add_argument("--stream", action="store_true", help="Stream tokens as they arrive")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON (answer, sources)")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    return p.parse_args()

def print_header(title: str, use_color: bool):
    print(c(f"\n{title}", "bold", "green", use_color=use_color))

def main():
    args = parse_args()
    use_color = not args.no_color

    # Resolve hybrid override
    hybrid_override: Optional[bool] = None
    if args.hybrid:
        hybrid_override = True
    elif args.no_hybrid:
        hybrid_override = False

    # Reindex step
    if args.reindex:
        print_header("Indexing…", use_color)
        if args.data_dir:
            print(c(f"• data_dir: {args.data_dir}", "dim", use_color=use_color))
        if hybrid_override is not None:
            print(c(f"• hybrid: {hybrid_override}", "dim", use_color=use_color))
        t0 = time.perf_counter()
        build_index(data_dir=args.data_dir, use_hybrid=hybrid_override)
        t1 = time.perf_counter()
        print(c(f"Done in {t1 - t0:.2f}s", "green", use_color=use_color))

    # Ask step
    if args.question:
        print_header("Asking…", use_color)
        print(c(f"• query: {args.question}", "dim", use_color=use_color))
        print(c(f"• top-k: {args.n_results}", "dim", use_color=use_color))
        use_stream = args.stream or STREAM_ANSWERS

        # Live token printer when streaming
        def _printer(tok: str):
            sys.stdout.write(tok)
            sys.stdout.flush()

        t0 = time.perf_counter()
        answer, sources = ask(
            args.question,
            n_results=args.n_results,
            stream_handler=_printer if use_stream else None
        )
        if use_stream:
            print()  # newline after final token
        t1 = time.perf_counter()

        if args.json:
            # Convert "Sources: a#chunk1, b#chunk2" -> list of {"source":..., "chunk":...}
            src_list = []
            if sources and sources.lower().startswith("sources:"):
                items = sources.split(":", 1)[1].strip()
                if items and items.lower() != "(none)":
                    for part in [p.strip() for p in items.split(",") if p.strip()]:
                        # expected "path#chunkN"
                        if "#chunk" in part:
                            path, chunk_str = part.split("#chunk", 1)
                            try:
                                src_list.append({"source": path, "chunk": int(chunk_str)})
                            except ValueError:
                                src_list.append({"source": path, "chunk": chunk_str})
                        else:
                            src_list.append({"source": part})
            payload = {
                "question": args.question,
                "answer": answer,
                "sources": src_list,
                "elapsed_seconds": round(t1 - t0, 3),
                "streamed": bool(use_stream),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(c("\nAnswer:", "bold", use_color=use_color), answer)
            print(c("Sources:", "bold", use_color=use_color), sources.split(":", 1)[1].strip() if ":" in sources else sources)
            print(c(f"\n⏱  {t1 - t0:.2f}s  (streamed={use_stream})", "yellow", use_color=use_color))

    if not args.reindex and not args.question:
        # Nothing to do; guide the user
        print(
            "Nothing to do. Try:\n"
            "  python main.py --reindex --data_dir data/\n"
            '  python main.py --question "What did the paper conclude?" --stream\n'
            "  python main.py --question \"What's the refund policy?\" --json"
        )

if __name__ == "__main__":
    main()
