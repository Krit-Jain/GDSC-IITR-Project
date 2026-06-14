# Nexvara — Architecture Deep Dive

> This document covers the internal design decisions and data flow of the Nexvara system.

---

## System Overview

Nexvara is a full-stack developer intelligence platform split into two services:

| Service | Port | Technology |
|---|---|---|
| **Backend** | `8000` | Python 3.11 + FastAPI |
| **Frontend** | `5173` | React 18 + Vite |

Communication is via REST (JSON) for analysis data and **Server-Sent Events (SSE)** for AI streaming.

---

## Data Flow: Full Analysis Pipeline

```
User inputs a local directory path
           │
           ▼
[Frontend] POST /api/analyze?path=...
           │
           ▼
[Backend: routers/analyze.py]
  1. Validate path exists & is a directory
  2. Call ast_engine.traverse(path)
           │
           ▼
[Backend: services/ast_engine.py]
  3. os.walk() — discover all source files
  4. Per .py file: parse with ast.parse()
       → extract Import / ImportFrom nodes
       → resolve to relative file paths
  5. Per .js/.ts file: regex import extraction
  6. Per .c/.cpp/.h file: #include extraction
  7. Return: List[Tuple[source, target]]
           │
           ▼
[Backend: services/metrics.py]
  8. Per file: count LoC (non-blank, non-comment)
  9. Per .py file: radon.complexity.cc_visit()
       → McCabe Cyclomatic Complexity
  10. Coupling score = len(unique imports)
           │
           ▼
[Backend: services/graph_engine.py]
  11. networkx.DiGraph from edges
  12. Detect cycles: nx.find_cycle()
  13. Compute blast radius per node:
       reverse_graph = G.reverse()
       blast = nx.descendants(reverse_graph, node)
  14. Serialise to React Flow format:
       nodes: [{ id, data: { label, loc, complexity, coupling, blastRadius } }]
       edges: [{ id, source, target, animated: isCyclic }]
           │
           ▼
[Frontend] receives JSON → Zustand store
           │
           ▼
[Frontend: useGraphLayout]
  15. ELKjs computes node positions (hierarchical/force/radial)
           │
           ▼
[Frontend: GraphCanvas]
  16. React Flow renders draggable, zoomable graph
  17. CustomNode renders complexity heatmap glow
```

---

## AI Pipeline: Streaming File Insights

```
User clicks a node
       │
       ▼
[Frontend] opens EventSource to /api/ai/explain?path=...&mode=...
       │
       ▼
[Backend: routers/ai.py]
  1. Read file content
  2. Compute SHA-256(content)
  3. Check cache/  for existing entry with same hash + mode
     ├── HIT  → stream cached response character by character
     └── MISS → call Gemini 1.5 Flash API (streaming=True)
                 → write chunks to SSE stream
                 → save full response to cache JSON
       │
       ▼
[Frontend: SidePanel]
  4. Appends each SSE chunk to displayed text
  5. Shows "⚡ Cached" badge if served from cache
```

---

## Key Design Decisions

### Why ELKjs over Dagre?
ELKjs (Eclipse Layout Kernel) is the industry standard for complex hierarchical graphs. It handles large graphs with hundreds of nodes much better than Dagre, supports multiple algorithms (layered, force, stress, radial) and is the official recommendation in React Flow docs.

### Why SHA-256 cache instead of TTL cache?
A TTL (time-based) cache would re-analyse unchanged files on expiry. SHA-256 content hashing ensures the cache is only invalidated when the file **actually changes** — meaning cached results are always valid and API costs are minimised.

### Why Zustand over Redux?
Redux is heavyweight for a graph state that doesn't need complex middleware. Zustand's minimal API is ideal for this use case — no boilerplate, direct state mutations, and excellent React integration.

### Why NetworkX for graph operations?
NetworkX provides ready-made algorithms for cycle detection, BFS/DFS traversal, PageRank, and reverse graph operations — all needed for blast radius and circular dependency detection. Writing these from scratch would introduce bugs without benefit.
