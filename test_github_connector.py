from src.ingestion.github_connector import GitHubRepositoryConnector

# Test fetching real documentation from a public GitHub repo (e.g., fastapi/fastapi)
connector = GitHubRepositoryConnector()

# Test repo: "fastapi/fastapi"
repo_identifier = "fastapi/fastapi"
print(f"==================================================")
print(f"🐙 Testing GitHub API Connector on '{repo_identifier}'")
print(f"==================================================\n")

chunks = connector.fetch_repo_documents(repo_identifier)

print(f"\n🧩 Total Chunks Received: {len(chunks)}\n")

for idx, c in enumerate(chunks, start=1):
    chunk_data = c.to_dict()
    print(f"--- CHUNK #{idx} ---")
    print(f"📄 File:        {chunk_data['filename']}")
    print(f"📌 Section:     {chunk_data['section_header']}")
    print(f"📍 Source Type: {chunk_data['source_type']}")
    print(f"📝 Text Excerpt:\n{chunk_data['text'][:150]}...\n")
