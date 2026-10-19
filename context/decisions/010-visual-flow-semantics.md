# Decision: Visual Flow Semantics and Runtime State

## Context

The Flow Map now records ordered action steps and typed relations, but its
rendering shows most connections alike and presents every automation as active.
Home Assistant state snapshots are already available while the graph is built,
yet the configuration nodes do not retain their corresponding runtime state.

## Decision

Classify rendered edges from their explicit relation and configuration location:
show branch outcomes as yes or no, parallel paths as parallel, and calls into
another configuration as a flow call. Keep dynamic confidence as a separate
uncertainty signal. Copy the current state and availability of a configuration
entity onto its automation node during graph construction, then render its
status indicator from that metadata.

The map communicates configuration structure and current availability only. It
does not claim that an action, branch, or parallel path was actually executed.

## Rationale

The graph contract already provides the data needed to distinguish supported
relations without adding a renderer-specific backend format. Associating an
automation with its own state lets an operator see disabled or unavailable
automations at a glance while preserving the integration's read-only boundary.
Separating relation semantics from confidence prevents a dashed dynamic edge
from being mistaken for a different control-flow path.

## Alternatives Considered

Using one visual style for every confirmed edge is simpler but obscures the
control structure that the parser already preserves. Inferring execution from
state or showing an active indicator for every configuration would be
misleading. Adding trace collection was deferred because it requires runtime
history beyond the current static graph scope.

## Outcomes

The builder now attaches a configuration automation's current Home Assistant
state and availability to its node. The panel classifies explicit relation
semantics in pure helpers, renders the matching themed style in both the panel
and SVG exports, and gives automation status dots an accessible label. Focused
tests, frontend tests, lint, and static syntax validation pass.

## Related

- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Decision: Graph Contract and Service Projection](005-graph-contract-and-service-projection.md)
- [Decision: Sequential Action Steps](008-sequential-action-steps.md)
- [Decision: Theme-Aware Panel Palette](006-theme-aware-panel-palette.md)
- [Pattern: Theme-Aware Panel Styling](../knowledge/patterns/theme-aware-panel-styling.md)
- [Pattern: Visual Flow Semantics](../knowledge/patterns/visual-flow-semantics.md)

## Status

- **Created**: 2026-08-31 (Phase: Build)
- **Status**: Accepted
- **Note**: Approved visual-semantics approach; implementation follows.
