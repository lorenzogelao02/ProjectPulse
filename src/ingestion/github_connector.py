import requests
from typing import List
from src.ingestion.markdown_parser import DocumentChunk

class GitHubRepositoryConnector:
    """Imports technical documentation, READMEs, and open issues from any public GitHub repository via REST API."""

    def __init__(self, github_token: str = None):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple:
        """Extracts (owner, repo_name) from a GitHub URL or string like 'owner/repo'."""
        clean_url = repo_url.strip().rstrip("/")
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
        print(f"[GitHub API] Fetching documentation from: {owner}/{repo}...")

        chunks: List[DocumentChunk] = []

        # 1. Fetch README.md
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        res = requests.get(readme_url, headers=self.headers)
        
        if res.status_code == 200:
            content_data = res.json()
            download_url = content_data.get("download_url")
            if download_url:
                raw_text = requests.get(download_url).text
                lines = raw_text.splitlines()
                
                chunk_id = f"github_{repo}_readme"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        filename=f"GitHub: {owner}/{repo}/README.md",
                        text=raw_text[:800].strip(),
                        start_line=1,
                        end_line=min(30, len(lines)),
                        section_header="GitHub Repository README",
                        source_type="github_api"
                    )
                )

        # 2. Fetch Open Issues (Top 5 recent issues)
        issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=5"
        issues_res = requests.get(issues_url, headers=self.headers)
        if issues_res.status_code == 200:
            issues = issues_res.json()
            for idx, issue in enumerate(issues, start=1):
                title = issue.get("title", "")
                body = issue.get("body", "") or ""
                issue_number = issue.get("number")
                
                chunk_text = f"Issue #{issue_number}: {title}\n{body[:300]}"
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

        print(f"[GitHub API] Extracted {len(chunks)} document chunks from repo {owner}/{repo}.")
        return chunks
