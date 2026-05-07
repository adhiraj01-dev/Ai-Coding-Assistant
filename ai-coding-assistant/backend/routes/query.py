"""
Query Route - General-purpose developer query endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent import agent

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    message: str
    code: Optional[str] = ""
    explain_level: Optional[str] = "intermediate"  # beginner | intermediate | expert
    memory: Optional[list] = []


@router.post("/query")
async def query(request: QueryRequest):
    """
    General developer query — agent auto-detects intent and responds.

    Body:
        message: User's question or instruction.
        code: Optional code snippet for context.
        explain_level: Explanation depth (beginner/intermediate/expert).
        memory: Previous conversation turns.

    Returns:
        Agent response with detected intent and extracted code blocks.
    """
    try:
        result = agent.run(
            message=request.message,
            code=request.code or "",
            explain_level=request.explain_level,
            memory=request.memory or [],
        )
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
