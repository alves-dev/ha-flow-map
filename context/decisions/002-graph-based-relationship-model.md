# Decision: Graph-Based Relationship Model

## Context

The product needs to represent many kinds of relationships between configuration owners, smart-home items, events, and intermediate flow logic, then answer search, neighborhood, and impact queries.

## Decision

Represent discovered relationships with a library-neutral directed graph of typed nodes and edges. Use namespaced stable node identifiers, deterministic edge identifiers, reverse indexes, and a recursive parser that models nested control flow.

## Rationale

The graph model separates collection and transport concerns from Home Assistant runtime APIs, while typed relations preserve useful semantics for presentation and queries. Deterministic IDs prevent refreshes from producing arbitrary API identities. Reverse indexes make inbound and outbound traversal direct. The rationale is inferred from graph, parser, and index implementation.

## Alternatives Considered

Alternatives are not documented in the existing codebase. Possible approaches include returning raw configuration fragments to the panel, using an external graph database, or flattening relationships into a simple list; the implementation instead retains an in-memory, typed graph.

## Outcomes

Outcomes to be documented as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Relationship Discovery](../intent/feature-relationship-discovery.md)
- [Feature: Change-Impact Summaries](../intent/feature-impact-summaries.md)
- [Pattern: Graph Construction with Stable IDs](../knowledge/patterns/graph-construction-stable-ids.md)
- [Pattern: Recursive Flow Parsing](../knowledge/patterns/recursive-flow-parsing.md)
- [Pattern: Bounded Graph Querying](../knowledge/patterns/bounded-graph-querying.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
