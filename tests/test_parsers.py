import unittest

from custom_components.ha_flow_map.graph.builder import build_graph
from custom_components.ha_flow_map.graph.index import GraphIndex
from custom_components.ha_flow_map.graph.model import Node
from custom_components.ha_flow_map.parsers.automation import _safe_data


def graph():
    return build_graph(
        {
            "automation.office": {
                "alias": "Office",
                "triggers": [
                    {
                        "trigger": "state",
                        "entity_id": ["binary_sensor.motion", "sensor.lux"],
                    }
                ],
                "conditions": [
                    {
                        "condition": "and",
                        "conditions": [
                            {"condition": "state", "entity_id": "input_boolean.enabled"}
                        ],
                    }
                ],
                "actions": [
                    {
                        "if": [
                            {"condition": "state", "entity_id": "input_boolean.enabled"}
                        ],
                        "then": [
                            {
                                "parallel": [
                                    [{"action": "script.good_night"}],
                                    [
                                        {
                                            "wait_for_trigger": [
                                                {
                                                    "trigger": "state",
                                                    "entity_id": "binary_sensor.door",
                                                }
                                            ]
                                        }
                                    ],
                                ]
                            }
                        ],
                        "else": [{"delay": "00:00:01"}],
                    },
                    {
                        "choose": [
                            {
                                "conditions": [
                                    {"condition": "state", "entity_id": "sun.sun"}
                                ],
                                "sequence": [{"action": "script.good_night"}],
                            }
                        ],
                        "default": [
                            {
                                "action": "scene.turn_on",
                                "target": {"entity_id": "scene.evening"},
                            }
                        ],
                    },
                    {
                        "action": "light.turn_on",
                        "target": {
                            "entity_id": "{{ states('input_text.light') }}",
                            "device_id": "device-1",
                            "area_id": "area-1",
                        },
                    },
                ],
            }
        },
        {
            "script.good_night": {
                "sequence": [
                    {
                        "repeat": {
                            "count": 2,
                            "sequence": [
                                {
                                    "action": "light.turn_off",
                                    "target": {"entity_id": "light.bedroom"},
                                }
                            ],
                        }
                    }
                ]
            }
        },
        {"scene.evening": {"entities": {"light.desk": "on"}}},
    )


