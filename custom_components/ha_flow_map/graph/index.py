"""Fast reverse indexes and bounded graph traversal."""

from __future__ import annotations

from collections import defaultdict, deque

SEARCHABLE_TYPES = {
    "automation",
    "script",
    "scene",
    "entity",
    "event",
    "device",
    "area",
}

FLOW_INPUT_RELATIONS = {
    "reads_state",
    "used_in_condition",
    "triggers",
    "listens_event",
    "waits_for",
}
FLOW_OWNER_TYPES = {"automation", "script", "scene"}


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
            self._visit_neighborhood(
                current,
                level,
                direction,
                max_nodes,
                max_edges,
                seen,
                selected,
                queue,
            )
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

    def _visit_neighborhood(
        self,
        current,
        level,
        direction,
        max_nodes,
        max_edges,
        seen,
        selected,
        queue,
    ):
        candidates = ([] if direction == "outbound" else self.inbound[current]) + (
            [] if direction == "inbound" else self.outbound[current]
        )
        for edge in candidates:
            if len(selected) >= max_edges:
                return
            if edge not in selected:
                selected.append(edge)
            other = edge.source if edge.target == current else edge.target
            if other not in seen and len(seen) < max_nodes:
                seen.add(other)
                queue.append((other, level + 1))

    def focused_flow(self, node_id, max_nodes=250, max_edges=500):
        """Return the selected owner's complete direct output flow.

        Service nodes are intentionally shared across the graph. Once a service
        call is reached, only targets from the same configuration location are
        followed, preventing another owner's service targets from leaking into
        this focused view.
        """
        max_nodes = max(1, min(int(max_nodes), 1000))
        max_edges = max(1, min(int(max_edges), 2000))
        seen = {node_id}
        selected = []
        selected_ids = set()
        queue = deque([(node_id, None, None, None)])
        visited = {(node_id, None, None, None)}
        truncated = False

        truncated = self._add_focused_triggers(
            node_id, max_nodes, max_edges, seen, selected, selected_ids
        )

        while queue and not truncated:
            current, service_location, source_kind, flow_owner = queue.popleft()
            node = self.graph.nodes.get(current)
            if not node:
                continue
            candidates = self._focused_candidates(
                current, node, service_location, source_kind, flow_owner
            )
            truncated = (
                self._visit_focused_edges(
                    candidates,
                    node_id,
                    max_nodes,
                    max_edges,
                    seen,
                    selected,
                    selected_ids,
                    visited,
                    queue,
                )
                or truncated
            )
            if truncated:
                break

        return {
            "nodes": [
                self.graph.nodes[item].as_dict()
                for item in seen
                if item in self.graph.nodes
            ],
            "edges": [edge.as_dict() for edge in selected],
            "warnings": self.graph.warnings,
            "truncated": truncated,
            "mode": "focused_flow",
        }

    def _visit_focused_edges(
        self,
        candidates,
        node_id,
        max_nodes,
        max_edges,
        seen,
        selected,
        selected_ids,
        visited,
        queue,
    ):
        truncated = False
        for edge in candidates:
            if edge.type in FLOW_INPUT_RELATIONS:
                continue
            truncated = (
                self._collect_focused_edge(
                    edge,
                    node_id,
                    max_nodes,
                    max_edges,
                    seen,
                    selected,
                    selected_ids,
                    visited,
                    queue,
                )
                or truncated
            )
            if truncated and len(selected) >= max_edges:
                break
        return truncated

    def _add_focused_triggers(
        self, node_id, max_nodes, max_edges, seen, selected, selected_ids
    ):
        for edge in self.inbound[node_id]:
            if edge.type not in {"triggers", "listens_event"}:
                continue
            if edge.source not in seen and len(seen) >= max_nodes:
                return True
            if len(selected) >= max_edges:
                return True
            seen.add(edge.source)
            selected.append(edge)
            selected_ids.add(edge.id)
        return False

    def _focused_candidates(
        self, current, node, service_location, source_kind, flow_owner
    ):
        if node.type != "service":
            return self.outbound[current]
        return [
            edge
            for edge in self.outbound[current]
            if edge.location == service_location
            and edge.source_kind == source_kind
            and edge.metadata.get("flow_owner") == flow_owner
        ]

    def _collect_focused_edge(
        self,
        edge,
        node_id,
        max_nodes,
        max_edges,
        seen,
        selected,
        selected_ids,
        visited,
        queue,
    ):
        target = edge.target
        if target not in seen and len(seen) >= max_nodes:
            return True
        if edge.id not in selected_ids:
            if len(selected) >= max_edges:
                return True
            selected.append(edge)
            selected_ids.add(edge.id)
        seen.add(target)
        target_node = self.graph.nodes.get(target)
        if target_node and target_node.type in FLOW_OWNER_TYPES and target != node_id:
            return False
        context = self._service_context(edge, target_node)
        state = (target, *context)
        if state not in visited:
            visited.add(state)
            queue.append(state)
        return False

    @staticmethod
    def _service_context(edge, target_node):
        if target_node and target_node.type == "service":
            return edge.location, edge.source_kind, edge.metadata.get("flow_owner")
        return None, None, None

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
                impacted[node.type].append(
                    {"id": node.id, "label": node.label, "depth": level}
                )
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
