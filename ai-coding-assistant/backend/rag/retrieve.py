"""
RAG Retriever - Queries the FAISS index to retrieve relevant code chunks.
"""

import os
import json
import logging
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

VECTOR_STORE_DIR = Path("data/vector_store")
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


class Retriever:
    """
    Retrieves relevant code chunks from the FAISS vector store.
    Lazy-loads the index on first query.
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._index = None
        self._metadata = None

    def _load_index(self):
        """Load FAISS index and metadata from disk if not already loaded."""
        if self._index is not None:
            return

        if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
            raise FileNotFoundError(
                "Vector store not found. Please ingest a codebase first via /api/upload_codebase."
            )

        logger.info("Loading FAISS index from disk...")
        self._index = faiss.read_index(str(FAISS_INDEX_PATH))

        with open(METADATA_PATH, "r") as f:
            self._metadata = json.load(f)

        logger.info(f"Index loaded: {self._index.ntotal} vectors")

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string."""
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query],
        )
        return np.array([response.data[0].embedding], dtype=np.float32)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve the top-k most relevant code chunks for a query.

        Args:
            query: User's natural language query.
            top_k: Number of results to return.

        Returns:
            List of dicts with 'content', 'source', 'score'.
        """
        self._load_index()

        query_embedding = self.embed_query(query)
        distances, indices = self._index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._metadata):
                continue
            chunk = self._metadata[idx]
            results.append({
                "content": chunk["content"],
                "source": chunk["source"],
                "chunk_index": chunk.get("chunk_index", 0),
                "score": float(dist),
            })

        logger.info(f"Retrieved {len(results)} chunks for query")
        return results

    def reload(self):
        """Force reload of the index (called after new ingestion)."""
        self._index = None
        self._metadata = None
        logger.info("Retriever cache cleared, will reload on next query")


# Singleton instance
retriever = Retriever()
