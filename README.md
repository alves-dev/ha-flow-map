# HA Flow Map

Read-only Home Assistant custom integration that indexes explicit relationships in
automations, scripts and scenes, then exposes them through a `Flow Map` panel.

## Installation

Copy `custom_components/ha_flow_map` into the Home Assistant configuration
directory's `custom_components` folder, restart Home Assistant, then add **HA
Flow Map** from **Settings → Devices & services → Add integration**. The panel
appears in the sidebar after configuration.

## What the MVP indexes

- State/entity triggers, conditions and explicit action targets.
- Nested `if`, `choose`, `repeat`, `parallel`, sequences, waits and delays.
- Script, automation, scene, service and event calls.
- Scene entity states when their configuration is available.
- Entity, device and area targets, with stable namespaced node IDs.

The panel searches the index, expands inbound/outbound neighborhoods (depth
1–3), distinguishes confirmed and dynamic references, and can hide/show service
nodes without changing the stored graph. Rebuild is administrator-only.

## Deliberate MVP limits

The integration does not render or execute Jinja templates. Literal entity IDs
found inside templates are retained and marked `dynamic`; unresolved template
results are therefore never shown as confirmed. It currently uses the runtime
automation/script/scene configuration exposed by Home Assistant and reports a
partial index if a source cannot be read.

Dashboard configurations, custom cards, execution traces/history and external
callers (REST, Node-RED, voice assistants, etc.) are not statically indexed in
this MVP. Their absence from the map means only that no supported source
discovered a relation.

## Verification

The parser tests in `tests/test_parsers.py` cover recursive control-flow blocks,
dynamic templates, calls, scene targets, reverse indexes and bounded traversal.
They are intentionally independent of a running HA instance.

## License

This project is licensed under the [MIT License](LICENSE).
