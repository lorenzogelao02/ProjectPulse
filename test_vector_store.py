from pathlib import Path
from src.ingestion.markdown_parser import MarkdownParser
from src.db.vector_store import VectorStoreManager

# 1. Initialize Vector Store
store = VectorStoreManager()

# 2. Ingest local sample document
doc_path = Path("data/sample_project/01_Architecture.md")
chunks = MarkdownParser.parse_file(doc_path)
store.add_chunks(chunks)

# 3. Test Vector Search
query = "What database system was selected for ACID compliance?"
print(f"\n==================================================")
print(f"❓ QUERY: \"{query}\"")
print(f"==================================================")

results = store.dense_search(query, top_k=2)

for idx, (chunk, score) in enumerate(results, start=1):
    print(f"\n🎯 MATCH #{idx} (Score: {score:.4f})")
    print(f"📄 File:     {chunk.filename}")
    print(f"📍 Citation: L{chunk.start_line}-L{chunk.end_line}")
    print(f"📝 Text:\n{chunk.text}")
