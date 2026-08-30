# Decision: Tech Stack

## Context

HA Flow Map must run as a Home Assistant custom integration, expose a browser-based sidebar experience, and be maintainable with automated validation.

## Decision

Use Python 3.14 with Home Assistant 2026.6 as the integration runtime, a native browser ES-module frontend, and `uv` for dependency management. Use pytest (including asyncio and coverage support) for Python checks, Node.js for frontend checks, Ruff for linting, and SonarQube configuration for quality analysis.

## Rationale

The manifest and project configuration bind the integration to Home Assistant and its frontend/http capabilities. A dependency-free native module keeps the panel small and directly compatible with the host frontend. The configured tooling provides repeatable linting, unit testing, coverage, and quality reporting. Rationale is inferred from repository configuration and implementation.

## Alternatives Considered

Alternatives are not documented in the existing codebase. Plausible alternatives include a separately bundled frontend framework, another Python environment manager, or no standalone frontend tests; none are selected by the current implementation.

## Outcomes

Outcomes to be documented as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Home Assistant Integration Boundary](003-home-assistant-integration-boundary.md)

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation
