"""
Service: AI Service
====================
Manages all interactions with Google Gemini 1.5 Flash API.

Features
--------
- **Streaming responses** via Server-Sent Events (SSE)
- **SHA-256 file hash caching**: If a file hasn't changed since the last
  analysis, the cached response is returned instantly.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import AsyncGenerator

import google.generativeai as genai
from fastapi import HTTPException

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# The cache directory sits next to this file's parent
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "gemini-1.5-flash"


def _compute_hash(content: str) -> str:
    """Computes SHA-256 hash of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _get_cache_path(file_hash: str, mode: str) -> Path:
    """Returns the cache JSON path for a given hash and mode."""
    return CACHE_DIR / f"{file_hash}_{mode}.json"


def _read_cache(cache_path: Path) -> str | None:
    """Reads the response from cache if it exists."""
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text("utf-8"))
            return data.get("response")
        except Exception:
            pass
    return None


def _write_cache(cache_path: Path, file_hash: str, mode: str, response: str) -> None:
    """Writes the full AI response to the cache."""
    data = {
        "hash": file_hash,
        "mode": mode,
        "response": response
    }
    cache_path.write_text(json.dumps(data), "utf-8")


def _get_prompt_for_mode(mode: str, file_path: str, content: str) -> str:
    """Generates the prompt based on the requested insight mode."""
    base = f"You are Nexvara, a senior software architect. Analyze the file `{file_path}`:\n\n```\n{content}\n```\n\n"
    if mode == "summary":
        return base + "Explain what this code does in 3 simple sentences. Keep it extremely concise and developer-focused."
    elif mode == "functions":
        return base + "List the key functions/classes in this file and describe what each does in one bullet point each."
    elif mode == "rationale":
        return base + "Explain WHY this file exists. What architectural role does it play in the overall system? Keep it to 2 brief paragraphs."
    else:
        return base + "Provide a brief summary of this code."


async def stream_file_insight(abs_path: str, mode: str) -> AsyncGenerator[str, None]:
    """
    Streams the AI explanation of a file via SSE.
    Yields JSON strings of the format: data: {"chunk": "...", "cached": true/false}
    """
    path = Path(abs_path)
    if not path.exists() or not path.is_file():
        yield f'data: {json.dumps({"error": "File not found"})}\n\n'
        return

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        yield f'data: {json.dumps({"error": f"Failed to read file: {str(e)}"})}\n\n'
        return

    file_hash = _compute_hash(content)
    cache_path = _get_cache_path(file_hash, mode)
    
    # 1. Check cache first
    cached_response = _read_cache(cache_path)
    if cached_response:
        # Stream the cached response back immediately (chunked for visual effect)
        words = cached_response.split(" ")
        for word in words:
            chunk_data = json.dumps({"chunk": word + " ", "cached": True})
            yield f"data: {chunk_data}\n\n"
        return

    # 2. Cache MISS - Call Gemini API
    if not os.getenv("GEMINI_API_KEY"):
        yield f'data: {json.dumps({"error": "GEMINI_API_KEY not configured in backend"})}\n\n'
        return

    prompt = _get_prompt_for_mode(mode, path.name, content)
    model = genai.GenerativeModel(MODEL_NAME)
    
    try:
        response_stream = model.generate_content(prompt, stream=True)
        full_response = []
        
        for chunk in response_stream:
            text = chunk.text
            full_response.append(text)
            chunk_data = json.dumps({"chunk": text, "cached": False})
            yield f"data: {chunk_data}\n\n"
            
        # Write the final full string to cache
        _write_cache(cache_path, file_hash, mode, "".join(full_response))
        
    except Exception as e:
        yield f'data: {json.dumps({"error": f"AI Generation failed: {str(e)}"})}\n\n'
