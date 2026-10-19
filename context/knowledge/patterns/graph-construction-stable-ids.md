# Pattern: Graph Construction with Stable IDs

## Description

Build the dependency map through a small graph model where nodes and edges have typed, namespaced identifiers. Derive each edge ID deterministically and retain only the first equivalent relationship.

## When to Use

Use when adding a discoverable item or relationship that must remain stable across index rebuilds and be consumed by search, traversal, or panel code.

## Pattern

Create nodes with a domain-specific namespace such as `entity:` or `automation:`. Add edges through `Graph.add_edge()` rather than assigning identifiers at call sites. Include source, target, relation, location, and confidence in equivalence.

## Example

```python
def add_edge(self, edge: Edge):
    key = f"{edge.source}|{edge.target}|{edge.type}|{edge.location or ''}|{edge.confidence}"
    edge.id = f"edge:{sha1(key.encode()).hexdigest()[:16]}"
    if not any(
        (item.source, item.target, item.type, item.location, item.confidence)
        == (edge.source, edge.target, edge.type, edge.location, edge.confidence)
        for item in self.edges.values()
    ):
        self.edges[edge.id] = edge
```

## Files Using This Pattern

- `custom_components/ha_flow_map/graph/model.py` — defines the graph, node, edge, stable ID, and deduplication behavior.
- `custom_components/ha_flow_map/graph/builder.py` — assigns namespaced IDs while adapting configuration owners and runtime entities.

## Related

- [Decision: Graph-Based Relationship Model](../../decisions/002-graph-based-relationship-model.md)
- [Feature: Relationship Discovery](../../intent/feature-relationship-discovery.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
