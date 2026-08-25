"""Set up the HA Flow Map integration."""

from __future__ import annotations

from .const import DOMAIN

try:  # Keep the deterministic graph engine importable outside Home Assistant.
    from .coordinator import FlowMapCoordinator
    from .panel import async_register_panel
    from .websocket_api import async_register_websocket_commands
except ImportError:
    FlowMapCoordinator = None
    async_register_panel = None
    async_register_websocket_commands = None


async def async_setup(hass, _config):
    """Set up shared commands and panel once."""
    hass.data.setdefault(DOMAIN, {})
    if async_register_websocket_commands:
        async_register_websocket_commands(hass)
        await async_register_panel(hass)
    return True


async def async_setup_entry(hass, entry):
    if FlowMapCoordinator is None:
        return False
    coordinator = FlowMapCoordinator(hass)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    coordinator.async_listen_for_changes()
    await coordinator.async_rebuild()
    return True


async def async_unload_entry(hass, entry):
    coordinator = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if coordinator:
        await coordinator.async_shutdown()
    return True
