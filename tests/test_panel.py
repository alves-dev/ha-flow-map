import unittest
from unittest.mock import AsyncMock, patch

from custom_components.ha_flow_map.panel import async_register_panel


class FakeHTTP:
    def __init__(self):
        self.paths = []

    async def async_register_static_paths(self, paths):
        self.paths.extend(paths)


class FakeHass:
    def __init__(self):
        self.data = {}
        self.http = FakeHTTP()


class PanelTests(unittest.IsolatedAsyncioTestCase):
    async def test_registers_assets_and_panel_once(self):
        hass = FakeHass()
        register = AsyncMock()

        with patch(
            "custom_components.ha_flow_map.panel.panel_custom.async_register_panel",
            register,
        ):
            await async_register_panel(hass)
            await async_register_panel(hass)

        self.assertTrue(hass.data["ha_flow_map_panel"])
        self.assertEqual(len(hass.http.paths), 1)
        register.assert_awaited_once()
        self.assertIn("ha-flow-map.js?v=", register.await_args.kwargs["module_url"])
