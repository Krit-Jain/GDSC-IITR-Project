"""
Nexvara — FastAPI Application Entry Point
==========================================
Main app bootstrap: registers routers, configures CORS, and mounts
the root health-check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze, ai

app = FastAPI(
    title="Nexvara API",
    description=(
        "Backend intelligence engine for Nexvara — a repository structure "
        "analysis and visualisation system. Parses local directories via AST, "
        "computes complexity metrics, detects dependency cycles, calculates "
        "blast radius, and streams AI-powered file insights."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Nexvara API", "version": "1.0.0"}
