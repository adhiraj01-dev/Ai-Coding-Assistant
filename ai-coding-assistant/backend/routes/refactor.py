"""
Refactor Route - Code refactoring and optimization endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent import agent, Intent

logger = logging.getLogger(__name__)
router = APIRouter()


class RefactorRequest(BaseModel):
    code: str
    instructions: Optional[str] = "Improve readability, rename variables, and break large functions."
    language: Optional[str] = ""


@router.post("/refactor")
async def refactor_code(request: RefactorRequest):
    """
    Refactor provided code for improved quality.

    Body:
        code: Code to refactor.
        instructions: Specific refactoring goals.
        language: Optional language hint.

    Returns:
        Refactored code with change summary.
    """
    try:
        message = f"Refactor this code. Instructions: {request.instructions}"

        result = agent.run(
            message=message,
            code=request.code,
            intent_override=Intent.REFACTOR,
        )
        return result

    except Exception as e:
        logger.error(f"Refactor route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
