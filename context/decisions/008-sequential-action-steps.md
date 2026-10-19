# Decision: Sequential Action Steps

## Context

Service nodes are intentionally shared across configuration owners. They can
show what an action calls, but cannot safely represent the unique position of
that action in an automation. The previous graph attached each sibling action
to the same parent, so it did not communicate configured execution order.

## Decision

Represent every configured action as an owner-scoped, stable `action` node and
connect consecutive steps with a typed `next` relation. Keep service nodes as
technical details connected from their corresponding action step. Parse nested
conditional, choose, parallel, sequence, and repeat structures as paths that
return their terminal steps; the following configured action receives `next`
edges from those terminals, making alternative paths reconverge without
inventing an execution result.

## Rationale

Unique action steps retain ordering and location without changing the shared
service-node model. A direct `next` relation is renderer-independent and lets a
panel arrange the primary flow top-to-bottom while retaining service and target
details when desired. Multiple incoming `next` edges truthfully represent a
later step reached after any supported prior branch.

## Alternatives Considered

Using a shared service node as the sequence step would merge calls from
different locations and owners. Flattening action order into metadata would
leave renderers to reconstruct control flow. Explicit join nodes would be
possible but add visual noise; direct reconverging edges are sufficient for the
current read-only view.

## Outcomes

The parser now creates action steps with stable owner-scoped identifiers and
links them with `next` edges. Conditional and parallel paths return their
terminal steps, allowing the following action to receive a direct reconverging
edge from each path. Parallel branches retain indexed locations, so their steps
and service targets remain distinct. Shared service nodes remain optional
technical detail.

## Related

- [Feature: Dependency Exploration](../intent/feature-dependency-exploration.md)
- [Decision: Graph-Based Relationship Model](002-graph-based-relationship-model.md)
- [Decision: Graph Contract and Service Projection](005-graph-contract-and-service-projection.md)
- [Pattern: Graph Construction with Stable IDs](../knowledge/patterns/graph-construction-stable-ids.md)
- [Pattern: Recursive Flow Parsing](../knowledge/patterns/recursive-flow-parsing.md)
- [Pattern: Sequential Action Steps](../knowledge/patterns/sequential-action-steps.md)

## Status

- **Created**: 2026-08-31 (Phase: Build)
- **Status**: Accepted
- **Note**: Implemented with renderer-independent `next` relations.
