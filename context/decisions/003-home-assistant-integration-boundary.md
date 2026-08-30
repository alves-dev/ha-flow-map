# Decision: Home Assistant Integration Boundary

## Context

The integration needs configuration, lifecycle management, access to available runtime configuration, a sidebar surface, and communication between the panel and backend.

## Decision

Implement HA Flow Map as a single-instance Home Assistant config entry. Adapt public runtime entity configuration in a coordinator, serve a custom sidebar panel, and expose its data through registered Home Assistant WebSocket commands. Rebuild work is serialized and offloaded from the event loop when configuration extraction may be large.

## Rationale

This uses the host platform's established integration, panel, authorization, event, and WebSocket facilities. Keeping runtime-specific access in the coordinator localizes compatibility handling, while serialized rebuilds avoid overlapping index updates. Rationale is inferred from the integration lifecycle, coordinator, panel, and WebSocket code.

## Alternatives Considered

Alternatives are not documented in the existing codebase. Possible alternatives include a separate external service, a dashboard card instead of a sidebar panel, polling-only refresh, or access to private host storage; the current implementation uses platform services and runtime configuration adapters.

## Outcomes

Outcomes to be documented as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Tech Stack](001-tech-stack.md)
- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Feature: Index Refresh and Availability Feedback](../intent/feature-index-refresh.md)
- [Pattern: Resilient Coordinated Rebuild](../knowledge/patterns/resilient-coordinated-rebuild.md)
- [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
