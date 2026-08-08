import math
from typing import List, Tuple
from src.config import EMBEDDING_MODEL_NAME
from src.ingestion import DocumentChunk


class VectorStoreManager:
    """Manages vector embeddings and similarity search index for project chunks."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[List[float]] = []
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            except Exception:
                self._model = "fallback"
        return self._model

    def _embed_text(self, text: str) -> List[float]:
        """Converts text into a vector embedding."""
        model = self._get_model()
        if model != "fallback":
            return model.encode(text).tolist()
        else:
            words = text.lower().split()
            vec = [0.0] * 64
            for w in words:
                vec[abs(hash(w)) % 64] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            return [x / norm for x in vec]

    def add_chunks(self, chunks: List[DocumentChunk]):
        """Indexes DocumentChunk objects into vector storage."""
        for chunk in chunks:
            if not chunk.text.strip():
                continue
            emb = self._embed_text(chunk.text)
            self.chunks.append(chunk)
            self.embeddings.append(emb)

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def dense_search(self, query: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """Performs vector similarity search against indexed chunks."""
        if not self.chunks:
            return []

        query_emb = self._embed_text(query)
        scored_results = []

        for chunk, emb in zip(self.chunks, self.embeddings):
            score = self._cosine_similarity(query_emb, emb)
            scored_results.append((chunk, score))

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]


class HybridRetriever:
    """Combines Dense Vector Similarity Search with BM25 Keyword Search for high-precision retrieval."""

    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store

    def _bm25_keyword_score(self, query: str, text: str) -> float:
        """Calculates keyword match score for term alignment."""
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
            combined_score = (dense_weight * dense_score) + ((1.0 - dense_weight) * bm25_score)
            hybrid_results.append((chunk, round(combined_score, 4)))

        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        return hybrid_results[:top_k]
