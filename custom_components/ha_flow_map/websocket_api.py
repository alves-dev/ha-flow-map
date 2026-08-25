"""Authenticated, bounded WebSocket commands for the panel."""

from __future__ import annotations

from homeassistant.components import websocket_api
import voluptuous as vol

from .const import DOMAIN, MAX_DEPTH, MAX_EDGES, MAX_NODES


def _coordinator(hass):
    entries = hass.data.get(DOMAIN, {})
    return next(
        (
            value
            for value in entries.values()
            if hasattr(value, "async_rebuild") and hasattr(value, "index")
        ),
        None,
    )


def async_register_websocket_commands(hass):
    if hass.data[DOMAIN].get("commands_registered"):
        return
    hass.data[DOMAIN]["commands_registered"] = True

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "ha_flow_map/search",
            vol.Optional("query", default=""): str,
            vol.Optional("limit", default=50): vol.All(int, vol.Range(min=1, max=100)),
        }
    )
    @websocket_api.async_response
    async def search(_hass, connection, msg):
        coordinator = _coordinator(_hass)
        connection.send_result(
            msg["id"],
            {
                "items": coordinator.index.search(msg["query"], msg["limit"])
                if coordinator and coordinator.index
                else []
            },
        )

    @websocket_api.websocket_command({vol.Required("type"): "ha_flow_map/status"})
    @websocket_api.async_response
    async def status(_hass, connection, msg):
        coordinator = _coordinator(_hass)
        connection.send_result(
            msg["id"],
            coordinator.status_data() if coordinator else {"status": "not_configured"},
        )

    common_schema = {
        vol.Required("node_id"): str,
        vol.Optional("direction", default="both"): vol.In(
            ["inbound", "outbound", "both"]
        ),
        vol.Optional("depth", default=1): vol.All(int, vol.Range(min=1, max=MAX_DEPTH)),
        vol.Optional("max_nodes", default=MAX_NODES): vol.All(
            int, vol.Range(min=1, max=1000)
        ),
        vol.Optional("max_edges", default=MAX_EDGES): vol.All(
            int, vol.Range(min=1, max=2000)
        ),
    }

    async def _graph_data(_hass, connection, msg):
        coordinator = _coordinator(_hass)
        if (
            not coordinator
            or not coordinator.index
            or msg["node_id"] not in coordinator.graph.nodes
        ):
            connection.send_error(msg["id"], "not_found", "Flow Map node not found")
            return
        if msg["type"] == "ha_flow_map/node":
            connection.send_result(
                msg["id"], coordinator.graph.nodes[msg["node_id"]].as_dict()
            )
            return
        connection.send_result(
            msg["id"],
            coordinator.index.neighborhood(
                msg["node_id"],
                msg["direction"],
                msg["depth"],
                msg["max_nodes"],
                msg["max_edges"],
            ),
        )

    @websocket_api.websocket_command(
        {vol.Required("type"): "ha_flow_map/node", **common_schema}
    )
    @websocket_api.async_response
    async def node(_hass, connection, msg):
        await _graph_data(_hass, connection, msg)

    @websocket_api.websocket_command(
        {vol.Required("type"): "ha_flow_map/relations", **common_schema}
    )
    @websocket_api.async_response
    async def relations(_hass, connection, msg):
        await _graph_data(_hass, connection, msg)

    @websocket_api.websocket_command(
        {vol.Required("type"): "ha_flow_map/flow", **common_schema}
    )
    @websocket_api.async_response
    async def flow(_hass, connection, msg):
        await _graph_data(_hass, connection, msg)

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "ha_flow_map/impact",
            vol.Required("node_id"): str,
            vol.Optional("max_depth", default=12): vol.All(int, vol.Range(min=1, max=20)),
        }
    )
    @websocket_api.async_response
    async def impact(_hass, connection, msg):
        coordinator = _coordinator(_hass)
        if (
            not coordinator
            or not coordinator.index
            or msg["node_id"] not in coordinator.graph.nodes
        ):
            connection.send_error(msg["id"], "not_found", "Flow Map node not found")
            return
        connection.send_result(
            msg["id"], coordinator.index.impact(msg["node_id"], msg["max_depth"])
        )

    @websocket_api.websocket_command({vol.Required("type"): "ha_flow_map/rebuild"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def rebuild(_hass, connection, msg):
        coordinator = _coordinator(_hass)
        if not coordinator:
            connection.send_error(
                msg["id"], "not_configured", "Configure HA Flow Map first"
            )
            return
        await coordinator.async_rebuild()
        connection.send_result(msg["id"], coordinator.status_data())

    for command in (search, status, node, relations, flow, impact, rebuild):
        websocket_api.async_register_command(hass, command)
