"""
Service: AST Engine
===================
Multi-language static analysis engine for Nexvara.

Supports
--------
- Python  : built-in `ast` module — Import / ImportFrom nodes
- JS / TS : regex heuristics — ES6 import, require()
- C / C++ : regex heuristics — #include "local.h" directives

Returns
-------
A list of FileInfo objects (all discovered source files) and
a list of DependencyEdge objects (resolved inter-file relationships).
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Constants ─────────────────────────────────────────────────────────────────

# Directories to always skip during traversal
SKIP_DIRS: set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "coverage", ".pytest_cache",
    ".mypy_cache", "htmlcov", ".eggs", "*.egg-info",
}

# File extensions we understand
PYTHON_EXTS   = {".py"}
JS_EXTS       = {".js", ".jsx", ".mjs", ".cjs"}
TS_EXTS       = {".ts", ".tsx"}
C_EXTS        = {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}
SUPPORTED_EXTS = PYTHON_EXTS | JS_EXTS | TS_EXTS | C_EXTS


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    """Metadata about a single source file."""
    rel_path: str           # Path relative to repo root (used as node ID)
    abs_path: str           # Absolute filesystem path
    name: str               # Basename (e.g. "main.py")
    extension: str          # Extension (e.g. ".py")
    imports: list[str] = field(default_factory=list)  # Raw import strings found


@dataclass
class DependencyEdge:
    """A resolved dependency relationship between two files."""
    source: str             # rel_path of the importing file
    target: str             # rel_path of the imported file


# ── Main Entry Point ──────────────────────────────────────────────────────────

def analyse_directory(root_path: str) -> tuple[list[FileInfo], list[DependencyEdge]]:
    """
    Traverse a directory, parse all source files, and return structured
    FileInfo objects and resolved DependencyEdge relationships.

    Parameters
    ----------
    root_path : str
        Absolute path to the repository root.

    Returns
    -------
    files : list[FileInfo]
        All discovered source files with raw import strings.
    edges : list[DependencyEdge]
        Resolved inter-file dependency edges.
    """
    root = Path(root_path).resolve()
    files: list[FileInfo] = []

    # ── Walk the directory ────────────────────────────────────────────────────
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip-dirs in-place so os.walk doesn't recurse into them
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            abs_path = Path(dirpath) / filename
            ext = abs_path.suffix.lower()

            if ext not in SUPPORTED_EXTS:
                continue

            rel_path = str(abs_path.relative_to(root)).replace("\\", "/")

            info = FileInfo(
                rel_path=rel_path,
                abs_path=str(abs_path),
                name=filename,
                extension=ext,
                imports=[],
            )

            # Parse the file for raw import strings
            try:
                source_code = abs_path.read_text(encoding="utf-8", errors="replace")
                if ext in PYTHON_EXTS:
                    info.imports = _extract_python_imports(source_code)
                elif ext in (JS_EXTS | TS_EXTS):
                    info.imports = _extract_js_imports(source_code)
                elif ext in C_EXTS:
                    info.imports = _extract_c_includes(source_code)
            except Exception:
                pass  # Unreadable file — skip silently

            files.append(info)

    # ── Resolve import strings → DependencyEdge ───────────────────────────────
    edges = _resolve_edges(files, root)
    return files, edges


# ── Language-specific Parsers ─────────────────────────────────────────────────

def _extract_python_imports(source: str) -> list[str]:
    """
    Use Python's built-in `ast` module to extract all import targets.
    Handles both `import foo` and `from foo import bar` forms.
    """
    imports: list[str] = []
    try:
        tree = ast.parse(source, type_comments=False)
    except SyntaxError:
        # Fallback: regex for files with syntax errors
        return _python_import_regex_fallback(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # node.level > 0 means relative import (e.g. `from .utils import X`)
            if node.module:
                prefix = "." * node.level
                imports.append(prefix + node.module)
            elif node.level > 0:
                # `from . import something`
                imports.append("." * node.level)

    return imports


def _python_import_regex_fallback(source: str) -> list[str]:
    """Regex fallback for Python files that fail to parse (e.g. Python 2)."""
    pattern = re.compile(
        r"^(?:from\s+([\.\w]+)\s+import|import\s+([\.\w ,]+))",
        re.MULTILINE,
    )
    results = []
    for match in pattern.finditer(source):
        target = match.group(1) or match.group(2)
        if target:
            for part in target.split(","):
                results.append(part.strip())
    return results


def _extract_js_imports(source: str) -> list[str]:
    """
    Extract import targets from JS/TS files using regex.

    Covers:
    - ES6: import X from './foo'
    - ES6: import { X } from "../bar"
    - Dynamic: import('./baz')
    - CommonJS: require('./qux')
    - Re-exports: export { X } from './module'
    """
    patterns = [
        # import ... from '...' / "..."
        re.compile(r'(?:import|export)\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', re.DOTALL),
        # import('...')
        re.compile(r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'),
        # require('...')
        re.compile(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'),
        # Side-effect imports: import '...'
        re.compile(r'import\s+[\'"]([^\'"]+)[\'"]'),
    ]

    imports: list[str] = []
    seen: set[str] = set()

    for pattern in patterns:
        for match in pattern.finditer(source):
            target = match.group(1)
            if target and target not in seen:
                seen.add(target)
                imports.append(target)

    return imports


def _extract_c_includes(source: str) -> list[str]:
    """
    Extract local #include directives from C/C++ files.
    Only processes quoted includes (#include "file.h"), not system ones (<stdio.h>).
    """
    pattern = re.compile(r'#\s*include\s+"([^"]+)"')
    return [match.group(1) for match in pattern.finditer(source)]


# ── Edge Resolution ───────────────────────────────────────────────────────────

def _resolve_edges(
    files: list[FileInfo],
    root: Path,
) -> list[DependencyEdge]:
    """
    Convert raw import strings in each FileInfo into concrete DependencyEdge
    objects by matching them against known file paths.

    Strategy
    --------
    - Build a lookup index: module_key → rel_path for quick matching
    - For Python: resolve dotted names (e.g. "services.ast_engine") and
      relative imports (e.g. ".metrics") to file paths
    - For JS/TS: resolve relative paths (./foo, ../bar) to actual files
    - For C/C++: resolve "local.h" relative to the including file's directory
    """
    # Build lookup maps
    rel_path_set: set[str] = {f.rel_path for f in files}
    # Map basename (no ext) → rel_path for fuzzy matching
    basename_map: dict[str, list[str]] = {}
    for f in files:
        stem = Path(f.rel_path).stem
        basename_map.setdefault(stem, []).append(f.rel_path)

    # Map dotted module path → rel_path (for Python)
    # e.g. "services.ast_engine" → "services/ast_engine.py"
    module_map: dict[str, str] = {}
    for f in files:
        if f.extension in PYTHON_EXTS:
            # Convert path to dotted module notation
            dotted = f.rel_path.replace("/", ".").replace("\\", ".")
            for ext in PYTHON_EXTS:
                dotted = dotted.removesuffix(ext)
            module_map[dotted] = f.rel_path

    edges: list[DependencyEdge] = []
    seen_edges: set[tuple[str, str]] = set()

    for file_info in files:
        source_dir = str(Path(file_info.rel_path).parent)
        ext = file_info.extension

        for raw_import in file_info.imports:
            target: Optional[str] = None

            if ext in PYTHON_EXTS:
                target = _resolve_python_import(
                    raw_import, file_info.rel_path, module_map, rel_path_set, root
                )
            elif ext in (JS_EXTS | TS_EXTS):
                target = _resolve_js_import(
                    raw_import, source_dir, rel_path_set, files
                )
            elif ext in C_EXTS:
                target = _resolve_c_include(
                    raw_import, source_dir, rel_path_set
                )

            if target and target != file_info.rel_path:
                edge_key = (file_info.rel_path, target)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(DependencyEdge(
                        source=file_info.rel_path,
                        target=target,
                    ))

    return edges


def _resolve_python_import(
    raw: str,
    source_path: str,
    module_map: dict[str, str],
    rel_path_set: set[str],
    root: Path,
) -> Optional[str]:
    """Resolve a Python import string to a rel_path."""
    source_dir = str(Path(source_path).parent)

    # Relative import (starts with dots)
    if raw.startswith("."):
        level = len(raw) - len(raw.lstrip("."))
        module_part = raw.lstrip(".")
        parts = source_dir.split("/")
        base_parts = parts[:max(0, len(parts) - level + 1)]

        if module_part:
            candidate_parts = base_parts + module_part.split(".")
        else:
            candidate_parts = base_parts

        # Try as a module file
        candidate = "/".join(candidate_parts) + ".py"
        if candidate in rel_path_set:
            return candidate
        # Try as a package __init__.py
        candidate = "/".join(candidate_parts) + "/__init__.py"
        if candidate in rel_path_set:
            return candidate
        return None

    # Absolute import — check module_map first
    if raw in module_map:
        return module_map[raw]

    # Try progressive prefix matching (handle "from services.metrics import X")
    parts = raw.split(".")
    for i in range(len(parts), 0, -1):
        dotted = ".".join(parts[:i])
        if dotted in module_map:
            return module_map[dotted]

    return None


def _resolve_js_import(
    raw: str,
    source_dir: str,
    rel_path_set: set[str],
    files: list[FileInfo],
) -> Optional[str]:
    """Resolve a JS/TS import string to a rel_path."""
    # Only handle relative imports (./foo, ../bar) — skip npm packages
    if not raw.startswith("."):
        return None

    base = (Path(source_dir) / raw).as_posix()
    # Normalise path separators
    base = _normalise_path(base)

    # Try exact match first
    if base in rel_path_set:
        return base

    # Try with common extensions
    for ext in [".js", ".jsx", ".ts", ".tsx", ".mjs"]:
        candidate = base + ext
        if candidate in rel_path_set:
            return candidate

    # Try as index file in a directory
    for ext in [".js", ".jsx", ".ts", ".tsx"]:
        candidate = base + "/index" + ext
        if candidate in rel_path_set:
            return candidate

    return None


def _resolve_c_include(
    raw: str,
    source_dir: str,
    rel_path_set: set[str],
) -> Optional[str]:
    """Resolve a C/C++ local #include path to a rel_path."""
    candidate = _normalise_path(str(Path(source_dir) / raw))
    if candidate in rel_path_set:
        return candidate
    return None


def _normalise_path(path: str) -> str:
    """
    Normalise a path string: resolve '..' components and standardise
    separators to forward slashes without making it absolute.
    """
    parts = []
    for part in path.replace("\\", "/").split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return "/".join(parts)
