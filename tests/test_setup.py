import importlib
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.ha_flow_map.config_flow import FlowMapConfigFlow
from custom_components.ha_flow_map.const import DOMAIN

integration = importlib.import_module("custom_components.ha_flow_map")


class SetupTests(unittest.IsolatedAsyncioTestCase):
    async def test_setup_registers_panel_and_websocket_commands(self):
        hass = SimpleNamespace(data={})
        register_commands = MagicMock()
        register_panel = AsyncMock()

        with (
            patch.object(
                integration, "async_register_websocket_commands", register_commands
            ),
            patch.object(integration, "async_register_panel", register_panel),
        ):
            self.assertTrue(await integration.async_setup(hass, {}))

        self.assertIn(DOMAIN, hass.data)
        register_commands.assert_called_once_with(hass)
        register_panel.assert_awaited_once_with(hass)

    async def test_setup_entry_rebuilds_and_unloads_coordinator(self):
        hass = SimpleNamespace(data={DOMAIN: {}})
        coordinator = MagicMock()
        coordinator.async_rebuild = AsyncMock()
        coordinator.async_listen_for_changes = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry = SimpleNamespace(entry_id="entry")

        with patch.object(integration, "FlowMapCoordinator", return_value=coordinator):
            self.assertTrue(await integration.async_setup_entry(hass, entry))
            self.assertTrue(await integration.async_unload_entry(hass, entry))

        coordinator.async_listen_for_changes.assert_called_once()
        coordinator.async_rebuild.assert_awaited_once()
        coordinator.async_shutdown.assert_awaited_once()


class ConfigFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_user_step_shows_form_creates_entry_or_aborts(self):
        flow = FlowMapConfigFlow()
        flow._async_current_entries = MagicMock(return_value=[])
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        self.assertEqual(await flow.async_step_user(), {"type": "form"})
        self.assertEqual(await flow.async_step_user({}), {"type": "create_entry"})

        flow._async_current_entries.return_value = [object()]
        flow.async_abort = MagicMock(return_value={"type": "abort"})
        self.assertEqual(await flow.async_step_user(), {"type": "abort"})
