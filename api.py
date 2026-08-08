import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import inngest
import inngest.fast_api

from src.config import DATA_DIR
from src.ingestion import MarkdownParser, GitHubRepositoryConnector
from src.vector_store import VectorStoreManager, HybridRetriever
from src.agent import ProjectCoordinatorAgent
from src.inngest_app import inngest_client, ingest_github_repository_fn, daily_risk_scan_fn

app = FastAPI(
    title="ProjectPulse AI API",
    description="AI-Driven Project Coordination & Production RAG API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Inngest background workflow endpoint
inngest.fast_api.serve(
    app,
    inngest_client,
    [ingest_github_repository_fn, daily_risk_scan_fn],
    serve_path="/api/inngest"
)

# Global Instances
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
    sample_dir = DATA_DIR / "sample_project"
    if sample_dir.exists():
        for file_path in sample_dir.glob("*.md"):
            chunks = MarkdownParser.parse_file(file_path)
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
async def ingest_github_repository(request: GitHubIngestRequest):
    """Triggers an Inngest background event to fetch and index GitHub repo documents asynchronously."""
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="GitHub repository URL cannot be empty.")

    try:
        await inngest_client.send(
            inngest.Event(
                name="projectpulse/github.ingest",
                data={"repo_url": request.repo_url}
            )
        )
        return {
            "status": "queued",
            "message": "GitHub repository ingestion triggered in background via Inngest workflow.",
            "repo_url": request.repo_url
        }
    except Exception:
        connector = GitHubRepositoryConnector()
        chunks = connector.fetch_repo_documents(request.repo_url)
        vector_store.add_chunks(chunks)
        return {
            "status": "success",
            "repo_url": request.repo_url,
            "chunks_added": len(chunks),
            "total_system_chunks": len(vector_store.chunks)
        }


@app.get("/api/risks")
def scan_project_risks():
    """Scans project documentation for risks, dependency bottlenecks, or decision conflicts."""
    risks = agent.scan_project_risks()
    return {"risks": risks, "total_risks_found": len(risks)}


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["src"])

