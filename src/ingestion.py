import io
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf


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


class PDFParser:
    """Extracts text page-by-page from PDF files and converts them into DocumentChunks."""

    @staticmethod
    def parse_pdf_file(file_path: Path) -> List[DocumentChunk]:
        """Parses a local PDF file from a disk path."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        reader = pypdf.PdfReader(file_path)
        return PDFParser._extract_chunks_from_reader(file_path.name, reader)

    @staticmethod
    def parse_pdf_bytes(filename: str, file_bytes: bytes) -> List[DocumentChunk]:
        """Parses PDF binary content directly from in-memory upload streams."""
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return PDFParser._extract_chunks_from_reader(filename, reader)

    @staticmethod
    def _extract_chunks_from_reader(filename: str, reader: pypdf.PdfReader) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                lines = text.splitlines()
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{filename}_page_{page_num}",
                        filename=filename,
                        text=text.strip(),
                        start_line=1,
                        end_line=len(lines),
                        section_header=f"Page {page_num}",
                        source_type="pdf"
                    )
                )
        return chunks


class GitHubRepositoryConnector:
    """Imports technical documentation, READMEs, and open issues from any public GitHub repository via REST API."""

    def __init__(self, github_token: str = None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ProjectPulseAI-App/1.0"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    @staticmethod
    def parse_repo_url(repo_url: str) -> Tuple[str, str]:
        """Extracts (owner, repo_name) from a GitHub URL."""
        clean_url = repo_url.strip().rstrip("/")
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]

        if "github.com/" in clean_url:
            parts = clean_url.split("github.com/")[-1].split("/")
            return parts[0], parts[1]
        elif "/" in clean_url:
            parts = clean_url.split("/")
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid GitHub repository identifier: {repo_url}")

    def fetch_repo_documents(self, repo_identifier: str) -> List[DocumentChunk]:
        """Fetches README.md and open issues from a public GitHub repository."""
        owner, repo = self.parse_repo_url(repo_identifier)
        chunks: List[DocumentChunk] = []

        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        res = requests.get(readme_url, headers=self.headers)
        
        if res.status_code == 200:
            content_data = res.json()
            download_url = content_data.get("download_url")
            if download_url:
                raw_text = requests.get(download_url, headers=self.headers).text
                lines = raw_text.splitlines()
                
                current_buffer = []
                current_section = "GitHub README"
                start_line = 1

                for idx, line in enumerate(lines, start=1):
                    if line.startswith("#"):
                        current_section = line.lstrip("#").strip()
                    current_buffer.append(line)
                    
                    if len("\n".join(current_buffer)) >= 600 or (line.startswith("## ") and len(current_buffer) > 4):
                        chunk_text = "\n".join(current_buffer).strip()
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"github_{repo}_readme_{len(chunks)+1}",
                                filename=f"GitHub: {owner}/{repo}/README.md",
                                text=chunk_text,
                                start_line=start_line,
                                end_line=idx,
                                section_header=current_section,
                                source_type="github_api"
                            )
                        )
                        current_buffer = []
                        start_line = idx + 1

                if current_buffer:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"github_{repo}_readme_{len(chunks)+1}",
                            filename=f"GitHub: {owner}/{repo}/README.md",
                            text="\n".join(current_buffer).strip(),
                            start_line=start_line,
                            end_line=len(lines),
                            section_header=current_section,
                            source_type="github_api"
                        )
                    )

        issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=5"
        issues_res = requests.get(issues_url, headers=self.headers)
        if issues_res.status_code == 200:
            issues = issues_res.json()
            for issue in issues:
                if "pull_request" in issue:
                    continue
                title = issue.get("title", "")
                body = issue.get("body", "") or ""
                issue_number = issue.get("number")
                
                chunk_text = f"Issue #{issue_number}: {title}\n{body[:350]}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"github_{repo}_issue_{issue_number}",
                        filename=f"GitHub: {owner}/{repo}/Issue #{issue_number}",
                        text=chunk_text.strip(),
                        start_line=1,
                        end_line=10,
                        section_header=f"Issue #{issue_number}",
                        source_type="github_api"
                    )
                )

        return chunks
