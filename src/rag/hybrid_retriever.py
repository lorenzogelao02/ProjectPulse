from typing import List, Tuple
from src.ingestion.markdown_parser import DocumentChunk
from src.db.vector_store import VectorStoreManager

class HybridRetriever:
    """Combines Dense Vector Similarity Search with BM25 Keyword Search for high-precision retrieval."""

    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store

    def _bm25_keyword_score(self, query: str, text: str) -> float:
        """Calculates keyword match score for exact term alignment."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        if not query_words:
            return 0.0
        matches = query_words.intersection(text_words)
        return len(matches) / len(query_words)

    def retrieve(self, query: str, top_k: int = 3, dense_weight: float = 0.7) -> List[Tuple[DocumentChunk, float]]:
        """Executes hybrid retrieval combining dense vector score and sparse keyword score."""
        dense_results = self.vector_store.dense_search(query, top_k=len(self.vector_store.chunks) or 1)

        hybrid_results = []
        for chunk, dense_score in dense_results:
            bm25_score = self._bm25_keyword_score(query, chunk.text)
            
            # Combined hybrid score (70% Vector + 30% Keyword)
            combined_score = (dense_weight * dense_score) + ((1.0 - dense_weight) * bm25_score)
            hybrid_results.append((chunk, round(combined_score, 4)))

        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        return hybrid_results[:top_k]
