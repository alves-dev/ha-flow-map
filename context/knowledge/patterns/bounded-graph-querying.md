# Pattern: Bounded Graph Querying

## Description

Build inbound and outbound indexes once, then use breadth-first traversal with explicit limits for neighborhood and impact responses.

## When to Use

Use for any new graph query exposed to the panel or another consumer, especially when user input determines traversal scope.

## Pattern

Clamp requested limits to supported ranges, track visited nodes to avoid cycles, return selected nodes and edges, and include a `truncated` signal whenever queued work remains.

## Example

```python
depth = max(1, min(int(depth), 3))
seen = {node_id}
selected = []
queue = deque([(node_id, 0)])
while queue and len(seen) < max_nodes and len(selected) < max_edges:
    current, level = queue.popleft()
    if level >= depth:
        continue
    for edge in self.inbound[current] + self.outbound[current]:
        other = edge.source if edge.target == current else edge.target
        if other not in seen and len(seen) < max_nodes:
            seen.add(other)
            queue.append((other, level + 1))
```

## Files Using This Pattern

- `custom_components/ha_flow_map/graph/index.py` — builds reverse indexes and runs neighborhood and impact traversal.
- `custom_components/ha_flow_map/websocket_api.py` — validates request bounds before querying.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — informs users when responses are limited.

## Related

- [Decision: Graph-Based Relationship Model](../../decisions/002-graph-based-relationship-model.md)
- [Decision: Safe and Bounded Data Exposure](../../decisions/004-safe-and-bounded-data-exposure.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)
- [Feature: Change-Impact Summaries](../../intent/feature-impact-summaries.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
