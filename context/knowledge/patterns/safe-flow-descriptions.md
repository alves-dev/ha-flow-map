# Pattern: Safe Flow Descriptions

## Description

Generate concise human-readable labels from explicitly discovered configuration
metadata without evaluating templates or exposing sensitive values.

## When to Use

Use when presenting an action, condition, or trigger in the Flow Map panel or
another read-only consumer.

## Pattern

Store only the supported fields needed to describe the item, passing every
value through the configuration sanitiser. Resolve target names from graph nodes
when they are available. Use recognized service, condition, and trigger forms
for a natural phrase. If a value is dynamic, template-derived, or unrecognized,
fall back to a short technical description rather than guessing intent.

## Files Using This Pattern

- `custom_components/ha_flow_map/parsers/automation.py` — retains sanitized
  action, condition, and trigger metadata.
- `custom_components/ha_flow_map/frontend/flow-map-model.js` — provides pure
  helpers for action, condition, and trigger descriptions.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — applies the labels
  while rendering graph nodes.
- `tests/test_frontend.mjs` — verifies representative descriptions.

## Related

- [Decision: Safe Flow Descriptions](../../decisions/009-safe-flow-descriptions.md)
- [Decision: Safe and Bounded Data Exposure](../../decisions/004-safe-and-bounded-data-exposure.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)
- [Pattern: Recursive Flow Parsing](recursive-flow-parsing.md)

## Status

- **Created**: 2026-08-31
- **Status**: Active
