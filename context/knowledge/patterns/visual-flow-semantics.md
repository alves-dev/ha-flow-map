# Pattern: Visual Flow Semantics

## Description

Turn explicit graph relation and runtime metadata into themed visual cues while
keeping configuration structure, current state, and execution history distinct.

## When to Use

Use when adding a visible edge or node-state distinction to the Flow Map panel
or its SVG/PNG exports.

## Pattern

Classify edges in a pure frontend helper from their typed relation and recorded
configuration location. Let confidence remain a separate class so dynamic
references keep their uncertainty treatment. Derive all in-panel and exported
SVG colors from existing Home Assistant theme tokens. Associate runtime state
only with the configuration entity that owns it, and label that state as
current status rather than an execution result.

## Example

```javascript
const presentation = edgePresentation(edge);
const dynamic = edge.confidence === "dynamic";
line.classList.add(presentation.className);
if (dynamic) line.classList.add("dynamic");
```

## Files Using This Pattern

- `custom_components/ha_flow_map/graph/builder.py` — copies current
  automation state from Home Assistant snapshots.
- `custom_components/ha_flow_map/frontend/flow-map-model.js` — pure relation
  and automation-status classifiers.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — themed rendering
  and standalone SVG styling.
- `tests/test_frontend.mjs` and `tests/test_parsers.py` — representative
  presentation and state coverage.

## Related

- [Decision: Visual Flow Semantics and Runtime State](../../decisions/010-visual-flow-semantics.md)
- [Decision: Theme-Aware Panel Palette](../../decisions/006-theme-aware-panel-palette.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)
- [Pattern: Theme-Aware Panel Styling](theme-aware-panel-styling.md)

## Status

- **Created**: 2026-08-31
- **Status**: Active
