import unittest

from custom_components.ha_flow_map.graph.builder import build_graph
from custom_components.ha_flow_map.graph.index import GraphIndex
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

    def test_reverse_index_and_bounded_expansion(self):
        index = GraphIndex(graph())
        node_id = "entity:binary_sensor.motion"
        data = index.neighborhood(node_id, "outbound", 2, 100, 100)
        self.assertIn(node_id, {node["id"] for node in data["nodes"]})
        self.assertTrue(
            any(edge["target"] == "automation:office" for edge in data["edges"])
        )
        self.assertEqual(index.search("office")[0]["type"], "automation")

    def test_impact_finds_configuration_owners_in_both_directions(self):
        impact = GraphIndex(graph()).impact("entity:binary_sensor.motion")
        self.assertEqual([item["id"] for item in impact["automations"]], ["automation:office"])
        self.assertEqual([item["id"] for item in impact["scripts"]], ["script:good_night"])
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
