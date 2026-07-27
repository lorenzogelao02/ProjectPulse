from pathlib import Path
from src.ingestion.markdown_parser import MarkdownParser
from src.db.vector_store import VectorStoreManager
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.agent import ProjectCoordinatorAgent

# 1. Initialize Pipeline
store = VectorStoreManager()
retriever = HybridRetriever(store)
agent = ProjectCoordinatorAgent(retriever)

# 2. Ingest Sample Document
doc_path = Path("data/sample_project/01_Architecture.md")
chunks = MarkdownParser.parse_file(doc_path)
store.add_chunks(chunks)

# 3. Test Hybrid Query & Citation Generation
query = "What database system was selected for ACID compliance?"
print(f"==================================================")
print(f"❓ QUERY: \"{query}\"")
print(f"==================================================")

response = agent.answer_query(query)

print(f"\n🤖 RAG ANSWER:\n{response['answer']}\n")
print("📌 CITATIONS:")
for c in response['citations']:
    print(f"   • {c['filename']} ({c['lines']}) -> Match Confidence: {c['confidence_score']}")
