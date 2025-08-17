import argparse
from rag.pipeline import build_index, ask

def main():
    p = argparse.ArgumentParser(description="RAG over local news .txt files")
    p.add_argument("--reindex", action="store_true", help="Rebuild/append index from data dir")
    p.add_argument("--question", type=str, help="Ask a question against the index")
    p.add_argument("--n_results", type=int, default=None, help="Override retrieval depth")
    args = p.parse_args()

    if args.reindex:
        build_index()

    if args.question:
        answer, sources = ask(args.question, n_results=args.n_results or 6)
        print("\nAnswer:", answer)
        print(sources)

if __name__ == "__main__":
    main()
