"""Recursive parser for automation and script YAML-like configuration."""

from __future__ import annotations

from typing import Any

from ..graph.model import Edge, Node
from .template import references

CONTROL_KEYS = {
    "choose",
    "if",
    "then",
    "else",
    "repeat",
    "parallel",
    "sequence",
    "wait_for_trigger",
    "delay",
    "wait_template",
}


def entity_node(graph, entity_id):
    return graph.add_node(
        Node(
            f"entity:{entity_id}",
            "entity",
            entity_id,
            {"domain": entity_id.split(".", 1)[0]},
        )
    )


class FlowParser:
    def __init__(self, graph, source_kind="automation_config"):
        self.graph = graph
        self.source_kind = source_kind
        self._sequence = 0

    def edge(
        self, source, target, relation, location, confidence="confirmed", metadata=None
    ):
        self.graph.add_edge(
            Edge(
                "",
                source,
                target,
                relation,
                confidence,
                self.source_kind,
                location,
                metadata or {},
            )
        )

    def _struct(self, parent, kind, label, location):
        self._sequence += 1
        node_id = f"{parent}:{kind}:{self._sequence}"
        self.graph.add_node(Node(node_id, kind, label, {"location": location}))
        self.edge(parent, node_id, "contains", location)
        return node_id

    def _entity_values(self, value):
        if isinstance(value, str):
            refs, dynamic = references(value)
            return refs, dynamic
        if isinstance(value, list):
            refs = []
            dynamic = False
            for item in value:
                a, b = self._entity_values(item)
                refs.extend(a)
                dynamic |= b
            return refs, dynamic
        return [], False

    def target(self, owner, target, relation, location):
        if not isinstance(target, dict):
            return
        values = target.get("entity_id", target.get("entity_ids"))
        refs, dynamic = self._entity_values(values)
        for entity_id in refs:
            target_id = entity_node(self.graph, entity_id)
            self.edge(
                owner,
                target_id,
                relation,
                location,
                "dynamic" if dynamic else "confirmed",
            )
        for field, kind in (("device_id", "device"), ("area_id", "area")):
            values = target.get(field)
            if not values:
                continue
            for value in values if isinstance(values, list) else [values]:
                node_id = f"{kind}:{value}"
                self.graph.add_node(Node(node_id, kind, str(value)))
                self.edge(
                    owner,
                    node_id,
                    relation if relation == "targets" else "targets",
                    location,
                )

    def condition(self, owner, config, location):
        items = config if isinstance(config, list) else [config]
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            node = self._struct(
                owner,
                "condition",
                item.get("condition", "condition"),
                f"{location}[{index}]",
            )
            values, dynamic = self._entity_values(
                item.get("entity_id", item.get("entity_ids"))
            )
            for entity_id in values:
                self.edge(
                    entity_node(self.graph, entity_id),
                    node,
                    "used_in_condition",
                    f"{location}[{index}]",
                    "dynamic" if dynamic else "confirmed",
                )
            self.target(
                node,
                {key: item[key] for key in ("device_id", "area_id") if key in item},
                "used_in_condition",
                f"{location}[{index}]",
            )
            for key in ("conditions", "condition"):
                nested = item.get(key)
                if isinstance(nested, (dict, list)) and nested is not item:
                    self.condition(node, nested, f"{location}[{index}].{key}")
            for value in item.values():
                refs, dynamic = self._entity_values(value)
                for entity in refs:
                    self.edge(
                        node,
                        entity_node(self.graph, entity),
                        "reads_state",
                        location,
                        "dynamic" if dynamic else "confirmed",
                    )

    def triggers(self, owner, config, location, relation="triggers"):
        for index, item in enumerate(config if isinstance(config, list) else [config]):
            if not isinstance(item, dict):
                continue
            values = item.get("entity_id", item.get("entity_ids"))
            refs, dynamic = self._entity_values(values)
            for entity_id in refs:
                self.edge(
                    entity_node(self.graph, entity_id),
                    owner,
                    relation,
                    f"{location}[{index}]",
                    "dynamic" if dynamic else "confirmed",
                )
            # Device and area triggers have no entity reference but remain discoverable.
            self.target(
                owner,
                {key: item[key] for key in ("device_id", "area_id") if key in item},
                "triggers",
                f"{location}[{index}]",
            )
            if item.get("trigger") == "event" and item.get("event_type"):
                eid = f"event:{item['event_type']}"
                self.graph.add_node(Node(eid, "event", item["event_type"]))
                self.edge(eid, owner, "listens_event", f"{location}[{index}]")

    def actions(self, owner, config, location="actions"):
        for index, action in enumerate(
            config if isinstance(config, list) else [config]
        ):
            if not isinstance(action, dict):
                continue
            loc = f"{location}[{index}]"
            current = owner
            if "delay" in action or "wait_template" in action:
                current = self._struct(owner, "delay", "Delay / wait", loc)
            if "wait_for_trigger" in action:
                current = self._struct(owner, "delay", "Wait for trigger", loc)
                self.triggers(
                    current,
                    action["wait_for_trigger"],
                    loc + ".wait_for_trigger",
                    "waits_for",
                )
            if "condition" in action and not any(
                key in action for key in ("if", "choose")
            ):
                self.condition(owner, action, loc)
                continue
            if "if" in action:
                branch = self._struct(owner, "branch", "If", loc)
                self.condition(branch, action["if"], loc + ".if")
                self.actions(branch, action.get("then", []), loc + ".then")
                self.actions(branch, action.get("else", []), loc + ".else")
            if "choose" in action:
                branch = self._struct(owner, "branch", "Choose", loc)
                for choice_index, choice in enumerate(
                    action["choose"] if isinstance(action["choose"], list) else []
                ):
                    option = self._struct(
                        branch,
                        "branch",
                        f"Option {choice_index + 1}",
                        f"{loc}.choose[{choice_index}]",
                    )
                    self.condition(
                        option,
                        choice.get("conditions", []),
                        f"{loc}.choose[{choice_index}].conditions",
                    )
                    self.actions(
                        option,
                        choice.get("sequence", []),
                        f"{loc}.choose[{choice_index}].sequence",
                    )
                self.actions(branch, action.get("default", []), loc + ".default")
            for key, label in (("sequence", "Sequence"), ("parallel", "Parallel")):
                if key in action:
                    branch = self._struct(owner, "branch", label, loc + "." + key)
                    sequences = action[key] if key == "parallel" else [action[key]]
                    for sequence in sequences:
                        self.actions(branch, sequence, loc + "." + key)
            if "repeat" in action:
                branch = self._struct(owner, "branch", "Repeat", loc)
                repeat = action["repeat"] if isinstance(action["repeat"], dict) else {}
                self.condition(
                    branch,
                    repeat.get("while", repeat.get("until", [])),
                    loc + ".repeat",
                )
                self.actions(
                    branch, repeat.get("sequence", []), loc + ".repeat.sequence"
                )
            service = action.get("action", action.get("service"))
            if not isinstance(service, str):
                continue
            service_id = f"service:{service}"
            self.graph.add_node(
                Node(
                    service_id,
                    "service",
                    service,
                    {"domain": service.split(".", 1)[0] if "." in service else service},
                )
            )
            self.edge(
                current,
                service_id,
                "calls_service",
                loc,
                metadata={
                    "service": service,
                    "data": _safe_data(
                        action.get("data", action.get("service_data", {}))
                    ),
                },
            )
            self.target(
                service_id, action.get("target", action.get("data", {})), "targets", loc
            )
            domain, _, object_id = service.partition(".")
            if domain in {"script", "automation", "scene"} and object_id not in {
                "turn_on",
                "turn_off",
                "toggle",
                "reload",
            }:
                target_id = f"{domain}:{object_id}"
                self.graph.add_node(Node(target_id, domain, object_id))
                relation = {
                    "script": "calls_script",
                    "automation": "calls_automation",
                    "scene": "activates_scene",
                }[domain]
                self.edge(current, target_id, relation, loc)
            # script.turn_on / scene.turn_on refer to their target rather than the
            # service name. Preserve both the service call and its semantic target.
            target_config = action.get("target", action.get("data", {}))
            if isinstance(target_config, dict):
                target_refs, _ = self._entity_values(
                    target_config.get("entity_id", target_config.get("entity_ids"))
                )
                for target_ref in target_refs:
                    target_domain, _, target_object = target_ref.partition(".")
                    if target_domain in {"script", "automation", "scene"}:
                        target_id = f"{target_domain}:{target_object}"
                        self.graph.add_node(
                            Node(target_id, target_domain, target_object)
                        )
                        relation = {
                            "script": "calls_script",
                            "automation": "calls_automation",
                            "scene": "activates_scene",
                        }[target_domain]
                        self.edge(current, target_id, relation, loc)
            if service == "event.fire":
                event = action.get("data", {}).get("event_type")
                if isinstance(event, str):
                    eid = f"event:{event}"
                    self.graph.add_node(Node(eid, "event", event))
                    self.edge(current, eid, "fires_event", loc)

    def parse_flow(self, node_id, config):
        self.triggers(
            node_id, config.get("triggers", config.get("trigger", [])), "triggers"
        )
        self.condition(
            node_id, config.get("conditions", config.get("condition", [])), "conditions"
        )
        self.actions(
            node_id,
            config.get("actions", config.get("action", config.get("sequence", []))),
            "actions",
        )


def _safe_data(value: Any):
    """Return explanatory metadata without exposing nested secret values."""
    secret_keys = {
        "password",
        "token",
        "api_key",
        "access_token",
        "authorization",
        "secret",
    }

    def sanitize(item, key=""):
        if key.lower() in secret_keys:
            return "<redacted>"
        if isinstance(item, str):
            return "<template>" if "{{" in item or "{%" in item else item
        if isinstance(item, dict):
            return {
                str(name): sanitize(nested, str(name)) for name, nested in item.items()
            }
        if isinstance(item, list):
            return [sanitize(nested) for nested in item]
        return item

    return sanitize(value) if isinstance(value, dict) else {}
