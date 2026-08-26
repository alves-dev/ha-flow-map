import inspect
import unittest
from unittest.mock import AsyncMock, patch

from custom_components.ha_flow_map.const import DOMAIN
from custom_components.ha_flow_map.graph.builder import build_graph
from custom_components.ha_flow_map.graph.index import GraphIndex
from custom_components.ha_flow_map.websocket_api import (
    async_register_websocket_commands,
)


class FakeConnection:
    def __init__(self):
        self.results = []
        self.errors = []

    def send_result(self, message_id, result):
        self.results.append((message_id, result))

    def send_error(self, message_id, code, message):
        self.errors.append((message_id, code, message))


class FakeCoordinator:
    def __init__(self):
        self.graph = build_graph({"automation.office": {"alias": "Office"}}, {}, {})
        self.index = GraphIndex(self.graph)
        self.async_rebuild = AsyncMock()

    def status_data(self):
        return {"status": "complete", "node_count": len(self.graph.nodes)}


class FakeHass:
    def __init__(self):
        self.data = {DOMAIN: {}}


class WebsocketApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.hass = FakeHass()
        self.commands = {}
        self.register = patch(
            "custom_components.ha_flow_map.websocket_api.websocket_api.async_register_command",
            side_effect=lambda _hass, command: self.commands.setdefault(
                command._ws_command,
                command,
            ),
        )
        self.register.start()
        async_register_websocket_commands(self.hass)
        self.addCleanup(self.register.stop)
        self.coordinator = FakeCoordinator()
        self.hass.data[DOMAIN]["entry"] = self.coordinator
        self.connection = FakeConnection()

    async def call(self, command, message):
        await inspect.unwrap(self.commands[command])(
            self.hass,
            self.connection,
            {"type": command, **message},
        )

    async def test_search_status_and_node_commands(self):
        await self.call("ha_flow_map/search", {"id": 1, "query": "office", "limit": 50})
        await self.call("ha_flow_map/status", {"id": 2})
        await self.call("ha_flow_map/node", {"id": 3, "node_id": "automation:office"})

        self.assertEqual(
            self.connection.results[0][1]["items"][0]["id"], "automation:office"
        )
        self.assertEqual(self.connection.results[1][1]["status"], "complete")
        self.assertEqual(self.connection.results[2][1]["id"], "automation:office")

    async def test_missing_node_returns_not_found(self):
        await self.call("ha_flow_map/relations", {"id": 1, "node_id": "missing"})

        self.assertEqual(
            self.connection.errors, [(1, "not_found", "Flow Map node not found")]
        )

    async def test_rebuild_returns_updated_status(self):
        await self.call("ha_flow_map/rebuild", {"id": 1})

        self.coordinator.async_rebuild.assert_awaited_once()
        self.assertEqual(self.connection.results[0][1]["status"], "complete")
