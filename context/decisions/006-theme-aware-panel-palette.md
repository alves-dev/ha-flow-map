# Decision: Theme-Aware Panel Palette

## Context

The Flow Map sidebar was visually bound to a dark fixed palette. This made it
inconsistent with Home Assistant themes, including light and custom themes, and
caused downloaded SVG and PNG graphs to use unrelated colors.

## Decision

Derive all panel colors from Home Assistant theme tokens. Use the host's
background, text, divider, primary, accent, success, warning, and error colors
as semantic inputs. Create graph-type colors by mixing those inputs with the
themed canvas rather than introducing a fixed type palette. Resolve the same
computed tokens into standalone SVG exports and use the themed canvas for PNG
exports.

## Rationale

Home Assistant themes can define the main visual tokens used by custom panels.
Using semantic tokens keeps the panel aligned with the selected theme while
preserving graph distinctions through light, theme-derived tints. An exported
SVG is outside the Home Assistant document, so it needs resolved values rather
than CSS custom properties from its original host.

## Alternatives Considered

Keeping the fixed graph palette would preserve its original appearance but
would conflict with themed Home Assistant interfaces. Applying only a themed
page background would leave node and edge colors inconsistent. Referencing CSS
custom properties directly in the exported SVG would not work once it is opened
outside Home Assistant.

## Outcomes

The panel, SVG downloads, and PNG downloads now reflect the active theme at
render or export time. Theme authors retain control of the base semantic colors;
graph-specific shades are derived in the panel.

## Related

- [Decision: Tech Stack](001-tech-stack.md)
- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Pattern: Theme-Aware Panel Styling](../knowledge/patterns/theme-aware-panel-styling.md)

## Status

- **Created**: 2026-08-30 (Phase: Build)
- **Status**: Accepted
- **Note**: Replaces the panel's fixed dark palette with Home Assistant theme tokens.
