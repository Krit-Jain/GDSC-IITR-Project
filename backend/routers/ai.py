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
# TODO (Phase 3): Implement AI streaming endpoint
