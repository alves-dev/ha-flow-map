# Decision: Safe Flow Descriptions

## Context

The graph already records configuration relationships, but raw service IDs and
condition types are harder to understand than the resulting behavior. Natural
language must not evaluate templates or infer values that the static
configuration does not establish.

## Decision

Preserve a safe subset of explicit action, condition, and trigger fields in
graph metadata. Generate Portuguese descriptions in independently testable
frontend helpers from those fields and known graph nodes. Prefer a
domain-specific phrase when the service or condition is recognized; otherwise
show a concise technical fallback. Dynamic or template-derived values remain
identified as such and are never interpreted.

## Rationale

Keeping the descriptions at presentation time preserves the technical graph
contract and lets labels use the best friendly names available in the returned
subgraph. Explicit metadata provides useful context without exposing secrets or
requiring the panel to parse raw configuration.

## Alternatives Considered

Generating prose in the parser would make presentation language part of the
core graph contract. Evaluating templates could produce misleading results or
execute untrusted configuration. Showing only raw YAML is precise but defeats
the panel's explanatory purpose.

## Outcomes

Action nodes now retain a sanitized service target and data subset, while
condition nodes and trigger edges retain the supported explicit fields needed
for descriptions. The frontend labels actions, state and numeric conditions,
logical conditions, and entity or event triggers without evaluating templates.

## Related

- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Decision: Safe and Bounded Data Exposure](004-safe-and-bounded-data-exposure.md)
- [Decision: Graph Contract and Service Projection](005-graph-contract-and-service-projection.md)
- [Pattern: Recursive Flow Parsing](../knowledge/patterns/recursive-flow-parsing.md)
- [Pattern: Safe Flow Descriptions](../knowledge/patterns/safe-flow-descriptions.md)

## Status

- **Created**: 2026-08-31 (Phase: Build)
- **Status**: Accepted
- **Note**: Implemented with safe metadata and frontend-only presentation helpers.
