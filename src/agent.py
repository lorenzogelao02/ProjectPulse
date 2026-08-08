import os
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

from src.ingestion import DocumentChunk
from src.vector_store import HybridRetriever


class ProjectCoordinatorAgent:
    """AI Project Coordinator Agent providing contextual Q&A with citations and automated risk detection."""

    def __init__(self, retriever: HybridRetriever, openai_api_key: str = None, groq_api_key: str = None):
        self.retriever = retriever
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

    def answer_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Runs hybrid search and synthesizes a cited answer using LLM (Groq / OpenAI / Local Fallback)."""
        retrieved_results = self.retriever.retrieve(query, top_k=top_k)
        if not retrieved_results:
            return {
                "query": query,
                "answer": "No relevant project documentation found.",
                "citations": []
            }

        citations = []
        context_snippets = []

        for chunk, score in retrieved_results:
            citations.append({
                "filename": chunk.filename,
                "lines": f"L{chunk.start_line}-L{chunk.end_line}",
                "section": chunk.section_header,
                "confidence_score": score,
                "source_type": chunk.source_type
            })
            context_snippets.append(
                f"--- SOURCE: {chunk.filename} (Lines L{chunk.start_line}-L{chunk.end_line}) ---\n{chunk.text}\n"
            )

        context_str = "\n".join(context_snippets)

        prompt = (
            "You are ProjectPulse AI, an intelligent technical project co-pilot.\n"
            "Answer the user's question using ONLY the provided project context below.\n"
            "Include exact file names and line numbers as citations.\n\n"
            f"=== CONTEXT DOCUMENTS ===\n{context_str}\n=========================\n\n"
            f"USER QUESTION: {query}"
        )

        if self.groq_api_key:
            try:
                import openai
                client = openai.OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=self.groq_api_key
                )
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                answer_text = res.choices[0].message.content
            except Exception as e:
                print(f"Groq API call error: {e}")
                answer_text = self._synthesize_local_answer(query, retrieved_results)
        elif self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                answer_text = res.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API call error: {e}")
                answer_text = self._synthesize_local_answer(query, retrieved_results)
        else:
            answer_text = self._synthesize_local_answer(query, retrieved_results)

        return {
            "query": query,
            "answer": answer_text,
            "citations": citations
        }

    def _synthesize_local_answer(self, query: str, retrieved_results: List[Tuple[DocumentChunk, float]]) -> str:
        top_chunk, score = retrieved_results[0]
        return (
            f"Based on **{top_chunk.filename}** (Lines L{top_chunk.start_line}-L{top_chunk.end_line}):\n\n"
            f"> \"{top_chunk.text.strip()}\"\n\n"
            f"📌 **Citation:** Section *{top_chunk.section_header}* ({top_chunk.filename}, lines L{top_chunk.start_line}-L{top_chunk.end_line}, confidence score: {score})."
        )

    def scan_project_risks(self) -> List[Dict[str, Any]]:
        """Scans indexed documents for potential project risks, contradictions, or unassigned blockers."""
        risks = []
        all_chunks = self.retriever.vector_store.chunks

        for c in all_chunks:
            lower_text = c.text.lower()
            if "blocker" in lower_text or "critical" in lower_text or "risk" in lower_text:
                risks.append({
                    "risk_type": "Dependency / Blocker Risk",
                    "source": c.filename,
                    "lines": f"L{c.start_line}-L{c.end_line}",
                    "summary": c.text[:200]
                })
            elif "select for update" in lower_text or "lock" in lower_text:
                risks.append({
                    "risk_type": "Database Concurrency Decision",
                    "source": c.filename,
                    "lines": f"L{c.start_line}-L{c.end_line}",
                    "summary": c.text[:200]
                })

        return risks
