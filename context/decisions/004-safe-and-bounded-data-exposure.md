# Decision: Safe and Bounded Data Exposure

## Context

Configuration data can contain sensitive service fields, templates whose final value is unknown, and graphs large enough to degrade host responsiveness or the panel experience.

## Decision

Treat templates as non-executed references, mark literal references found in them as dynamic, redact sensitive service-data fields, require administrator authorization for rebuilds, and impose limits on traversal depth, nodes, edges, and impact expansion.

## Rationale

The project is a read-only explorer and must not execute or expose more than it can safely determine. Explicit confidence and truncation signals make uncertainty visible, while bounded queries protect Home Assistant and the browser from oversized graph operations. Rationale is inferred from parser, index, WebSocket, and frontend code.

## Alternatives Considered

Alternatives are not documented in the existing codebase. Possible alternatives include rendering templates, returning unredacted action data, unlimited graph queries, or allowing all users to request rebuilds; none are used by the current implementation.

## Outcomes

Outcomes to be documented as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Relationship Discovery](../intent/feature-relationship-discovery.md)
- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Feature: Change-Impact Summaries](../intent/feature-impact-summaries.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)
- [Pattern: Recursive Flow Parsing](../knowledge/patterns/recursive-flow-parsing.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
