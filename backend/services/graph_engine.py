"""
Service: Graph Engine
======================
Builds and analyses the dependency graph using NetworkX.

Responsibilities
----------------
- Construct a directed graph (DiGraph) from AST-extracted edges
- Detect **circular dependencies** (cycles)
- Compute **Blast Radius** for each node
- Return graph data serialised to React Flow node/edge format
"""

import networkx as nx
from typing import Any

from .ast_engine import FileInfo, DependencyEdge
from .metrics import FileMetrics, calculate_metrics


def build_and_analyze_graph(files: list[FileInfo], edges: list[DependencyEdge]) -> dict[str, Any]:
    """
    Builds a NetworkX graph, computes all necessary metrics (including graph metrics),
    and returns a payload formatted for React Flow.
    """
    G = nx.DiGraph()

    # Add all nodes with their calculated metrics
    for file_info in files:
        metrics = calculate_metrics(file_info)
        G.add_node(
            file_info.rel_path,
            name=file_info.name,
            extension=file_info.extension,
            loc=metrics.loc,
            complexity=metrics.complexity,
            coupling=metrics.coupling,
        )

    # Add edges
    for edge in edges:
        # Only add edge if both nodes exist (sanity check)
        if G.has_node(edge.source) and G.has_node(edge.target):
            G.add_edge(edge.source, edge.target)

    # Calculate Blast Radius for all nodes
    # Blast radius = number of descendants in the REVERSE graph
    # i.e., files that depend on this file
    R = G.reverse()
    for node in G.nodes():
        # descendants returns a set of nodes reachable from `node`
        blast_set = nx.descendants(R, node)
        G.nodes[node]["blastRadius"] = len(blast_set)
        # Store actual IDs for frontend hover effects
        G.nodes[node]["blastRadiusNodes"] = list(blast_set)

    # Detect cycles (circular dependencies)
    try:
        cycles = list(nx.simple_cycles(G))
    except nx.NetworkXNoCycle:
        cycles = []
    
    # Create a set of edges that participate in a cycle
    cyclic_edges = set()
    for cycle in cycles:
        # cycle is a list of nodes, e.g., ['A', 'B', 'C'] -> edges A->B, B->C, C->A
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            cyclic_edges.add((u, v))

    # Format for React Flow
    react_flow_nodes = []
    for node_id, data in G.nodes(data=True):
        react_flow_nodes.append({
            "id": node_id,
            "position": {"x": 0, "y": 0}, # ELKjs will layout
            "data": {
                "label": data["name"],
                "path": node_id,
                "extension": data["extension"],
                "loc": data["loc"],
                "complexity": data["complexity"],
                "coupling": data["coupling"],
                "blastRadius": data["blastRadius"],
                "blastRadiusNodes": data["blastRadiusNodes"]
            }
        })

    react_flow_edges = []
    for u, v in G.edges():
        is_cyclic = (u, v) in cyclic_edges
        edge_id = f"{u}->{v}"
        react_flow_edges.append({
            "id": edge_id,
            "source": u,
            "target": v,
            "animated": is_cyclic,
            "style": {
                "stroke": "#ef4444" if is_cyclic else "#a0a0c0",
                "strokeWidth": 2 if is_cyclic else 1
            }
        })

    return {
        "nodes": react_flow_nodes,
        "edges": react_flow_edges,
        "metrics": {
            "totalFiles": len(files),
            "totalDependencies": len(edges),
            "totalCycles": len(cycles)
        }
    }
