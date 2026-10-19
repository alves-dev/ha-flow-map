# Pattern: Focused Flow Projection

## Description

Render one configuration owner's flow by traversing its structural and output
relationships without expanding the general dependency neighborhood.

## When to Use

Use when an operator needs the complete direct flow of an automation, script,
or scene without unrelated inputs, callers, or dependencies from other owners.

## Pattern

Include direct trigger edges into the selected owner as entry context, then
follow its outgoing structural and output relations. Do not traverse beyond the
trigger nodes; exclude other input and condition-reference relations. Stop when
reaching another configuration owner so a direct call remains visible without
inlining that owner's flow. When the graph reuses a service node, retain the
originating owner and location on service-call and target edges, then only
follow targets that match both values. Apply the normal node and edge bounds
and return a truncation signal.

## Files Using This Pattern

- `custom_components/ha_flow_map/parsers/automation.py` — records the owner on
  service calls and their target edges.
- `custom_components/ha_flow_map/graph/index.py` — creates the bounded,
  owner-scoped focused flow.
- `custom_components/ha_flow_map/websocket_api.py` — exposes the focused-flow
  operation.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — provides the
  focused-flow control and return to neighborhood exploration.

## Related

- [Decision: Focused Flow Projection](../../decisions/007-focused-flow-projection.md)
- [Decision: Graph Contract and Service Projection](../../decisions/005-graph-contract-and-service-projection.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)
- [Pattern: Bounded Graph Querying](bounded-graph-querying.md)

## Status

- **Created**: 2026-08-31
- **Status**: Active