class ParserTests(unittest.TestCase):
    def test_recursive_flow_and_relations(self):
        result = graph()
        self.assertIn("entity:binary_sensor.motion", result.nodes)
        self.assertTrue(any(edge.type == "triggers" for edge in result.edges.values()))
        self.assertTrue(
            any(edge.type == "calls_script" for edge in result.edges.values())
        )
        self.assertTrue(
            any(
                edge.type == "activates_scene" and edge.target == "scene:evening"
                for edge in result.edges.values()
            )
        )
        self.assertTrue(any(node.type == "branch" for node in result.nodes.values()))
        self.assertTrue(any(edge.type == "waits_for" for edge in result.edges.values()))
        self.assertIn("device:device-1", result.nodes)
        self.assertIn("area:area-1", result.nodes)
        self.assertTrue(
            any(edge.confidence == "dynamic" for edge in result.edges.values())
        )

    def test_if_actions_follow_the_condition_node(self):
        result = graph()
        condition = next(
            node
            for node in result.nodes.values()
            if node.metadata.get("location") == "actions[0].if[0]"
        )
        paths = {
            edge.location
            for edge in result.edges.values()
            if edge.source == condition.id
        }
        self.assertIn("actions[0].then[0].parallel", paths)
        self.assertIn("actions[0].else[0]", paths)

    def test_device_and_area_triggers_are_preserved_as_triggers(self):
        result = build_graph(
            {
                "automation.device_trigger": {
                    "triggers": [
                        {
                            "trigger": "motion.detected",
                            "target": {"device_id": "motion-device"},
                        },
                        {
                            "trigger": "event",
                            "target": {"area_id": "office"},
                        },
                    ]
                }
            },
            {},
            {},
        )

        trigger_edges = {
            (edge.source, edge.target, edge.type) for edge in result.edges.values()
        }
        self.assertIn(
            ("device:motion-device", "automation:device_trigger", "triggers"),
            trigger_edges,
        )
        self.assertIn(
            ("area:office", "automation:device_trigger", "triggers"),
            trigger_edges,
        )

    def test_reverse_index_and_bounded_expansion(self):
        index = GraphIndex(graph())
        node_id = "entity:binary_sensor.motion"
        data = index.neighborhood(node_id, "outbound", 2, 100, 100)
        self.assertIn(node_id, {node["id"] for node in data["nodes"]})
        self.assertTrue(
            any(edge["target"] == "automation:office" for edge in data["edges"])
        )
        self.assertEqual(index.search("office")[0]["type"], "automation")

    def test_focused_flow_keeps_only_selected_owner_service_targets(self):
        result = build_graph(
            {
                "automation.focused": {
                    "actions": [
                        {
                            "action": "light.turn_on",
                            "target": {"entity_id": "light.desk"},
                        },
                        {
                            "action": "script.turn_on",
                            "target": {"entity_id": "script.called"},
                        },
                    ]
                },
                "automation.other": {
                    "actions": [
                        {
                            "action": "light.turn_on",
                            "target": {"entity_id": "light.unrelated"},
                        }
                    ]
                },
            },
            {
                "script.called": {
                    "sequence": [
                        {
                            "action": "light.turn_off",
                            "target": {"entity_id": "light.inside_called_script"},
                        }
                    ]
                }
            },
            {},
        )

        data = GraphIndex(result).focused_flow("automation:focused")
        node_ids = {node["id"] for node in data["nodes"]}

        self.assertEqual(data["mode"], "focused_flow")
        self.assertIn("entity:light.desk", node_ids)
        self.assertIn("script:called", node_ids)
        self.assertNotIn("entity:light.unrelated", node_ids)
        self.assertNotIn("entity:light.inside_called_script", node_ids)
        self.assertTrue(
            all(
                edge["source"] in node_ids and edge["target"] in node_ids
                for edge in data["edges"]
            )
        )

    def test_focused_flow_keeps_direct_triggers_but_excludes_conditions(self):
        data = GraphIndex(graph()).focused_flow("automation:office")
        node_ids = {node["id"] for node in data["nodes"]}

        self.assertIn("entity:binary_sensor.motion", node_ids)
        self.assertTrue(
            any(
                edge["source"] == "entity:binary_sensor.motion"
                and edge["target"] == "automation:office"
                and edge["type"] == "triggers"
                for edge in data["edges"]
            )
        )
        self.assertNotIn("entity:input_boolean.enabled", node_ids)

    def test_focused_flow_respects_node_limit(self):
        result = build_graph(
            {
                "automation.focused": {
                    "actions": [
                        {
                            "action": "light.turn_on",
                            "target": {"entity_id": "light.desk"},
                        }
                    ]
                }
            },
            {},
            {},
        )

        data = GraphIndex(result).focused_flow("automation:focused", max_nodes=1)

        self.assertEqual([node["id"] for node in data["nodes"]], ["automation:focused"])
        self.assertEqual(data["edges"], [])
        self.assertTrue(data["truncated"])

    def test_action_steps_preserve_sequence_and_reconverge_after_if(self):
        result = build_graph(
            {
                "automation.sequence": {
                    "actions": [
                        {"action": "light.turn_on"},
                        {
                            "if": [
                                {
                                    "condition": "state",
                                    "entity_id": "input_boolean.enabled",
                                }
                            ],
                            "then": [{"action": "switch.turn_on"}],
                            "else": [{"action": "switch.turn_off"}],
                        },
                        {"action": "light.turn_off"},
                    ]
                }
            },
            {},
            {},
        )
        action_nodes = {
            node.metadata["location"]: node.id
            for node in result.nodes.values()
            if node.type == "action"
        }
        next_edges = {
            (edge.source, edge.target)
            for edge in result.edges.values()
            if edge.type == "next"
        }

        first = action_nodes["actions[0]"]
        then = action_nodes["actions[1].then[0]"]
        otherwise = action_nodes["actions[1].else[0]"]
        final = action_nodes["actions[2]"]
        branch = next(
            node.id
            for node in result.nodes.values()
            if node.type == "branch" and node.metadata["location"] == "actions[1]"
        )

        self.assertTrue(
            any(
                edge.source == first and edge.type == "calls_service"
                for edge in result.edges.values()
            )
        )
        self.assertIn((then, final), next_edges)
        self.assertIn((otherwise, final), next_edges)
        self.assertIn((first, branch), next_edges)

    def test_action_steps_reconverge_after_parallel_paths(self):
        result = build_graph(
            {
                "automation.parallel": {
                    "actions": [
                        {
                            "parallel": [
                                [{"action": "light.turn_on"}],
                                [{"action": "switch.turn_on"}],
                            ]
                        },
                        {"action": "notify.send"},
                    ]
                }
            },
            {},
            {},
        )
        action_nodes = {
            node.metadata["location"]: node.id
            for node in result.nodes.values()
            if node.type == "action"
        }
        next_edges = {
            (edge.source, edge.target)
            for edge in result.edges.values()
            if edge.type == "next"
        }
        final = action_nodes["actions[1]"]

        self.assertIn((action_nodes["actions[0].parallel[0][0]"], final), next_edges)
        self.assertIn((action_nodes["actions[0].parallel[1][0]"], final), next_edges)

    def test_search_hides_entity_duplicate_of_configuration_node(self):
        result = graph()
        result.add_node(Node("entity:automation.office", "entity", "Office automation"))
        index = GraphIndex(result)
        matches = index.search("office")
        self.assertEqual([item["id"] for item in matches], ["automation:office"])

    def test_impact_finds_configuration_owners_in_both_directions(self):
        impact = GraphIndex(graph()).impact("entity:binary_sensor.motion")
        self.assertEqual(
            [item["id"] for item in impact["automations"]], ["automation:office"]
        )
        self.assertEqual(
            [item["id"] for item in impact["scripts"]], ["script:good_night"]
        )
        self.assertGreaterEqual(impact["levels"], 4)

    def test_edge_ids_are_stable_and_equivalent_edges_are_deduplicated(self):
        first, second = graph(), graph()
        self.assertEqual(set(first.edges), set(second.edges))
        self.assertEqual(
            len(first.edges), len({edge.id for edge in first.edges.values()})
        )

    def test_service_metadata_redacts_nested_secrets_and_templates(self):
        result = _safe_data(
            {
                "headers": {"authorization": "Bearer secret"},
                "nested": [{"token": "x"}],
                "value": "{{ states('sensor.x') }}",
            }
        )
        self.assertEqual(result["headers"]["authorization"], "<redacted>")
        self.assertEqual(result["nested"][0]["token"], "<redacted>")
        self.assertEqual(result["value"], "<template>")
