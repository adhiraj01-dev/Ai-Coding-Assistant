"""
AI Coding Assistant - FastAPI Backend
Main application entry point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import query, debug, generate, refactor, tests, upload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("assistant.log"),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Coding Assistant",
    description="Local AI agent for code understanding, debugging, and generation",
    version="1.0.0",
)

# Allow Streamlit frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(debug.router, prefix="/api", tags=["Debug"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(refactor.router, prefix="/api", tags=["Refactor"])
app.include_router(tests.router, prefix="/api", tags=["Tests"])


@app.get("/")
async def root():
    return {"message": "AI Coding Assistant is running", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
