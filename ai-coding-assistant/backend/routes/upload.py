"""
Upload Route - Handles codebase ingestion requests.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rag.ingest import ingestor
from rag.retrieve import retriever

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadRequest(BaseModel):
    project_dir: str  # Absolute or relative path to project directory


@router.post("/upload_codebase")
async def upload_codebase(request: UploadRequest):
    """
    Ingest a local codebase into the vector store.

    Body:
        project_dir: Path to the project directory to ingest.

    Returns:
        Summary of ingestion results.
    """
    try:
        logger.info(f"Ingestion requested for: {request.project_dir}")
        result = ingestor.ingest(request.project_dir)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        # Reload retriever to pick up new index
        retriever.reload()

        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
