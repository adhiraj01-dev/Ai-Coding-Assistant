"""
Debug Route - Specialized debugging endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent import agent, Intent
from services.code_analyzer import code_analyzer

logger = logging.getLogger(__name__)
router = APIRouter()


class DebugRequest(BaseModel):
    code: str
    error_message: str
    language: Optional[str] = ""


@router.post("/debug")
async def debug_code(request: DebugRequest):
    """
    Debug code given an error message.

    Body:
        code: The buggy code snippet.
        error_message: The error or traceback.
        language: Optional programming language hint.

    Returns:
        Structured debug response: explanation, root cause, fixed code.
    """
    try:
        # Parse error for extra context
        error_info = code_analyzer.extract_error_info(request.error_message)
        lang = request.language or code_analyzer.detect_language(request.code)

        message = (
            f"Debug this {lang} code.\n"
            f"Error: {request.error_message}\n"
            f"Error type: {error_info.get('error_type', 'Unknown')}"
        )

        result = agent.run(
            message=message,
            code=request.code,
            intent_override=Intent.DEBUG,
        )

        result["error_info"] = error_info
        result["detected_language"] = lang
        return result

    except Exception as e:
        logger.error(f"Debug route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
