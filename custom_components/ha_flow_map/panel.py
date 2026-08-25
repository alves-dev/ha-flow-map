"""Panel registration."""

from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig

from .const import PANEL_COMPONENT, PANEL_URL


async def async_register_panel(hass):
    if hass.data.get("ha_flow_map_panel"):
        return
    hass.data["ha_flow_map_panel"] = True
    path = Path(__file__).parent / "frontend" / "ha-flow-map.js"
    # The panel is a module and imports its small, testable graph helper.
    # Serve the frontend directory so relative module imports are available too.
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/ha_flow_map", str(path.parent), False)]
    )
    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=PANEL_URL,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title="Flow Map",
        sidebar_icon="mdi:graph-outline",
        module_url=f"/ha_flow_map/ha-flow-map.js?v={path.stat().st_mtime_ns}",
        embed_iframe=False,
        require_admin=False,
    )
