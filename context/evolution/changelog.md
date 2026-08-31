# Changelog

## [Unreleased]

### Added

- Focused flow now shows direct triggers and all direct output items of a
  selected automation, script, or scene without increasing neighborhood depth
  or including unrelated indirect relationships.
- Flow maps now model each configured action as an ordered step and reconnect
  supported conditional and parallel paths before the next configured action.
- Supported actions, conditions, and triggers now use safe Portuguese
  descriptions derived from explicit configuration and friendly graph labels.
- Flow connections now distinguish supported branches, parallel paths, and
  calls into another configuration; automation nodes show their current state
  and availability without representing execution history.

### Fixed

- Versioned the panel's local graph-helper import to prevent stale browser
  caches from loading an incompatible module after a panel update.

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
