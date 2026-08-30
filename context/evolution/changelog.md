# Changelog

## [Unreleased]

### Changed

- Flow Map now derives its panel, graph, and exported SVG/PNG colors from the
  active Home Assistant theme instead of using a fixed dark palette.

## [Current State] - Context Mesh Added

### Existing Features (documented)

- Relationship discovery — exposes supported configuration dependencies and their confidence.
- Dependency exploration — search and inspect nearby inbound and outbound relationships.
- Change-impact summaries — identify connected automations, scripts, and scenes.
- Index refresh and availability feedback — keep the map current and communicate index state.

### Tech Stack (documented)

- Python 3.14, Home Assistant 2026.6 custom integration, and `uv`.
- Native browser ES-module sidebar panel.
- Pytest, Ruff, Node.js checks, and SonarQube configuration.

### Patterns Identified

- Graph construction with stable IDs.
- Recursive flow parsing.
- Bounded graph querying.
- Resilient coordinated rebuild.
- Panel WebSocket interaction.

### Historical Baseline Preserved

- Legacy MVP scope, deferred roadmap, and gaps against the current implementation are retained in [Legacy MVP Specification Baseline](legacy-mvp-spec-baseline.md).

---

*Context Mesh added: 2026-08-30*
*This changelog documents the state when Context Mesh was added.*
*Future changes will be tracked below.*
