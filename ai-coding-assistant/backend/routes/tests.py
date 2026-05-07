"""
Tests Route - Unit test generation endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent import agent, Intent

logger = logging.getLogger(__name__)
router = APIRouter()


class TestRequest(BaseModel):
    code: str
    framework: Optional[str] = "pytest"  # pytest | unittest | jest
    language: Optional[str] = "Python"


@router.post("/tests")
async def generate_tests(request: TestRequest):
    """
    Generate unit tests for the provided code.

    Body:
        code: Code to test.
        framework: Test framework to use.
        language: Programming language.

    Returns:
        Complete test suite with edge cases.
    """
    try:
        message = (
            f"Generate {request.framework} unit tests for this {request.language} code. "
            f"Include edge cases, error cases, and clear test names."
        )

        result = agent.run(
            message=message,
            code=request.code,
            intent_override=Intent.TEST,
        )
        result["framework"] = request.framework
        return result

    except Exception as e:
        logger.error(f"Tests route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
