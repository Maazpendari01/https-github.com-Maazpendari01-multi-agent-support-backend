from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.logger import logger
import os

app = FastAPI(
    title="Multi-Agent Customer Support API",
    description="Production-grade multi-agent system with RAG",
    version="1.0.0",
)

# CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["tickets"])


@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Customer Support API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting FastAPI server...")
port = int(os.environ.get("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
