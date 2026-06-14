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
- **Fan-In / Fan-Out**: How many files import *this* file vs how many it imports

Phase
-----
Implemented in Phase 1.
"""
# TODO (Phase 1): Implement metrics calculation using radon
