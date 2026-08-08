# ⚡ ProjectPulse AI

> 🚧 **Work in Progress (WIP)** — A fun side-project for experimenting with production RAG architectures, event-driven background workflows, and AI project co-pilots.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Inngest](https://img.shields.io/badge/Orchestration-Inngest-000000.svg)](https://www.inngest.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq_LLaMA_3.3-orange.svg)](https://groq.com/)

---

## 💡 About The Project

**ProjectPulse AI** is a personal playground project built to explore how to create an intelligent co-pilot for technical projects. 

Instead of searching through scattered Markdown docs, GitHub READMEs, issues, or PDFs, ProjectPulse indexes your codebase documentation, provides cited answers with line numbers, and automatically alerts you to potential risks or blockers.

---

## 🌟 Key Features

- **💬 Interactive Streamlit Dashboard:** Instant Q&A chat assistant with exact line-number citations and confidence scores.
- **📄 Multi-Format Document Ingestion:** Drag-and-drop support for **PDFs** (`pypdf`), **Markdown files**, and **GitHub Repositories** (fetches READMEs and open issues via REST API).
- **🔍 Hybrid Search Engine:** Combines **Dense Vector Embeddings** (`sentence-transformers/all-MiniLM-L6-v2`) with **Sparse Keyword Matching** (BM25) for high retrieval precision.
- **⚙️ Event-Driven Orchestration with Inngest:** Background task processing for heavy repository ingestion, retries, and daily automated risk scanning.
- **⚡ Ultra-Fast LLM Powered by Groq Cloud:** Default integration with Groq's `llama-3.3-70b-versatile` (with OpenAI `gpt-4o-mini` & local fallback support).
- **⚠️ Automated Project Risk Radar:** Scans indexed documentation for dependency bottlenecks, unassigned blockers, and architecture conflicts.

---

## 🏗️ Architecture

```text
               +----------------------------------+
               |     Streamlit Dashboard (app.py) |
               +----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
|                   ProjectPulse Core (src/)                      |
|                                                                  |
|  +--------------------+   +-------------------+  +------------+  |
|  |    Ingestion       |   |   Vector Store    |  | RAG Agent  |  |
|  | PDF / MD / GitHub  | ->| VectorStore + BM25|->| Groq/OpenAI|  |
|  +--------------------+   +-------------------+  +------------+  |
+------------------------------------------------------------------+
                                ^
                                |
               +----------------------------------+
               |   FastAPI & Inngest (api.py)     |
               +----------------------------------+
```

---

## 🛠️ Tech Stack

- **UI & Web:** Streamlit, FastAPI, Uvicorn
- **LLM & Embeddings:** Groq Cloud (`llama-3.3-70b`), OpenAI (`gpt-4o-mini`), SentenceTransformers (`all-MiniLM-L6-v2`)
- **Search & Vector Storage:** ChromaDB (Vector Store), BM25 (`rank-bm25`)
- **Workflow Orchestration:** Inngest (Background tasks & cron functions)
- **Document Parsers:** `pypdf`, GitHub REST API, Markdown Line Parser
- **Package Management:** `pyproject.toml` / `uv`

---

## 🚀 Quickstart

### 1. Clone the repo & setup `.env`
```bash
git clone https://github.com/your-username/RAG_Job.git
cd RAG_Job
```

Create a `.env` file at root:
```env
GROQ_API_KEY=gsk_your_groq_key_here
# Optional:
# OPENAI_API_KEY=sk-your-openai-key
# INNGEST_EVENT_KEY=your_inngest_event_key
# INNGEST_SIGNING_KEY=your_inngest_signing_key
```

### 2. Install Dependencies
Using `uv` (recommended):
```bash
uv sync
```
Or using standard `pip`:
```bash
pip install -e .
```

### 3. Launch Streamlit UI
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser!

### 4. (Optional) Run FastAPI & Inngest Background Worker
```bash
python api.py
```
FastAPI server runs on **`http://localhost:8000`** (Swagger docs at `/docs`).

---

## 📂 Project Structure

```text
RAG_Job/
├── .env                  # API keys (Groq, Inngest, OpenAI)
├── pyproject.toml        # uv / package configuration
├── app.py                # Streamlit UI dashboard
├── api.py                # FastAPI REST server & Inngest endpoint
├── src/
│   ├── config.py         # Directory paths & settings
│   ├── ingestion.py      # PDF, Markdown & GitHub parsers
│   ├── vector_store.py   # VectorStoreManager & Hybrid (Dense + BM25) Retriever
│   ├── agent.py          # ProjectCoordinatorAgent (Groq/OpenAI Q&A + Risk Scanner)
│   └── inngest_app.py    # Inngest client & background workflow functions
└── data/                 # Sample project benchmark docs
```

---

## 📌 Disclaimer
This is an ongoing personal experiment built for fun and learning. Features are actively being added and tweaked!
