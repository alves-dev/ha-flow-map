import assert from "node:assert/strict";
import { displayGraph, flowLayout, gridLayout } from "../custom_components/ha_flow_map/frontend/flow-map-model.js";

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
const flow = flowLayout(compact.nodes, compact.edges);
assert.ok(flow.get("entity:light.desk").y > flow.get("automation:office").y);
const cyclic = flowLayout(
  [{ id: "automation:office" }, { id: "condition:enabled" }],
  [
    { source: "automation:office", target: "condition:enabled", type: "contains" },
    { source: "condition:enabled", target: "automation:office", type: "reads_state" },
  ],
);
assert.ok(cyclic.get("condition:enabled").y > cyclic.get("automation:office").y);
const feedback = flowLayout(
  [{ id: "automation:office" }, { id: "branch:if" }, { id: "entity:motion" }],
  [
    { source: "automation:office", target: "branch:if", type: "contains" },
    { source: "branch:if", target: "entity:motion", type: "targets" },
    { source: "entity:motion", target: "automation:office", type: "triggers" },
  ],
);
assert.ok(Math.max(...[...feedback.values()].map(({ y }) => y)) < 500);
const deviceTrigger = flowLayout(
  [{ id: "automation:office" }, { id: "device:motion" }],
  [{ source: "device:motion", target: "automation:office", type: "triggers" }],
  "automation:office",
);
assert.ok(deviceTrigger.get("device:motion").y < deviceTrigger.get("automation:office").y);
console.log("frontend model tests: ok");
