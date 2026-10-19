# Feature: Dependency Exploration

## What

Provides a searchable Flow Map where people can select an item and explore the nearby relationships that lead into it, out of it, or both.

## Why

Lets users quickly answer practical questions such as what activates an automation, what it controls, and how closely connected items relate without manually tracing configuration.

## Acceptance Criteria

- [ ] Users can find supported items by name or identifier.
- [ ] Users can explore inbound, outbound, or combined relationships.
- [ ] Users can control the amount of surrounding context shown.
- [x] When focused on an automation, users can view its direct triggers and
  complete set of output items without adding unrelated indirect relationships.
- [x] A flow communicates the configured order of actions and reconverges after
  supported conditional or parallel paths.
- [x] Supported actions, conditions, and triggers use plain-language
  descriptions without claiming certainty for dynamic configuration.
- [x] Flow connections distinguish supported branches, parallel paths, and
  calls into another configuration, while uncertainty remains visible.
- [x] Automation nodes show their current active, disabled, unavailable, or
  unknown state without implying that a flow path has executed.
- [ ] The view communicates when the result is limited or contains dynamic references.
- [x] The panel and its graph exports follow the active Home Assistant theme.

## Related

- [Project Intent](project-intent.md)
- [Decision: Home Assistant Integration Boundary](../decisions/003-home-assistant-integration-boundary.md)
- [Decision: Safe and Bounded Data Exposure](../decisions/004-safe-and-bounded-data-exposure.md)
- [Decision: Graph Contract and Service Projection](../decisions/005-graph-contract-and-service-projection.md)
- [Decision: Focused Flow Projection](../decisions/007-focused-flow-projection.md)
- [Decision: Sequential Action Steps](../decisions/008-sequential-action-steps.md)
- [Decision: Safe Flow Descriptions](../decisions/009-safe-flow-descriptions.md)
- [Decision: Visual Flow Semantics and Runtime State](../decisions/010-visual-flow-semantics.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)
- [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md)
- [Pattern: Sequential Action Steps](../knowledge/patterns/sequential-action-steps.md)
- [Pattern: Safe Flow Descriptions](../knowledge/patterns/safe-flow-descriptions.md)
- [Pattern: Visual Flow Semantics](../knowledge/patterns/visual-flow-semantics.md)
- [Decision: Theme-Aware Panel Palette](../decisions/006-theme-aware-panel-palette.md)
- [Pattern: Theme-Aware Panel Styling](../knowledge/patterns/theme-aware-panel-styling.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active (already implemented)
