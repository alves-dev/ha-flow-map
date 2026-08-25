"""Fast reverse indexes and bounded graph traversal."""

from __future__ import annotations

from collections import defaultdict, deque


class GraphIndex:
    def __init__(self, graph):
        self.graph = graph
        self.inbound = defaultdict(list)
        self.outbound = defaultdict(list)
        for edge in graph.edges.values():
            self.outbound[edge.source].append(edge)
            self.inbound[edge.target].append(edge)

    def search(self, query, limit=50):
        needle = query.lower().strip()
        nodes = self.graph.nodes.values()
        return [
            node.as_dict()
            for node in nodes
            if not needle or needle in node.id.lower() or needle in node.label.lower()
        ][:limit]

    def neighborhood(
        self, node_id, direction="both", depth=1, max_nodes=250, max_edges=500
    ):
        depth = max(1, min(int(depth), 3))
        max_nodes = max(1, min(int(max_nodes), 1000))
        max_edges = max(1, min(int(max_edges), 2000))
        seen = {node_id}
        selected = []
        queue = deque([(node_id, 0)])
        while queue and len(seen) < max_nodes and len(selected) < max_edges:
            current, level = queue.popleft()
            if level >= depth:
                continue
            candidates = ([] if direction == "outbound" else self.inbound[current]) + (
                [] if direction == "inbound" else self.outbound[current]
            )
            for edge in candidates:
                if len(selected) >= max_edges:
                    break
                if edge not in selected:
                    selected.append(edge)
                other = edge.source if edge.target == current else edge.target
                if other not in seen and len(seen) < max_nodes:
                    seen.add(other)
                    queue.append((other, level + 1))
        truncated = bool(queue)
        return {
            "nodes": [
                self.graph.nodes[item].as_dict()
                for item in seen
                if item in self.graph.nodes
            ],
            "edges": [edge.as_dict() for edge in selected],
            "warnings": self.graph.warnings,
            "truncated": truncated,
        }
