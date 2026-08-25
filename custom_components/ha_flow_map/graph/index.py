"""Fast reverse indexes and bounded graph traversal."""

from __future__ import annotations

from collections import defaultdict, deque


SEARCHABLE_TYPES = {"automation", "script", "scene", "entity", "event", "device", "area"}


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
        nodes = (
            node
            for node in self.graph.nodes.values()
            if node.type in SEARCHABLE_TYPES
            and not self._is_duplicate_configuration_entity(node)
        )
        return [
            node.as_dict()
            for node in nodes
            if not needle or needle in node.id.lower() or needle in node.label.lower()
        ][:limit]

    def _is_duplicate_configuration_entity(self, node):
        """Hide runtime entities when their navigable config node is present.

        Home Assistant exposes automations, scripts and scenes as entities too.
        Showing both in search yields two identical friendly names, while the
        configuration node is the useful entry point for a flow exploration.
        """
        if node.type != "entity":
            return False
        entity_id = node.id.removeprefix("entity:")
        domain, separator, object_id = entity_id.partition(".")
        return bool(
            separator
            and domain in {"automation", "script", "scene"}
            and f"{domain}:{object_id}" in self.graph.nodes
        )

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

    def impact(self, node_id, max_depth=12, max_nodes=1000):
        """Summarise the configuration owners reachable from a node.

        The graph records relationships in their natural configuration direction.
        For impact analysis we deliberately walk both ways: an entity can trigger
        an automation (entity -> automation) and can also be changed by a script
        (script -> entity).  This gives an operator the complete set of owners to
        review before renaming or removing the selected item.
        """
        max_depth = max(1, min(int(max_depth), 20))
        max_nodes = max(1, min(int(max_nodes), 2000))
        seen = {node_id: 0}
        queue = deque([node_id])
        impacted = {"automation": [], "script": [], "scene": []}

        while queue and len(seen) < max_nodes:
            current = queue.popleft()
            level = seen[current]
            node = self.graph.nodes.get(current)
            if node and node.type in impacted and current != node_id:
                impacted[node.type].append({"id": node.id, "label": node.label, "depth": level})
            if level >= max_depth:
                continue
            for edge in self.inbound[current] + self.outbound[current]:
                other = edge.source if edge.target == current else edge.target
                if other not in seen:
                    seen[other] = level + 1
                    queue.append(other)

        return {
            "automations": impacted["automation"],
            "scripts": impacted["script"],
            "scenes": impacted["scene"],
            "levels": max(seen.values(), default=0),
            "truncated": bool(queue),
        }
