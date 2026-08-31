# AGENTS.md

## Setup Commands

- Install: `uv sync --all-groups --frozen`
- Lint: `uv run ruff check custom_components tests`
- Test: `uv run pytest --cov=custom_components/ha_flow_map --cov-report=xml --cov-report=term`
- Frontend test: `node tests/test_frontend.mjs`
- Structure check: `python3 /home/alves-dev/projects/others/infra/skills/home-assistant-integration-standards/scripts/validate_integration_structure.py .`
- Manual Home Assistant deployment: `dev/copy-to-core.sh`
- Start/stop shared Home Assistant: `dev/start-ha.sh` / `dev/stop-ha.sh`

Use Python 3.14.2+, `uv`, and Node.js 22+ as documented by the project. Do not use a production Home Assistant instance for experimental testing.

## Code Style

- Follow Ruff with an 88-character line length and Python 3.14 target.
- Keep Home Assistant runtime access contained in the coordinator; retain compatibility fallbacks where applicable.
- Use typed, namespaced graph identifiers and stable edge construction.
- Keep frontend graph helpers independently testable.
- Follow patterns from `@context/knowledge/patterns/`.

## Context Files to Load

Before starting any work, load relevant context:

- `@context/.context-mesh-framework.md` (framework rules)
- `@context/intent/project-intent.md` (always)
- `@context/intent/feature-*.md` (for the affected feature)
- `@context/decisions/*.md` (relevant decisions)
- `@context/knowledge/patterns/*.md` (patterns to follow)

## Project Structure

```text
root/
├── AGENTS.md
├── context/
│   ├── intent/
│   ├── decisions/
│   ├── knowledge/
│   ├── agents/
│   └── evolution/
├── custom_components/ha_flow_map/
├── tests/
├── docs/
└── dev/
```

## AI Agent Rules

### Always

- Load relevant Context Mesh records before planning or implementing.
- Follow accepted decisions and existing patterns.
- Use Plan, Approve, Execute for material changes.
- Update Context Mesh after functional or technical changes.

### Never

- Put technical implementation details in feature intent files.
- Ignore documented decisions or use anti-patterns from `@context/knowledge/anti-patterns/`.
- Leave intent, decisions, patterns, or changelog stale after a material change.

### After Any Changes

- Update the affected feature intent when user-visible behavior changed.
- Record a new or changed technical choice in `context/decisions/`.
- Add or update a pattern when reusable implementation guidance changed.
- Add decision outcomes or learning when results differ from the intended approach.
- Update `context/evolution/changelog.md`.

## Definition of Done (Build Phase)

- [ ] Relevant intent and technical decision records are accurate before implementation.
- [ ] Code follows documented patterns and accepted decisions.
- [ ] Appropriate linting and tests pass.
- [ ] Context records and bidirectional links are updated.
- [ ] Changelog is updated.
