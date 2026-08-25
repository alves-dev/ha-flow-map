"""Build a graph from HA runtime configuration snapshots."""

from __future__ import annotations

from ..parsers.automation import FlowParser, entity_node
from .model import Edge, Graph, Node


def _name(config, fallback):
    return config.get("alias") or config.get("name") or fallback


def build_graph(automations, scripts, scenes, states=()):
    graph = Graph()
    for state in states:
        entity_id = getattr(state, "entity_id", None)
        if entity_id:
            label = state.attributes.get("friendly_name", entity_id)
            graph.add_node(
                Node(
                    f"entity:{entity_id}",
                    "entity",
                    label,
                    {"domain": entity_id.split(".", 1)[0], "state": state.state},
                )
            )
    for entity_id, config in automations.items():
        node_id = f"automation:{entity_id.split('.', 1)[-1]}"
        graph.add_node(
            Node(
                node_id,
                "automation",
                _name(config, entity_id),
                {"entity_id": entity_id},
            )
        )
        FlowParser(graph, "automation_config").parse_flow(node_id, config)
    for entity_id, config in scripts.items():
        node_id = f"script:{entity_id.split('.', 1)[-1]}"
        graph.add_node(
            Node(node_id, "script", _name(config, entity_id), {"entity_id": entity_id})
        )
        FlowParser(graph, "script_config").parse_flow(node_id, config)
    for entity_id, config in scenes.items():
        node_id = f"scene:{entity_id.split('.', 1)[-1]}"
        graph.add_node(
            Node(node_id, "scene", _name(config, entity_id), {"entity_id": entity_id})
        )
        entities = config.get("entities", {}) if isinstance(config, dict) else {}
        for item in entities:
            if isinstance(item, str):
                target = entity_node(graph, item)
                graph.add_edge(
                    Edge(
                        "",
                        node_id,
                        target,
                        "targets",
                        "confirmed",
                        "scene_config",
                        "entities",
                    )
                )
    return graph
