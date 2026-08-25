"""Library-neutral graph model used by the parsers and transport."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from typing import Any


@dataclass(slots=True)
class Node:
    id: str
    type: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Edge:
    id: str
    source: str
    target: str
    type: str
    confidence: str = "confirmed"
    source_kind: str = "configuration"
    location: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self):
        result = {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "confidence": self.confidence,
            "source_kind": self.source_kind,
            "metadata": self.metadata,
        }
        if self.location:
            result["location"] = self.location
        return result


class Graph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.warnings: list[dict[str, str]] = []

    def add_node(self, node: Node):
        self.nodes.setdefault(node.id, node)
        return node.id

    def add_edge(self, edge: Edge):
        key = (
            f"{edge.source}|{edge.target}|{edge.type}|{edge.location or ''}|"
            f"{edge.confidence}"
        )
        # Python's hash is intentionally randomized between interpreter runs;
        # IDs are part of the API contract and must remain stable after rebuilds.
        edge.id = f"edge:{sha1(key.encode()).hexdigest()[:16]}"
        if not any(
            (item.source, item.target, item.type, item.location, item.confidence)
            == (edge.source, edge.target, edge.type, edge.location, edge.confidence)
            for item in self.edges.values()
        ):
            self.edges[edge.id] = edge
        return edge.id

    def as_dict(self):
        return {
            "nodes": [node.as_dict() for node in self.nodes.values()],
            "edges": [edge.as_dict() for edge in self.edges.values()],
            "warnings": self.warnings,
        }
