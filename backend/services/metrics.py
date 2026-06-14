"""
Service: Metrics Calculator
============================
Computes per-file code quality metrics used to colour nodes in the graph.

Metrics Computed
----------------
- **Lines of Code (LoC)**: Total non-blank, non-comment lines
- **Cyclomatic Complexity (CC)**: McCabe complexity via `radon`
  - Score 1–5   → LOW    (green)
  - Score 6–10  → MEDIUM (amber)
  - Score 11+   → HIGH   (red)
- **Coupling Score**: Number of unique files this file imports from
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from radon.complexity import cc_visit
from radon.metrics import h_visit

from .ast_engine import FileInfo


@dataclass
class FileMetrics:
    loc: int
    complexity: int
    coupling: int


def calculate_metrics(file_info: FileInfo) -> FileMetrics:
    """
    Calculate metrics for a given file.
    Uses radon for Python files, basic heuristics for others.
    """
    path = Path(file_info.abs_path)
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return FileMetrics(loc=0, complexity=0, coupling=len(set(file_info.imports)))

    loc = _count_loc(source, file_info.extension)
    complexity = _calculate_complexity(source, file_info.extension)
    coupling = len(set(file_info.imports))

    return FileMetrics(loc=loc, complexity=complexity, coupling=coupling)


def _count_loc(source: str, extension: str) -> int:
    """
    Calculate Lines of Code (LoC) excluding blanks.
    For Python, we also exclude comment lines.
    """
    lines = source.splitlines()
    if not lines:
        return 0

    if extension == ".py":
        # Rough estimation for Python: non-blank and non-comment
        return sum(
            1 for line in lines
            if line.strip() and not line.strip().startswith("#")
        )
    elif extension in {".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".h"}:
        # Basic for C/JS-style: ignore blanks and single-line comments
        return sum(
            1 for line in lines
            if line.strip() and not line.strip().startswith("//")
        )
    else:
        # Default fallback
        return sum(1 for line in lines if line.strip())


def _calculate_complexity(source: str, extension: str) -> int:
    """
    Calculate McCabe Cyclomatic Complexity.
    Only strictly supported for Python via `radon`.
    For other languages, returns a default of 1.
    """
    if extension != ".py":
        return 1

    try:
        # cc_visit returns a list of blocks (functions, classes, methods)
        blocks = cc_visit(source)
        if not blocks:
            return 1
        
        # Calculate the average or max complexity of the blocks in the file
        # Here we use the max complexity found in any block to represent the file's 'hotspot'
        return max(block.complexity for block in blocks)
    except SyntaxError:
        return 1
    except Exception:
        return 1
