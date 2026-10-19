# Feature: Relationship Discovery

## What

Identifies explicit relationships among supported home-automation configurations and the items they reference, including when an item starts, constrains, or is affected by an automation flow.

## Why

Gives operators a dependable inventory of visible dependencies, reducing the guesswork involved in understanding an established smart-home setup.

## Acceptance Criteria

- [ ] Supported configured relationships are available for discovery.
- [ ] Relationships distinguish directly known references from references that cannot be fully resolved.
- [ ] Unsupported or unavailable sources are communicated without presenting missing relationships as facts.

## Related

- [Project Intent](project-intent.md)
- [Decision: Graph-Based Relationship Model](../decisions/002-graph-based-relationship-model.md)
- [Decision: Safe and Bounded Data Exposure](../decisions/004-safe-and-bounded-data-exposure.md)
- [Pattern: Recursive Flow Parsing](../knowledge/patterns/recursive-flow-parsing.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active (already implemented)
