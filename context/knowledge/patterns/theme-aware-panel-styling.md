# Pattern: Theme-Aware Panel Styling

## Description

Style panel UI and graph visuals from Home Assistant semantic theme tokens, and
freeze their computed values only when generating a standalone artifact.

## When to Use

Use when adding or changing a visual treatment in the Flow Map panel, including
SVG or raster exports.

## Pattern

Define local semantic tokens from Home Assistant's background, text, divider,
primary, accent, success, warning, and error tokens. Derive graph type colors
and fills with `color-mix()` from those local tokens. Do not add literal color
values to the panel stylesheet. For a standalone SVG, read the resolved local
tokens with `getComputedStyle()` and place the values in the SVG stylesheet.

## Example

```css
:host {
  --accent: var(--primary-color);
  --canvas: color-mix(in srgb, var(--card-background-color) 92%,
    var(--primary-text-color) 8%);
  --automation-fill: color-mix(in srgb, var(--accent) 18%, var(--canvas));
}
```

```javascript
const color = (name) => getComputedStyle(this).getPropertyValue(name).trim();
svg.insertAdjacentHTML(
  "afterbegin",
  `<style>line { stroke: ${color("--accent")}; }</style>`,
);
```

## Files Using This Pattern

- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — panel theme tokens
  and theme-aware SVG/PNG export.

## Related

- [Decision: Theme-Aware Panel Palette](../../decisions/006-theme-aware-panel-palette.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
