from __future__ import annotations

from hashlib import blake2b
from pathlib import Path
from typing import Any

import numpy as np

from app.config import settings


class HashEmbeddingFunction:
    """Small deterministic embedding function so local setup needs no model download."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    @staticmethod
    def name() -> str:
        return "memory_tutor_hash_embedding"

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> "HashEmbeddingFunction":
        return HashEmbeddingFunction(dimensions=int(config.get("dimensions", 384)))

    @staticmethod
    def validate_config(config: dict[str, Any]) -> None:
        if int(config.get("dimensions", 384)) < 32:
            raise ValueError("Embedding dimensions must be at least 32")

    def get_config(self) -> dict[str, Any]:
        return {"dimensions": self.dimensions}

    def default_space(self) -> str:
        return "cosine"

    def supported_spaces(self) -> list[str]:
        return ["cosine", "l2", "ip"]

    def is_legacy(self) -> bool:
        return False

    def __call__(self, input):
        return [self._embed(document) for document in input]

    def embed_query(self, input):
        return self.__call__(input)

    def _embed(self, document: str):
        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = [token for token in document.lower().replace("-", " ").split() if token]
        for token in tokens:
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()


class VectorStore:
    def __init__(self, path: Path | None = None):
        self.path = path or settings.chroma_dir
        self.path.mkdir(parents=True, exist_ok=True)
        self.available = False
        self.collection = None
        self.embedding_function = HashEmbeddingFunction()
        self.error: str | None = None
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(self.path))
            self.collection = client.get_or_create_collection(
                name="memory_tutor_memories",
                embedding_function=self.embedding_function,
                metadata={"embedding": "deterministic_hash_384"},
            )
            self.available = True
        except Exception as exc:
            self.error = str(exc)

    def upsert_memory(self, memory_id: int, text: str, metadata: dict[str, Any]) -> str:
        vector_id = f"memory_{memory_id}"
        if not self.available or self.collection is None:
            return vector_id
        safe_metadata = {
            key: ("" if value is None else value)
            for key, value in metadata.items()
        }
        self.collection.upsert(
            ids=[vector_id],
            documents=[text],
            metadatas=[safe_metadata],
        )
        return vector_id

    def query(
        self,
        user_id: int,
        query_text: str,
        top_k: int = 5,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.available or self.collection is None or not query_text.strip():
            return []
        where: dict[str, Any] = {"user_id": str(user_id), "status": "active"}
        if topic:
            where = {"$and": [where, {"topic_tag": topic}]}
        try:
            result = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where,
                include=["distances", "metadatas", "documents"],
            )
        except Exception:
            return []
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        documents = result.get("documents", [[]])[0]
        matches = []
        for index, vector_id in enumerate(ids):
            distance = float(distances[index]) if index < len(distances) else 1.0
            matches.append(
                {
                    "vector_id": vector_id,
                    "memory_id": int(str(vector_id).replace("memory_", "")),
                    "score": max(0.0, 1.0 - distance),
                    "metadata": metadatas[index] if index < len(metadatas) else {},
                    "document": documents[index] if index < len(documents) else "",
                }
            )
        return matches

    def delete_memory(self, memory_id: int) -> None:
        if not self.available or self.collection is None:
            return
        try:
            self.collection.delete(ids=[f"memory_{memory_id}"])
        except Exception:
            return


vector_store = VectorStore()

