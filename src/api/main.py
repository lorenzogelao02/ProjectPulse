from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from src.ingestion.markdown_parser import MarkdownParser
from src.ingestion.github_connector import GitHubRepositoryConnector
from src.db.vector_store import VectorStoreManager
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.agent import ProjectCoordinatorAgent

app = FastAPI(
    title="ProjectPulse AI API",
    description="AI-Driven Project Coordination & RAG Workspace Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store = VectorStoreManager()
retriever = HybridRetriever(vector_store)
agent = ProjectCoordinatorAgent(retriever)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class GitHubIngestRequest(BaseModel):
    repo_url: str

@app.on_event("startup")
def auto_index_sample_project():
    """Auto-indexes sample Markdown files on server startup."""
    print("[ProjectPulse AI] Initializing production engine...")
    sample_file = Path("data/sample_project/01_Architecture.md")
    if sample_file.exists():
        chunks = MarkdownParser.parse_file(sample_file)
        vector_store.add_chunks(chunks)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "ProjectPulse AI Production Engine",
        "total_chunks_indexed": len(vector_store.chunks)
    }

@app.get("/api/documents")
def list_documents():
    """Returns registry of indexed files, chunk counts, and data source types."""
    doc_registry = {}
    for chunk in vector_store.chunks:
        if chunk.filename not in doc_registry:
            doc_registry[chunk.filename] = {
                "filename": chunk.filename,
                "chunk_count": 0,
                "source_type": chunk.source_type
            }
        doc_registry[chunk.filename]["chunk_count"] += 1

    return {"documents": list(doc_registry.values()), "total_chunks": len(vector_store.chunks)}

@app.post("/api/query")
def process_rag_query(request: QueryRequest):
    """Runs hybrid vector + sparse search and synthesizes cited answer."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    return agent.answer_query(request.query, top_k=request.top_k)

@app.post("/api/ingest/github")
def ingest_github_repository(request: GitHubIngestRequest):
    """Fetches and indexes README and issues from any public GitHub repository URL via API."""
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="GitHub repository URL cannot be empty.")

    try:
        connector = GitHubRepositoryConnector()
        chunks = connector.fetch_repo_documents(request.repo_url)
        vector_store.add_chunks(chunks)
        return {
            "status": "success",
            "repo_url": request.repo_url,
            "chunks_added": len(chunks),
            "total_system_chunks": len(vector_store.chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest GitHub repository: {str(e)}")

@app.get("/api/risks")
def scan_project_risks():
    """Scans project documentation for risks, dependency bottlenecks, or decision conflicts."""
    risks = agent.scan_project_risks()
    return {"risks": risks, "total_risks_found": len(risks)}

# Serve Web Frontend Dashboard if available
web_dir = Path("web")
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")

@app.get("/")
def serve_index():
    index_file = Path("web/index.html")
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "ProjectPulse AI API v2.0 is running. Visit /docs for API documentation."}
