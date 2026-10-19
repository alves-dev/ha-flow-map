# Feature: Index Refresh and Availability Feedback

## What

Keeps the relationship information current after relevant configuration changes, lets authorized administrators request a refresh, and reports whether the available map is complete, partial, unavailable, or failed.

## Why

Users need confidence that exploration reflects their latest setup while retaining clear feedback when some information cannot be collected.

## Acceptance Criteria

- [ ] Relationship information refreshes after supported configuration changes.
- [ ] Administrators can request a refresh.
- [ ] The experience reports index availability, size, timing, and warnings.
- [ ] A collection failure leaves a usable empty result instead of breaking the host system.

## Related

- [Project Intent](project-intent.md)
- [Decision: Home Assistant Integration Boundary](../decisions/003-home-assistant-integration-boundary.md)
- [Pattern: Resilient Coordinated Rebuild](../knowledge/patterns/resilient-coordinated-rebuild.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active (already implemented)
