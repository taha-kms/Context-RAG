# 📚 General-Purpose RAG Engine

A modular **Retrieval-Augmented Generation (RAG)** system built with:

* **ChromaDB** (vector store for embeddings)
* **OpenAI** (embeddings + LLMs)
* **Python** (clean, modular pipeline)

You can load documents in multiple formats (TXT, PDF, DOCX, MD, HTML, CSV), index them into a vector store, and ask natural-language questions. The system retrieves relevant chunks and generates concise, source-cited answers.

---

## 🚀 Features

* 📂 Multi-format document loaders (TXT, PDF, DOCX, MD, HTML, CSV)
* ✂️ Sentence-aware chunking with overlap
* 🔎 Vector search with **OpenAI embeddings**
* ⚖️ Optional **hybrid retrieval** (BM25 + vectors)
* 💬 Answer generation with **OpenAI GPT models**
* 📑 Source citations with file + chunk reference
* 🛠️ Modular design (easy to extend with other LLMs or vector stores)

---

## 📦 Project Structure

```
rag-news/ (rename to your repo name)
├─ .env.example            # Template for environment variables
├─ requirements.txt        # Python dependencies
├─ README.md               # This file
├─ data/                   # Your source documents
│   ├─ sample.txt
│   └─ ...
├─ storage/                # ChromaDB persistent storage
├─ main.py                 # CLI entrypoint
└─ rag/                    # Core library
   ├─ config.py
   ├─ loaders.py
   ├─ chunking.py
   ├─ embeddings.py
   ├─ storage.py
   ├─ retriever.py
   ├─ generator.py
   ├─ io_utils.py
   └─ pipeline.py
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/taha-kms/context-hub.git
cd context-hub.git
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI key:

```bash
OPENAI_API_KEY=sk-...
```

Optional: tweak chunk size, models, retrieval depth, hybrid mode, or request robustness (`REQUEST_TIMEOUT`, `MAX_RETRIES`, etc).

---

## 📂 Adding Documents

Place your files in the `data/` folder. Supported formats:

* `.txt`, `.md` → plain text / markdown
* `.pdf` → PDFs (text-based, not scanned images)
* `.docx` → Word docs
* `.html` → webpage exports
* `.csv` → tabular data (flattened to text rows)

You can also organize them into subfolders (e.g. `data/news/`, `data/research/`).

---

## ▶️ Usage

### Rebuild index

Index all documents in `DATA_DIR`:

```bash
python main.py --reindex
```

### Ask a question

Query the index:

```bash
python main.py --question "What did the research paper conclude?"
```

Sample output:

```
Answer: The paper concludes that hybrid retrieval improves recall by 25%.
Sources: research_paper.pdf#chunk3
⏱  1.42s  (streamed=False)
```

### Change retrieval depth

```bash
python main.py --question "What is X?" --n_results 8
```

---

## 🧪 Example Domains

Try the engine with different kinds of knowledge:

* **News articles** → “What happened in the Coinbase hack?”
* **Research PDFs** → “What is the main contribution of the paper?”
* **Tech docs** → “How do I install package X?”
* **Business reports** → “What were Q2 earnings?”
* **Policies/Legal** → “What is the penalty for violation Y?”
* **FAQs/CSV** → “What’s the refund policy?”

---

## Web App

The repository now provides a Flask-based web interface to:

- list available documents
- upload and reindex
- ask questions and view sources

Run with:

```bash
FLASK_APP=app.py flask run
# or
python app.py
```
---
## 🔧 Advanced

* Hybrid retrieval: enable with `USE_HYBRID=true` in `.env`.
* Switch models: set `CHAT_MODEL` or `EMBED_MODEL` in `.env`.

---

## 🤝 Contributing

Pull requests and issues welcome!
Ideas: add loaders, integrate new LLMs, improve evaluation.

