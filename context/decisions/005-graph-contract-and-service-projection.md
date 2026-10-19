# Decision: Graph Contract and Service Projection

## Context

The Flow Map needs a backend contract that preserves enough relationship detail for queries and future visual changes while allowing people to simplify the graph when service actions add visual noise.

## Decision

Use a graph payload with `nodes`, `edges`, and `warnings`. Nodes carry a stable namespaced ID, type, label, and metadata. Edges carry stable IDs, source, target, typed relation, confidence, discovery source, configuration location, and explanatory metadata. Preserve service calls as graph nodes and edges internally; let the panel hide service nodes by projecting a direct combined edge between surrounding nodes.

The current contract includes node types for entity, automation, script, scene, action, service, event, device, area, condition, branch, and delay. It includes relationships such as triggers, reads_state, used_in_condition, targets, calls_service, calls_script, calls_automation, activates_scene, fires_event, listens_event, waits_for, contains, and next. The historic specification also reserves dashboard, card, and unknown nodes and additional relationship types for later work; those are not currently implemented.

## Rationale

Keeping the complete relationship internally allows the interface to switch between concise and technical views without losing meaning. A typed, stable payload makes the backend independent of a particular renderer and provides traceable explanations for each displayed connection. Rationale is inferred from the model, parser, frontend projection helper, and the original MVP specification.

## Alternatives Considered

The original specification considered making services only visual edges. The implemented approach instead stores services as first-class graph nodes and derives the simplified view in the panel. The specification proposed Cytoscape.js, React Flow, and ELK.js for rendering/layout; the existing project uses a native SVG implementation and custom layout helpers instead.

## Outcomes

The panel supports a service-node toggle without rebuilding the backend graph. Dashboard/card nodes and several future confidence classifications remain unimplemented.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Graph-Based Relationship Model](002-graph-based-relationship-model.md)
- [Decision: Focused Flow Projection](007-focused-flow-projection.md)
- [Decision: Sequential Action Steps](008-sequential-action-steps.md)
- [Decision: Safe Flow Descriptions](009-safe-flow-descriptions.md)
- [Decision: Tech Stack](001-tech-stack.md)
- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Pattern: Graph Construction with Stable IDs](../knowledge/patterns/graph-construction-stable-ids.md)
- [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Accepted
- **Note**: Consolidated from existing implementation and the legacy MVP specification
