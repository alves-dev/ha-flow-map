"""Safe extraction of entity references from templates; templates are never rendered."""

from __future__ import annotations

import re

ENTITY_RE = re.compile(r"\b[a-z_][a-z0-9_]*\.[a-zA-Z0-9_]+\b")


def references(value):
    if not isinstance(value, str):
        return [], False
    dynamic = "{{" in value or "{%" in value
    return sorted(set(ENTITY_RE.findall(value))), dynamic
