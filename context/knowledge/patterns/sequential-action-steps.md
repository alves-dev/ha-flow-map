# Pattern: Sequential Action Steps

## Description

Represent each configured action with an owner-scoped step node and connect the
steps in their declared order without relying on shared service nodes.

## When to Use

Use when adding a supported action or control-flow construct whose placement in
an automation, script, or scene needs to remain visible in the graph.

## Pattern

Create a stable action or control-flow node from the current terminal steps and
join it with `next` edges. Return the new terminal steps from the parser. A
conditional or parallel construct returns every path terminal; the caller joins
the next configured step from each of them. Connect a service action from its
unique action step to the shared service node, rather than using the service
node as a sequence step.

## Files Using This Pattern

- `custom_components/ha_flow_map/parsers/automation.py` — creates action steps,
  returns path terminals, and emits `next` relations.
- `custom_components/ha_flow_map/frontend/flow-map-model.js` — lays out `next`
  relations in the primary flow direction.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — presents action
  steps and optionally reveals service details.
- `tests/test_parsers.py` — verifies action order and branch reconvergence.

## Related

- [Decision: Sequential Action Steps](../../decisions/008-sequential-action-steps.md)
- [Decision: Graph Contract and Service Projection](../../decisions/005-graph-contract-and-service-projection.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)
- [Pattern: Recursive Flow Parsing](recursive-flow-parsing.md)

## Status

- **Created**: 2026-08-31
- **Status**: Active
