# Legacy MVP Specification Baseline

## Purpose

This record preserves the product and technical intent that was documented in `HA-FLOW-MAP-SPEC.md` before that standalone specification is removed. It is a historical baseline, not a statement that every listed capability exists today.

## Product Baseline

HA Flow Map was specified as a read-only Home Assistant dependency and execution-flow explorer. Its central goals are to show where an item is used, expose direct and indirect dependencies, distinguish certainty from dynamic relationships, and reduce the need to manually trace YAML in complex installations.

The original MVP explicitly excludes editing configuration through the map, guaranteeing discovery of external callers, executing arbitrary Jinja templates, full execution-trace/history analysis, comprehensive custom-card parsing, and replacing Home Assistant's native automation editor.

## Identity and Integration Surface

The preserved public identity is **HA Flow Map**, with sidebar title **Flow Map**, repository name `ha-flow-map`, and integration domain `ha_flow_map`. The intended short description is “Visualize relationships and execution flows across Home Assistant.”

The specification defined equivalent WebSocket operations for search, node details, relations, flow, status, and administrator-requested rebuild. These command names and their bounded request model exist in the current implementation; [Pattern: Panel WebSocket Interaction](../knowledge/patterns/panel-websocket-interaction.md) records how to extend them.

## Current Coverage of the Baseline

Implemented and documented in intent, decisions, and patterns:

- Discovery of supported automation, script, scene, event, entity, device, area, service, and nested-flow relationships.
- Search, inbound/outbound exploration, impact summaries, service-node visibility control, zoom/drag/layout interaction, and selected-item details.
- Explicit distinction between confirmed and dynamic template-derived references.
- Bounded queries, reverse indexes, debounced rebuilds, status/warning feedback, redaction, administrator-only rebuild, and a read-only panel.
- Configuration flow, sidebar registration, WebSocket operations, parser/coordinator/frontend unit checks, and Home Assistant compatibility guidance.

Deliberate limitations retained from the original MVP scope are recorded in `README.md`: dashboard/custom-card parsing, execution traces/history, and static discovery of external callers are not implemented.

## Historic Contract and Interface Expectations

The original specification requires a typed graph with stable namespaced IDs, relation provenance, confidence, source location, and useful metadata. The current contract and the service-node projection choice are preserved in [Decision: Graph Contract and Service Projection](../decisions/005-graph-contract-and-service-projection.md).

The specified user experience includes search, graph canvas, direction and depth controls, service visibility, details, native Home Assistant links when available, visual confidence cues, and feedback for incomplete data. Some proposed controls remain backlog items: filters by node/relation/confidence, individual node expansion/removal controls, and an explicit recenter/reorganize action.

## Historic Quality and Safety Requirements

The legacy specification requires that invalid or incomplete input not stop the whole index, errors identify their source, index status distinguish complete/partial/failed, large graphs be bounded, the event loop remain responsive, and sensitive configuration values not be exposed. These requirements are implemented or reflected in:

- [Decision: Safe and Bounded Data Exposure](../decisions/004-safe-and-bounded-data-exposure.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)
- [Pattern: Resilient Coordinated Rebuild](../knowledge/patterns/resilient-coordinated-rebuild.md)

The legacy test checklist is represented by the existing parser, coordinator, WebSocket, panel, setup, and frontend test suites. Test expansion remains appropriate when new source types or UI controls are added.

## Deferred Roadmap from the Specification

The following was proposed for later phases and is not represented as current feature intent:

1. **Dashboards** — native dashboard/card nodes and explicit tap/hold/double-tap actions, with tolerant custom-card handling.
2. **Execution and traces** — observed relationships, executed paths, condition outcomes, last execution information, and comparison of possible versus actual flow.
3. **Diagnostics** — stale entity references, orphaned scripts/scenes, never-run automations, cycles, complexity indicators, and dynamic-dependency auditability.
4. **Advanced features** — map export, instance-local shareable URLs, graph comparison, saved layouts, grouping, and installation-wide aggregation.

## Official References Retained

- [Home Assistant WebSocket API](https://developers.home-assistant.io/docs/api/websocket/)
- [Extending the WebSocket API](https://developers.home-assistant.io/docs/frontend/extending/websocket-api/)
- [Frontend architecture](https://developers.home-assistant.io/docs/frontend/architecture/)
- [Frontend data](https://developers.home-assistant.io/docs/frontend/data/)
- [Entity registry](https://developers.home-assistant.io/docs/entity_registry_index/)
- [Device registry](https://developers.home-assistant.io/docs/device_registry_index/)
- [Automation triggers](https://www.home-assistant.io/docs/automation/trigger/)
- [Automation actions](https://www.home-assistant.io/docs/automation/action/)
- [Script syntax](https://www.home-assistant.io/docs/scripts/)
- [Script conditions](https://www.home-assistant.io/docs/scripts/conditions/)

## Supersession and Maintenance

For future work, create an intent file only once a roadmap item becomes an approved product capability. Record its implementation choice in a decision and its reusable technique in a pattern. Do not copy these deferred technical proposals into a feature file.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Graph-Based Relationship Model](../decisions/002-graph-based-relationship-model.md)
- [Decision: Graph Contract and Service Projection](../decisions/005-graph-contract-and-service-projection.md)
- [Changelog](changelog.md)

## Status

- **Created**: 2026-08-30 (Phase: Learn)
- **Status**: Historical baseline retained
- **Note**: Consolidated from `HA-FLOW-MAP-SPEC.md`; current implementation remains the authority for existing behavior.
