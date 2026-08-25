import assert from "node:assert/strict";
import { displayGraph, gridLayout } from "../custom_components/ha_flow_map/frontend/flow-map-model.js";

const graph = {
  nodes: [{ id: "automation:office", type: "automation" }, { id: "service:light.turn_on", type: "service" }, { id: "entity:light.desk", type: "entity" }],
  edges: [
    { id: "a", source: "automation:office", target: "service:light.turn_on", type: "calls_service", confidence: "confirmed" },
    { id: "b", source: "service:light.turn_on", target: "entity:light.desk", type: "targets", confidence: "confirmed" },
  ],
};
assert.equal(displayGraph(graph, true).nodes.length, 3);
const compact = displayGraph(graph, false);
assert.equal(compact.nodes.length, 2);
assert.deepEqual(compact.edges.map(({ source, target }) => [source, target]), [["automation:office", "entity:light.desk"]]);
const layout = gridLayout(compact.nodes);
assert.equal(layout.get("automation:office").x, 120);
assert.equal(layout.get("entity:light.desk").x, 370);
console.log("frontend model tests: ok");
