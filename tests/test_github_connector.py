import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.github_connector import GitHubRepositoryConnector

# Test fetching real documentation from a public GitHub repo (e.g., fastapi/fastapi)
connector = GitHubRepositoryConnector()

repo_identifier = "fastapi/fastapi"
print(f"==================================================")
print(f"[GitHub API Test] Connecting to '{repo_identifier}'")
print(f"==================================================")

chunks = connector.fetch_repo_documents(repo_identifier)

print(f"\n[Total Chunks Received: {len(chunks)}]\n")

for idx, c in enumerate(chunks[:5], start=1):
    chunk_data = c.to_dict()
    print(f"--- CHUNK #{idx} ---")
    print(f"File:        {chunk_data['filename']}")
    print(f"Section:     {chunk_data['section_header']}")
    print(f"Source Type: {chunk_data['source_type']}")
    print(f"Text Excerpt:\n{chunk_data['text'][:150]}...\n")
