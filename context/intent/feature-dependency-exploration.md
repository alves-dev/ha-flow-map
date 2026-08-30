# Feature: Dependency Exploration

## What

Provides a searchable Flow Map where people can select an item and explore the nearby relationships that lead into it, out of it, or both.

## Why

Lets users quickly answer practical questions such as what activates an automation, what it controls, and how closely connected items relate without manually tracing configuration.

## Acceptance Criteria

- [ ] Users can find supported items by name or identifier.
- [ ] Users can explore inbound, outbound, or combined relationships.
- [ ] Users can control the amount of surrounding context shown.
- [ ] The view communicates when the result is limited or contains dynamic references.

## Related

- [Project Intent](project-intent.md)
- [Decision: Home Assistant Integration Boundary](../decisions/003-home-assistant-integration-boundary.md)
- [Decision: Safe and Bounded Data Exposure](../decisions/004-safe-and-bounded-data-exposure.md)
- [Decision: Graph Contract and Service Projection](../decisions/005-graph-contract-and-service-projection.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)
- [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active (already implemented)
