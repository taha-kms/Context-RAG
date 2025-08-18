import argparse, sys
from rag.pipeline import build_index, ask
from rag.config import STREAM_ANSWERS

def main():
    p = argparse.ArgumentParser(description="RAG over local news .txt files")
    p.add_argument("--reindex", action="store_true", help="Rebuild/append index from data dir")
    p.add_argument("--question", type=str, help="Ask a question against the index")
    p.add_argument("--n_results", type=int, default=None, help="Override retrieval depth")
    p.add_argument("--stream", action="store_true", help="Stream tokens as they arrive")
    args = p.parse_args()

    if args.reindex:
        build_index()

    if args.question:
        # print tokens as they stream (if requested or env enables it)
        def _printer(tok: str):
            sys.stdout.write(tok)
            sys.stdout.flush()

        use_stream = args.stream or STREAM_ANSWERS
        answer, sources = ask(
            args.question,
            n_results=args.n_results or 6,
            stream_handler=_printer if use_stream else None
        )
        if use_stream:
            print()  # newline after final token
        print("\nAnswer:", answer)
        print(sources)

if __name__ == "__main__":
    main()
