"""
Generate Route - Code generation endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent import agent, Intent

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    language: Optional[str] = "Python"
    context_code: Optional[str] = ""  # Existing code for context


@router.post("/generate")
async def generate_code(request: GenerateRequest):
    """
    Generate code from a natural language prompt.

    Body:
        prompt: Description of code to generate.
        language: Target programming language.
        context_code: Existing code to consider for style/structure.

    Returns:
        Generated code with explanation.
    """
    try:
        message = f"Generate {request.language} code: {request.prompt}"

        result = agent.run(
            message=message,
            code=request.context_code or "",
            intent_override=Intent.GENERATE,
        )
        result["language"] = request.language
        return result

    except Exception as e:
        logger.error(f"Generate route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
