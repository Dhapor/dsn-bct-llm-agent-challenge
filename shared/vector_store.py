"""
Lightweight FAISS-based vector store for item retrieval in Task B.
Encodes items with sentence-transformers and retrieves nearest neighbors.
Falls back to keyword search if FAISS is unavailable.
"""

from __future__ import annotations
import json
import os
from typing import Any

try:
    import faiss
    import numpy as np
    from fastembed import TextEmbedding
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class ItemVectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.items: list[dict[str, Any]] = []
        self.model_name = model_name
        self._model = None
        self._index = None

    def _get_model(self):
        if self._model is None and FAISS_AVAILABLE:
            self._model = TextEmbedding(self.model_name)
        return self._model

    def _item_to_text(self, item: dict[str, Any]) -> str:
        parts = [
            item.get("name", ""),
            item.get("category", ""),
            item.get("description", ""),
            " ".join(item.get("tags", [])),
            item.get("cuisine", ""),
        ]
        return " ".join(p for p in parts if p)

    def add_items(self, items: list[dict[str, Any]]) -> None:
        self.items = items
        if not FAISS_AVAILABLE or not items:
            return
        model = self._get_model()
        texts = [self._item_to_text(item) for item in items]
        embeddings = np.array(list(model.embed(texts)), dtype="float32")
        faiss.normalize_L2(embeddings)
        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings)

    def search(self, query: str, top_k: int = 20, category_filter: str | None = None) -> list[dict[str, Any]]:
        candidates = self.items
        if category_filter:
            candidates = [i for i in candidates if category_filter.lower() in i.get("category", "").lower()]

        if not candidates:
            candidates = self.items

        if FAISS_AVAILABLE and self._index is not None:
            return self._faiss_search(query, top_k, candidates)
        return self._keyword_search(query, top_k, candidates)

    def _faiss_search(self, query: str, top_k: int, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        import numpy as np
        model = self._get_model()
        q_emb = np.array(list(model.embed([query])), dtype="float32")
        faiss.normalize_L2(q_emb)

        # Search full index, then filter to candidates
        k = min(top_k * 3, len(self.items))
        scores, indices = self._index.search(q_emb, k)
        candidate_ids = {id(c) for c in candidates}

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.items):
                item = self.items[idx]
                if id(item) in candidate_ids or len(results) < top_k:
                    results.append({**item, "_score": float(score)})
                    if len(results) >= top_k:
                        break
        return results

    def _keyword_search(self, query: str, top_k: int, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []
        for item in candidates:
            text = self._item_to_text(item).lower()
            score = sum(1 for w in query_words if w in text)
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def load_from_file(self, path: str) -> None:
        with open(path) as f:
            items = json.load(f)
        self.add_items(items)

    def get_by_category(self, category: str, limit: int = 50) -> list[dict[str, Any]]:
        return [i for i in self.items if category.lower() in i.get("category", "").lower()][:limit]
