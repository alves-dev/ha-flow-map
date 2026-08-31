# Feature: Change-Impact Summaries

## What

Shows the automations, scripts, and scenes connected to a selected item, together with the furthest dependency distance discovered.

## Why

Helps operators evaluate the possible consequences of renaming, removing, or changing an item before they make the change.

## Acceptance Criteria

- [ ] A selected item can show connected configuration owners.
- [ ] The summary accounts for relationships that use the item and relationships that affect it.
- [ ] The summary indicates when its result is limited.

## Related

- [Project Intent](project-intent.md)
- [Decision: Graph-Based Relationship Model](../decisions/002-graph-based-relationship-model.md)
- [Decision: Safe and Bounded Data Exposure](../decisions/004-safe-and-bounded-data-exposure.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active (already implemented)
