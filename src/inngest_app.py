import os
import inngest
from dotenv import load_dotenv

load_dotenv()

from src.ingestion import GitHubRepositoryConnector, DocumentChunk
from src.vector_store import VectorStoreManager, HybridRetriever
from src.agent import ProjectCoordinatorAgent

# Inngest Client
inngest_client = inngest.Inngest(
    app_id="projectpulse",
    is_production=False
)



@inngest_client.create_function(
    fn_id="github-repository-ingestion",
    trigger=inngest.TriggerEvent(event="projectpulse/github.ingest")
)
async def ingest_github_repository_fn(ctx: inngest.Context) -> dict:
    """Inngest background function that fetches documents from a GitHub repository and indexes them."""
    step = ctx.step
    repo_url = ctx.event.data.get("repo_url")
    if not repo_url:
        return {"status": "error", "message": "No repo_url provided in event data"}

    async def _fetch():
        connector = GitHubRepositoryConnector()
        chunks = connector.fetch_repo_documents(repo_url)
        return [
            {
                "filename": c.filename,
                "text": c.text,
                "section_header": c.section_header,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "source_type": c.source_type
            }
            for c in chunks
        ]

    chunks_data = await step.run("fetch-github-documents", _fetch)

    async def _index():
        chunks = [
            DocumentChunk(
                chunk_id=f"github_{cd['filename']}_{idx}",
                filename=cd["filename"],
                text=cd["text"],
                section_header=cd["section_header"],
                start_line=cd["start_line"],
                end_line=cd["end_line"],
                source_type=cd["source_type"]
            )
            for idx, cd in enumerate(chunks_data)
        ]
        vs = VectorStoreManager()
        vs.add_chunks(chunks)
        return {"chunks_indexed": len(chunks), "total_system_chunks": len(vs.chunks)}

    index_result = await step.run("index-vector-chunks", _index)
    return {"status": "success", "repo_url": repo_url, "details": index_result}


@inngest_client.create_function(
    fn_id="daily-project-risk-scan",
    trigger=inngest.TriggerCron(cron="0 8 * * *")
)
async def daily_risk_scan_fn(ctx: inngest.Context) -> dict:
    """Inngest background cron function that scans indexed documentation for project risks and blockers."""
    step = ctx.step
    async def _scan():
        vs = VectorStoreManager()
        retriever = HybridRetriever(vs)
        agent = ProjectCoordinatorAgent(retriever)
        risks = agent.scan_project_risks()
        return {"total_risks_found": len(risks), "risks": risks}

    scan_result = await step.run("scan-risks", _scan)
    return {"status": "success", "scan_result": scan_result}

