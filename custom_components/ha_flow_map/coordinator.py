"""Non-blocking coordinator which adapts HA runtime entities to graph inputs."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import logging

from homeassistant.core import EVENT_HOMEASSISTANT_STARTED, callback
from homeassistant.helpers.event import async_call_later

from .graph.builder import build_graph
from .graph.index import GraphIndex
from .graph.model import Graph

_LOGGER = logging.getLogger(__name__)


class FlowMapCoordinator:
    def __init__(self, hass):
        self.hass = hass
        self.graph = None
        self.index = None
        self.last_indexed = None
        self.duration_ms = 0
        self.status = "not_indexed"
        self.warnings = []
        self._lock = asyncio.Lock()
        self._unsubscribers = []
        self._pending_rebuild = None

    def async_listen_for_changes(self):
        """Debounce known configuration reloads without inspecting private storage."""
        if self._unsubscribers:
            return

        @callback
        def _service_called(event):
            data = event.data
            if data.get("domain") in {"automation", "script", "scene"} and data.get(
                "service"
            ) in {"reload", "create", "update", "delete"}:
                self._schedule_rebuild()

        self._unsubscribers.append(
            self.hass.bus.async_listen("call_service", _service_called)
        )
        self._unsubscribers.append(
            self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED,
                lambda _event: self._schedule_rebuild(),
            )
        )

    @callback
    def _schedule_rebuild(self):
        if self._pending_rebuild:
            self._pending_rebuild()
        self._pending_rebuild = async_call_later(
            self.hass, 2, self._async_debounced_rebuild
        )

    async def _async_debounced_rebuild(self, _now):
        self._pending_rebuild = None
        await self.async_rebuild()

    async def async_shutdown(self):
        if self._pending_rebuild:
            self._pending_rebuild()
            self._pending_rebuild = None
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    def _entities(self, domain):
        """Adapter for HA EntityComponents; kept here to contain runtime details."""
        try:
            if domain == "automation":
                from homeassistant.components.automation import DATA_COMPONENT

                component = self.hass.data.get(DATA_COMPONENT)
            elif domain == "scene":
                from homeassistant.components.scene import DATA_COMPONENT

                component = self.hass.data.get(DATA_COMPONENT)
            else:
                component = self.hass.data.get(domain)
            # EntityComponent keeps a public registry of all loaded entity
            # components. Some HA versions do not retain a component under the
            # domain-specific data key after a YAML reload, so use it as a
            # compatibility fallback.
            if component is None:
                from homeassistant.helpers.entity_component import DATA_INSTANCES

                component = self.hass.data.get(DATA_INSTANCES, {}).get(domain)
            return getattr(component, "entities", ()) if component else ()
        except (ImportError, AttributeError, KeyError) as err:
            self.warnings.append(
                {
                    "source": domain,
                    "message": f"Unable to access {domain} configuration: {err}",
                }
            )
            return ()

    def _configs(self, domain):
        values = {}
        for entity in self._entities(domain):
            raw = getattr(entity, "raw_config", None)
            entity_id = getattr(entity, "entity_id", None)
            if entity_id and isinstance(raw, dict):
                values[entity_id] = raw
        return values

    async def async_rebuild(self):
        async with self._lock:
            started = self.hass.loop.time()
            self.status = "indexing"
            self.warnings = []
            try:
                # Parsing happens in the executor so a large installation never
                # monopolizes HA's event loop.
                automations, scripts, scenes = await self.hass.async_add_executor_job(
                    lambda: (
                        self._configs("automation"),
                        self._configs("script"),
                        self._configs("scene"),
                    )
                )
                self.graph = build_graph(
                    automations, scripts, scenes, self.hass.states.async_all()
                )
                self.graph.warnings.extend(self.warnings)
                self.index = GraphIndex(self.graph)
                self.status = "complete" if not self.warnings else "partial"
            except Exception as err:  # a bad integration must not break HA startup
                _LOGGER.exception("Flow Map index failed")
                self.status = "failed"
                self.warnings.append({"source": "index", "message": str(err)})
                if self.graph is None:
                    self.graph = Graph()
                    self.index = GraphIndex(self.graph)
            self.duration_ms = round((self.hass.loop.time() - started) * 1000)
            self.last_indexed = datetime.now(UTC).isoformat()

    def status_data(self):
        return {
            "status": self.status,
            "indexed_at": self.last_indexed,
            "duration_ms": self.duration_ms,
            "node_count": len(self.graph.nodes) if self.graph else 0,
            "edge_count": len(self.graph.edges) if self.graph else 0,
            "warnings": self.warnings,
        }
