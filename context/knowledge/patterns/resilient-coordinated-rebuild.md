# Pattern: Resilient Coordinated Rebuild

## Description

Coordinate index rebuilding through one asynchronous owner that debounces relevant host events, serializes concurrent rebuilds, reports status, and preserves a queryable fallback after failure.

## When to Use

Use when extending refresh triggers, adding a new configuration source, or changing the lifecycle of cached graph data.

## Pattern

Subscribe once, schedule a delayed replacement task for bursts of changes, guard rebuilds with an asynchronous lock, perform potentially expensive extraction off the event loop, and populate an empty graph/index if rebuilding fails.

## Example

```python
async def async_rebuild(self):
    async with self._lock:
        self.status = "indexing"
        try:
            automations, scripts, scenes = await self.hass.async_add_executor_job(
                lambda: (self._configs("automation"), self._configs("script"), self._configs("scene"))
            )
            self.graph = build_graph(automations, scripts, scenes, self.hass.states.async_all())
            self.index = GraphIndex(self.graph)
            self.status = "complete" if not self.warnings else "partial"
        except Exception as err:
            self.status = "failed"
            self.warnings.append({"source": "index", "message": str(err)})
            if self.graph is None:
                self.graph = Graph()
                self.index = GraphIndex(self.graph)
```

## Files Using This Pattern

- `custom_components/ha_flow_map/coordinator.py` — owns event subscriptions, debounce scheduling, rebuild serialization, status, and cleanup.
- `tests/test_coordinator.py` — tests complete rebuild, failure fallback, debounce, and teardown behavior.

## Related

- [Decision: Home Assistant Integration Boundary](../../decisions/003-home-assistant-integration-boundary.md)
- [Feature: Index Refresh and Availability Feedback](../../intent/feature-index-refresh.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
