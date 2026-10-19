# Decision: Focused Flow Projection

## Context

Neighborhood exploration uses a configurable depth and follows relationships in
the selected direction. When an operator wants to understand one automation,
increasing that depth can add unrelated dependencies, particularly where service
nodes are shared by multiple configuration owners.

## Decision

Provide a focused-flow view for an automation, script, or scene. It includes the
selected owner, its internal control-flow structure, all of its direct outputs,
and direct trigger edges into the selected owner without applying the
neighborhood depth setting. Other references that only describe inputs or
conditions are excluded. A called automation, script, or scene is shown as an
output but is not expanded into its separately owned flow.

When a service action is included, select only its target edges from the same
configuration owner, location, and source. This prevents a shared service node
from pulling targets of other actions into the focused view. The view remains
bounded by the existing node and edge limits and reports truncation.

## Rationale

This keeps the visual answer aligned with the operator's question—what this
automation can do—while preserving the complete shared graph for general
dependency exploration. Location-aware service projection is necessary because
the current graph intentionally deduplicates service nodes.

## Alternatives Considered

Raising the standard depth limit would mix in indirect dependencies and obscure
the focused flow. Making a separate service node for every action would avoid
the ambiguity but would change the stable graph contract and duplicate shared
service information. Expanding called scripts and automations recursively would
also make the focused view much larger than the selected owner's direct flow.

## Outcomes

Focused flow now uses the same bounded limits as neighborhood exploration and
returns the selected owner's structural and output paths through the dedicated
WebSocket operation. Service-call and service-target edges carry the flow owner,
so repeated `actions[0]` locations in separate automations remain distinct.
Direct triggers are retained as the entry context without traversing upstream
dependencies.

## Related

- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Decision: Graph-Based Relationship Model](002-graph-based-relationship-model.md)
- [Decision: Graph Contract and Service Projection](005-graph-contract-and-service-projection.md)
- [Decision: Safe and Bounded Data Exposure](004-safe-and-bounded-data-exposure.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)
- [Pattern: Focused Flow Projection](../knowledge/patterns/focused-flow-projection.md)
- [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md)

## Status

- **Created**: 2026-08-31 (Phase: Build)
- **Status**: Accepted
- **Note**: Implemented without changing the shared graph's stable node IDs.
