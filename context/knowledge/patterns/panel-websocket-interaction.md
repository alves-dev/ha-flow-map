# Pattern: Panel WebSocket Interaction

## Description

Expose small, validated backend commands and keep the panel focused on calling those commands, rendering returned graph data, and handling user interaction.

## When to Use

Use when adding an action, query, or status capability to the Flow Map panel.

## Pattern

Register a schema-validated command in the backend, return a predictable result or named error, apply authorization where needed, then call the command from the panel through a single helper method.

## Example

```python
@websocket_api.websocket_command({vol.Required("type"): "ha_flow_map/rebuild"})
@websocket_api.require_admin
@websocket_api.async_response
async def rebuild(_hass, connection, msg):
    coordinator = _coordinator(_hass)
    if not coordinator:
        connection.send_error(msg["id"], "not_configured", "Configure HA Flow Map first")
        return
    await coordinator.async_rebuild()
    connection.send_result(msg["id"], coordinator.status_data())
```

```javascript
call(type, payload = {}) {
  return this._hass.callWS({ type, ...payload });
}
```

## Files Using This Pattern

- `custom_components/ha_flow_map/websocket_api.py` — command schemas, bounded inputs, result handling, and administrator-only rebuild.
- `custom_components/ha_flow_map/frontend/ha-flow-map.js` — central panel call helper and UI event handlers.
- `custom_components/ha_flow_map/panel.py` — serves and registers the panel module.

## Related

- [Decision: Home Assistant Integration Boundary](../../decisions/003-home-assistant-integration-boundary.md)
- [Decision: Graph Contract and Service Projection](../../decisions/005-graph-contract-and-service-projection.md)
- [Feature: Dependency Exploration](../../intent/feature-dependency-exploration.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
