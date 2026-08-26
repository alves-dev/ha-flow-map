# Development

## Prerequisites

- Python 3.14.2 or later
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 or later for the frontend checks

## Set up the workspace

```sh
uv sync --all-groups --frozen
```

Use a Home Assistant development environment when manually testing the
configuration flow and sidebar panel. The integration reads the runtime
automation, script and scene configuration; do not use a production instance
for experimental changes.

## Local validation

```sh
uv run ruff check custom_components tests
uv run pytest --cov=custom_components/ha_flow_map --cov-report=xml --cov-report=term
node tests/test_frontend.mjs
python3 /home/alves-dev/projects/others/infra/skills/home-assistant-integration-standards/scripts/validate_integration_structure.py .
```

Before a release, also run the HACS and Hassfest workflows. Keep the manifest,
changelog, compatibility matrix and project version aligned when changing the
integration version.
