
# ⚡ ProjectPulse AI
 
> 🚧 **Work in Progress** — A personal project to learn how RAG systems work and which technologies fit together: hybrid retrieval, event-driven background workflows and AI project co-pilots.
 
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Inngest](https://img.shields.io/badge/Orchestration-Inngest-000000.svg)](https://www.inngest.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq_LLaMA_3.3-orange.svg)](https://groq.com/)
  
---
 
## 💡 About The Project
 
**ProjectPulse AI** is a co-pilot for technical projects. Instead of searching through scattered Markdown docs, GitHub READMEs, issues or PDFs, it indexes your project documentation, gives cited answers with line numbers, and flags potential risks or blockers.
 
**How it was built:** I designed the architecture and chose the components, and built it with AI-assisted development (Claude), reviewing and testing the generated code along the way.
 
---
 
## 🌟 Key Features
 
- **💬 Interactive Streamlit Dashboard:** Q&A chat assistant with line-number citations and confidence scores.
- **📄 Multi-Format Document Ingestion:** Drag-and-drop support for **PDFs** (`pypdf`), **Markdown files** and **GitHub repositories** (fetches READMEs and open issues via the REST API).
- **🔍 Hybrid Search:** Combines **dense vector embeddings** (`sentence-transformers/all-MiniLM-L6-v2`) with **sparse keyword matching** (BM25).
- **⚙️ Event-Driven Orchestration with Inngest:** Background processing for heavy repository ingestion, retries and daily automated risk scans.
- **⚡ LLM via Groq Cloud:** Default integration with Groq's `llama-3.3-70b-versatile`, with OpenAI `gpt-4o-mini` and local fallback support.
- **⚠️ Project Risk Radar:** Scans indexed documentation for dependency bottlenecks, unassigned blockers and architecture conflicts.
---
 
## 🏗️ Architecture
 
```text
               +----------------------------------+
               |     Streamlit Dashboard (app.py) |
               +----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
|                   ProjectPulse Core (src/)                       |
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
 
## 🧪 What I Explored
 
This project was a hands-on way to try the pieces of a RAG system. I picked tools out of curiosity, not after a formal comparison.
 
- **Hybrid search (dense + BM25):** I wanted to see how semantic search and keyword search behave differently on the same documents.
- **Inngest:** I came across it in a video and used the project to try event-driven workflows, with background ingestion and retries.
- **Groq (LLaMA 3.3):** free API keys and fast responses made it easy to experiment. OpenAI and local options are available as fallbacks.
- **Cited answers with confidence scores:** I wanted answers that can be checked against the source.
 
---
 
## 🛠️ Tech Stack
 
- **UI & Web:** Streamlit, FastAPI, Uvicorn
- **LLM & Embeddings:** Groq Cloud (`llama-3.3-70b`), OpenAI (`gpt-4o-mini`), SentenceTransformers (`all-MiniLM-L6-v2`)
- **Search & Vector Storage:** ChromaDB, BM25 (`rank-bm25`)
- **Workflow Orchestration:** Inngest (background tasks & cron functions)
- **Document Parsers:** `pypdf`, GitHub REST API, Markdown line parser
- **Package Management:** `pyproject.toml` / `uv`
---
 
## 🚀 Quickstart
 
### 1. Clone the repo & set up `.env`
```bash
git clone https://github.com/lorenzogelao02/ProjectPulse.git
cd ProjectPulse
```
 
Create a `.env` file at the project root (it is git-ignored, never commit it):
```env
GROQ_API_KEY=gsk_your_groq_key_here
# Optional:
# OPENAI_API_KEY=sk-your-openai-key
# INNGEST_EVENT_KEY=your_inngest_event_key
# INNGEST_SIGNING_KEY=your_inngest_signing_key
```
 
### 2. Install dependencies
Using `uv` (recommended):
```bash
uv sync
```
Or using standard `pip`:
```bash
pip install -e .
```
 
### 3. Launch the Streamlit UI
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.
 
### 4. (Optional) Run the FastAPI & Inngest background worker
```bash
python api.py
```
The FastAPI server runs on **`http://localhost:8000`** (Swagger docs at `/docs`).
 
---
 
## 📂 Project Structure
 
```text
ProjectPulse/
├── .env                  # Create locally: API keys (git-ignored)
├── pyproject.toml        # uv / package configuration
├── app.py                # Streamlit UI dashboard
├── api.py                # FastAPI REST server & Inngest endpoint
├── src/
│   ├── config.py         # Directory paths & settings
│   ├── ingestion.py      # PDF, Markdown & GitHub parsers
│   ├── vector_store.py   # VectorStoreManager & hybrid (dense + BM25) retriever
│   ├── agent.py          # ProjectCoordinatorAgent (Groq/OpenAI Q&A + risk scanner)
│   └── inngest_app.py    # Inngest client & background workflow functions
├── tests/                # Tests
└── data/
    └── sample_project/   # Sample project docs
```
 
---
 
## 📌 Status
 
This is an ongoing personal project built for learning. Features are still being added and tweaked.
