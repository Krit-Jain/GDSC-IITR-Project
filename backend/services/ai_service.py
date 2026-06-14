"""
Service: AI Service
====================
Manages all interactions with Google Gemini 1.5 Flash API.

Features
--------
- **Streaming responses** via Server-Sent Events (SSE)
- **SHA-256 file hash caching**: If a file hasn't changed since the last
  analysis, the cached response is returned instantly — zero API cost.
- **Three insight modes**:
    1. `summary`   — 3-sentence plain-English summary of the file
    2. `functions` — Bulleted list of key functions/classes and their purpose
    3. `rationale` — Why does this file exist? What architectural role does it play?

Cache Strategy
--------------
Cache stored in `backend/cache/` as JSON files keyed by SHA-256 hash.
Format: { "hash": "...", "mode": "...", "response": "...", "timestamp": "..." }

Phase
-----
Implemented in Phase 3.
"""
# TODO (Phase 3): Implement Gemini AI service with streaming + SHA cache
