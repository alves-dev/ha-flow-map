import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from custom_components.ha_flow_map.coordinator import FlowMapCoordinator


class FakeBus:
    def __init__(self):
        self.listeners = []
        self.once_listeners = []

    def async_listen(self, event_type, callback):
        self.listeners.append((event_type, callback))
        return lambda: self.listeners.remove((event_type, callback))

    def async_listen_once(self, event_type, callback):
        self.once_listeners.append((event_type, callback))
        return lambda: self.once_listeners.remove((event_type, callback))


class FakeHass:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.bus = FakeBus()
        self.states = SimpleNamespace(async_all=lambda: [])
        self.data = {
            "automation": SimpleNamespace(
                entities=[
                    SimpleNamespace(
                        entity_id="automation.office",
                        raw_config={
                            "alias": "Office",
                            "triggers": [
                                {
                                    "trigger": "state",
                                    "entity_id": "binary_sensor.motion",
                                }
                            ],
                        },
                    )
                ]
            ),
            "script": SimpleNamespace(entities=[]),
            "scene": SimpleNamespace(entities=[]),
        }

    async def async_add_executor_job(self, job):
        return job()


class CoordinatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_rebuild_creates_a_complete_index(self):
        coordinator = FlowMapCoordinator(FakeHass())

        await coordinator.async_rebuild()

        self.assertEqual(coordinator.status, "complete")
        self.assertIn("automation:office", coordinator.graph.nodes)
        self.assertEqual(coordinator.status_data()["node_count"], 2)

    async def test_failed_rebuild_keeps_an_empty_queryable_graph(self):
        coordinator = FlowMapCoordinator(FakeHass())

        with patch(
            "custom_components.ha_flow_map.coordinator.build_graph",
            side_effect=RuntimeError("bad config"),
        ):
            await coordinator.async_rebuild()

        self.assertEqual(coordinator.status, "failed")
        self.assertIsNotNone(coordinator.index)
        self.assertEqual(coordinator.status_data()["node_count"], 0)

    async def test_listeners_debounce_and_shutdown(self):
        hass = FakeHass()
        coordinator = FlowMapCoordinator(hass)
        callbacks = []

        with patch(
            "custom_components.ha_flow_map.coordinator.async_call_later",
            side_effect=lambda _hass, _delay, callback: (
                callbacks.append(callback) or (lambda: callbacks.remove(callback))
            ),
        ):
            coordinator.async_listen_for_changes()
            service_callback = hass.bus.listeners[0][1]
            service_callback(
                SimpleNamespace(data={"domain": "automation", "service": "reload"})
            )
            service_callback(
                SimpleNamespace(data={"domain": "light", "service": "turn_on"})
            )

        self.assertEqual(len(callbacks), 1)
        await coordinator.async_shutdown()
        self.assertEqual(hass.bus.listeners, [])
        self.assertEqual(hass.bus.once_listeners, [])
