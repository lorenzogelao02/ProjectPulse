from pathlib import Path
from typing import List, Dict, Any

class DocumentChunk:
    """Stores a single chunk of project text with line range citations and source metadata."""

    def __init__(
        self,
        chunk_id: str,
        filename: str,
        text: str,
        start_line: int,
        end_line: int,
        section_header: str = "",
        source_type: str = "markdown"
    ):
        self.chunk_id = chunk_id
        self.filename = filename
        self.text = text
        self.start_line = start_line
        self.end_line = end_line
        self.section_header = section_header
        self.source_type = source_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "filename": self.filename,
            "text": self.text,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "line_citation": f"L{self.start_line}-L{self.end_line}",
            "section_header": self.section_header,
            "source_type": self.source_type
        }

class MarkdownParser:
    """Parses Markdown technical documents into structured chunks with line citations."""

    @staticmethod
    def parse_file(file_path: Path, max_chars: int = 500) -> List[DocumentChunk]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        lines = file_path.read_text(encoding="utf-8").splitlines()
        chunks: List[DocumentChunk] = []

        current_section = "General"
        current_buffer = []
        start_line = 1

        for idx, line in enumerate(lines, start=1):
            if line.startswith("#"):
                current_section = line.lstrip("#").strip()

            current_buffer.append(line)
            current_text = "\n".join(current_buffer)

            if len(current_text) >= max_chars or (line.startswith("## ") and len(current_buffer) > 3):
                chunk_id = f"{file_path.name}_{len(chunks) + 1}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        filename=file_path.name,
                        text=current_text.strip(),
                        start_line=start_line,
                        end_line=idx,
                        section_header=current_section,
                        source_type="markdown"
                    )
                )
                current_buffer = []
                start_line = idx + 1

        if current_buffer:
            chunk_id = f"{file_path.name}_{len(chunks) + 1}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    filename=file_path.name,
                    text="\n".join(current_buffer).strip(),
                    start_line=start_line,
                    end_line=len(lines),
                    section_header=current_section,
                    source_type="markdown"
                )
            )

        return chunks
