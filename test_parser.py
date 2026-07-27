from pathlib import Path
from src.ingestion.markdown_parser import MarkdownParser

# Test parsing our sample architecture document
doc_path = Path("data/sample_project/01_Architecture.md")
chunks = MarkdownParser.parse_file(doc_path)

print("==================================================")
print(f"📄 Testing MarkdownParser on '{doc_path.name}'")
print(f"🧩 Chunks Generated: {len(chunks)}")
print("==================================================\n")

for c in chunks:
    chunk_data = c.to_dict()
    print(f"📌 Section Header: {chunk_data['section_header']}")
    print(f"📍 Citation Line:  {chunk_data['line_citation']} (Lines {chunk_data['start_line']} to {chunk_data['end_line']})")
    print(f"📝 Chunk Text:\n{chunk_data['text']}\n")
