"""
Router: /api/analyze
====================
Accepts a local directory path, triggers the full analysis pipeline,
and returns a graph payload (nodes + edges) ready for React Flow.

Endpoints
---------
GET /api/analyze?path=<local_dir_path>
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

from services.ast_engine import analyse_directory
from services.graph_engine import build_and_analyze_graph

router = APIRouter()

@router.get("/analyze")
async def analyze_repo(path: str):
    """
    Analyses a local repository directory and returns a React Flow graph payload.
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path parameter is required")
    
    target_path = Path(path).expanduser().resolve()
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")
    if not target_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

    try:
        # Step 1: AST parsing and dependency extraction
        files, edges = analyse_directory(str(target_path))
        
        if not files:
            raise HTTPException(status_code=404, detail="No supported source files found in the directory")

        # Step 2: Build graph, calculate metrics, and format for React Flow
        payload = build_and_analyze_graph(files, edges)
        
        return payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
