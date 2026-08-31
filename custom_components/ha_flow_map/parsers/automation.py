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

    def _struct(self, parent, kind, label, location, relation="contains"):
        parents = [parent] if isinstance(parent, str) else list(parent)
        self._sequence += 1
        node_owner = parents[0] if len(parents) == 1 else self._flow_owner
        node_id = f"{node_owner}:{kind}:{self._sequence}"
        self.graph.add_node(Node(node_id, kind, label, {"location": location}))
        for item in parents:
            self.edge(item, node_id, relation, location)
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

    def target(self, owner, target, relation, location, metadata=None):
        if not isinstance(target, dict):
            return
        values = target.get("entity_id", target.get("entity_ids"))
        refs, dynamic = self._entity_values(values)
        for entity_id in refs:
            target_id = entity_node(self.graph, entity_id)
            self.edge(
                target_id if relation == "triggers" else owner,
                owner if relation == "triggers" else target_id,
                relation,
                location,
                "dynamic" if dynamic else "confirmed",
                metadata,
            )
        for field, kind in (("device_id", "device"), ("area_id", "area")):
            values = target.get(field)
            if not values:
                continue
            for value in values if isinstance(values, list) else [values]:
                node_id = f"{kind}:{value}"
                self.graph.add_node(Node(node_id, kind, str(value)))
                self.edge(
                    node_id if relation == "triggers" else owner,
                    owner if relation == "triggers" else node_id,
                    # A device/area can be the source of a trigger just as an
                    # entity can.  Preserve that relationship so the graph and
                    # UI do not mistake it for an action target.
                    relation if relation in {"targets", "triggers"} else "targets",
                    location,
                    metadata=metadata,
                )

    def condition(self, owner, config, location, relation="contains"):
        created = []
        items = config if isinstance(config, list) else [config]
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            node = self._struct(
                owner,
                "condition",
                item.get("condition", "condition"),
                f"{location}[{index}]",
                relation,
            )
            created.append(node)
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
                    created.extend(
                        self.condition(node, nested, f"{location}[{index}].{key}")
                    )
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
        return created

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
            # Device-trigger automations place their selector under ``target``;
            # older forms keep it at the trigger's top level.
            target = item.get("target")
            self.target(
                owner,
                target if isinstance(target, dict) else item,
                "triggers",
                f"{location}[{index}]",
            )
            if item.get("trigger") == "event" and item.get("event_type"):
                eid = f"event:{item['event_type']}"
                self.graph.add_node(Node(eid, "event", item["event_type"]))
                self.edge(eid, owner, "listens_event", f"{location}[{index}]")

    def actions(self, owner, config, location="actions"):
        tails = [owner] if isinstance(owner, str) else list(owner)
        for index, action in enumerate(
            config if isinstance(config, list) else [config]
        ):
            if not isinstance(action, dict):
                continue
            tails = self._action(tails, action, f"{location}[{index}]")
        return tails

    def _action(self, parents, action, location):  # noqa: PLR0911
        if "delay" in action or "wait_template" in action:
            return [
                self._struct(parents, "delay", "Delay / wait", location, "next")
            ]
        if "wait_for_trigger" in action:
            current = self._struct(
                parents, "delay", "Wait for trigger", location, "next"
            )
            self.triggers(
                current,
                action["wait_for_trigger"],
                location + ".wait_for_trigger",
                "waits_for",
            )
            return [current]
        if "condition" in action and not any(
            key in action for key in ("if", "choose")
        ):
            return self.condition(parents, action, location, "next")
        if "if" in action:
            branch = self._struct(parents, "branch", "If", location, "next")
            conditions = self.condition(branch, action["if"], location + ".if")
            condition_owner = conditions[-1] if conditions else branch
            then_tails = self.actions(
                condition_owner, action.get("then", []), location + ".then"
            )
            else_config = action.get("else", [])
            else_tails = self.actions(condition_owner, else_config, location + ".else")
            return self._unique(then_tails + (else_tails or [condition_owner]))
        if "choose" in action:
            branch = self._struct(parents, "branch", "Choose", location, "next")
            tails = []
            for choice_index, choice in enumerate(
                action["choose"] if isinstance(action["choose"], list) else []
            ):
                option = self._struct(
                    branch,
                    "branch",
                    f"Option {choice_index + 1}",
                    f"{location}.choose[{choice_index}]",
                )
                conditions = self.condition(
                    option,
                    choice.get("conditions", []),
                    f"{location}.choose[{choice_index}].conditions",
                )
                tails.extend(
                    self.actions(
                        conditions[-1] if conditions else option,
                        choice.get("sequence", []),
                        f"{location}.choose[{choice_index}].sequence",
                    )
                )
            default_tails = self.actions(
                branch, action.get("default", []), location + ".default"
            )
            return self._unique(tails + default_tails or [branch])
        if "sequence" in action:
            branch = self._struct(
                parents, "branch", "Sequence", location + ".sequence", "next"
            )
            return self.actions(branch, action["sequence"], location + ".sequence")
        if "parallel" in action:
            branch = self._struct(
                parents, "branch", "Parallel", location + ".parallel", "next"
            )
            tails = []
            sequences = (
                action["parallel"] if isinstance(action["parallel"], list) else []
            )
            for sequence_index, sequence in enumerate(sequences):
                tails.extend(
                    self.actions(
                        branch, sequence, f"{location}.parallel[{sequence_index}]"
                    )
                )
            return self._unique(tails or [branch])
        if "repeat" in action:
            branch = self._struct(parents, "branch", "Repeat", location, "next")
            repeat = action["repeat"] if isinstance(action["repeat"], dict) else {}
            conditions = self.condition(
                branch,
                repeat.get("while", repeat.get("until", [])),
                location + ".repeat",
            )
            sequence_tails = self.actions(
                conditions[-1] if conditions else branch,
                repeat.get("sequence", []),
                location + ".repeat.sequence",
            )
            return self._unique([branch, *sequence_tails])
        service = action.get("action", action.get("service"))
        label = service if isinstance(service, str) else "Action"
        current = self._struct(parents, "action", label, location, "next")
        if not isinstance(service, str):
            return [current]
        self._service_action(current, service, action, location)
        return [current]

    def _service_action(self, current, service, action, location):
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
            location,
            metadata={
                "service": service,
                "data": _safe_data(action.get("data", action.get("service_data", {}))),
                "flow_owner": self._flow_owner,
            },
        )
        self.target(
            service_id,
            action.get("target", action.get("data", {})),
            "targets",
            location,
            {"flow_owner": self._flow_owner},
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
            self.edge(current, target_id, relation, location)
        target_config = action.get("target", action.get("data", {}))
        if isinstance(target_config, dict):
            target_refs, _ = self._entity_values(
                target_config.get("entity_id", target_config.get("entity_ids"))
            )
            for target_ref in target_refs:
                target_domain, _, target_object = target_ref.partition(".")
                if target_domain in {"script", "automation", "scene"}:
                    target_id = f"{target_domain}:{target_object}"
                    self.graph.add_node(Node(target_id, target_domain, target_object))
                    relation = {
                        "script": "calls_script",
                        "automation": "calls_automation",
                        "scene": "activates_scene",
                    }[target_domain]
                    self.edge(current, target_id, relation, location)
        if service == "event.fire":
            event = action.get("data", {}).get("event_type")
            if isinstance(event, str):
                eid = f"event:{event}"
                self.graph.add_node(Node(eid, "event", event))
                self.edge(current, eid, "fires_event", location)

    @staticmethod
    def _unique(items):
        return list(dict.fromkeys(items))

    def parse_flow(self, node_id, config):
        self._flow_owner = node_id
        self.triggers(
            node_id, config.get("triggers", config.get("trigger", [])), "triggers"
        )
        conditions = self.condition(
            node_id, config.get("conditions", config.get("condition", [])), "conditions"
        )
        self.actions(
            conditions[-1] if conditions else node_id,
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
