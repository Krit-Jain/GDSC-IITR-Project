"""
Router: /api/ai
===============
Handles AI-powered file insight requests via Server-Sent Events (SSE)
for real-time streaming responses. Backed by Google Gemini 1.5 Flash.
Results are cached by SHA-256 file hash to avoid redundant API calls.

Endpoints
---------
GET /api/ai/explain?path=<file_path>&mode=<summary|functions|rationale>
"""

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from services.ai_service import stream_file_insight

router = APIRouter()

@router.get("/explain")
async def explain_file(
    path: str = Query(..., description="Absolute path to the file to explain"),
    mode: str = Query("summary", description="Insight mode: summary, functions, or rationale")
):
    """
    Streams an AI-generated explanation of the specified file using SSE.
    """
    valid_modes = {"summary", "functions", "rationale"}
    if mode not in valid_modes:
        mode = "summary"
        
    return EventSourceResponse(stream_file_insight(path, mode))
