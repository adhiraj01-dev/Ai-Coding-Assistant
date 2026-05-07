"""
RAG Ingest - Loads a codebase, chunks it, embeds it, and stores in FAISS.
"""

import os
import json
import logging
import pickle
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

from utils.file_loader import iter_code_files
from utils.chunker import chunk_code

load_dotenv()
logger = logging.getLogger(__name__)

VECTOR_STORE_DIR = Path("data/vector_store")
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

FAISS_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


class CodebaseIngestor:
    """
    Ingests a code project into a FAISS vector store.
    Each chunk is embedded and stored with its source metadata.
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index = None
        self.metadata = []  # list of {content, source, chunk_index}

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Embed a batch of texts using OpenAI's embedding model.

        Returns:
            NumPy array of shape (N, EMBEDDING_DIM).
        """
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype=np.float32)

    def ingest(self, project_dir: str) -> dict:
        """
        Ingest all code files from a project directory.

        Args:
            project_dir: Path to the root of the project.

        Returns:
            Summary dict with file count, chunk count, and status.
        """
        logger.info(f"Starting ingestion of: {project_dir}")
        all_chunks = []

        file_count = 0
        for filepath, content in iter_code_files(project_dir):
            chunks = chunk_code(content, source=filepath)
            all_chunks.extend(chunks)
            file_count += 1
            logger.debug(f"Processed: {filepath} ({len(chunks)} chunks)")

        if not all_chunks:
            return {"status": "error", "message": "No supported files found in directory"}

        logger.info(f"Total chunks to embed: {len(all_chunks)}")

        # Embed in batches of 100 (API limit)
        BATCH_SIZE = 100
        all_embeddings = []
        texts = [c["content"] for c in all_chunks]

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i: i + BATCH_SIZE]
            logger.info(f"Embedding batch {i // BATCH_SIZE + 1}/{(len(texts) - 1) // BATCH_SIZE + 1}")
            embeddings = self.embed_texts(batch)
            all_embeddings.append(embeddings)

        all_embeddings_np = np.vstack(all_embeddings)

        # Build FAISS flat (exact) index
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self.index.add(all_embeddings_np)
        self.metadata = all_chunks

        # Persist to disk
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(METADATA_PATH, "w") as f:
            json.dump(self.metadata, f)

        logger.info(f"Ingestion complete. Files: {file_count}, Chunks: {len(all_chunks)}")
        return {
            "status": "success",
            "files_processed": file_count,
            "chunks_stored": len(all_chunks),
            "project_dir": project_dir,
        }


# Singleton instance
ingestor = CodebaseIngestor()
