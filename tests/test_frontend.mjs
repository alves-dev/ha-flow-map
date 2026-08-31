import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  automationStatus,
  describeAction,
  describeCondition,
  describeTrigger,
  edgePresentation,
  displayGraph,
  flowLayout,
  gridLayout,
} from "../custom_components/ha_flow_map/frontend/flow-map-model.js";

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
const sequence = flowLayout(
  [{ id: "automation:office" }, { id: "action:one" }, { id: "action:two" }],
  [
    { source: "automation:office", target: "action:one", type: "next" },
    { source: "action:one", target: "action:two", type: "next" },
  ],
  "automation:office",
);
assert.ok(sequence.get("action:two").y > sequence.get("action:one").y);
const descriptions = new Map([
  ["entity:light.desk", { id: "entity:light.desk", label: "Luz da mesa", metadata: { domain: "light" } }],
  ["entity:binary_sensor.motion", { id: "entity:binary_sensor.motion", label: "Movimento", metadata: { domain: "binary_sensor" } }],
]);
assert.equal(
  describeAction(
    {
      label: "light.turn_on",
      metadata: {
        service: "light.turn_on",
        target: { entity_id: "light.desk" },
        data: { brightness_pct: 70 },
      },
    },
    descriptions,
  ),
  "Ajustar Luz da mesa para 70%",
);
assert.equal(
  describeCondition(
    {
      id: "condition:desk",
      label: "state",
      metadata: { condition: "state", state: "off" },
    },
    [{ source: "entity:light.desk", target: "condition:desk", type: "used_in_condition" }],
    descriptions,
  ),
  "Luz da mesa está desligada?",
);
assert.equal(
  describeTrigger(
    { id: "entity:binary_sensor.motion", label: "Movimento", type: "entity" },
    [{ source: "entity:binary_sensor.motion", type: "triggers", metadata: { trigger: "state", to: "on" } }],
  ),
  "Movimento foi ativado",
);
assert.deepEqual(
  edgePresentation({ type: "next", location: "actions[0].parallel[1][0]" }),
  { className: "parallel", label: "Em paralelo" },
);
assert.deepEqual(
  edgePresentation({ type: "calls_script" }),
  { className: "calls-flow", label: "Chama fluxo" },
);
assert.deepEqual(
  edgePresentation({ type: "next", location: "actions[0].else[0]" }),
  { className: "no", label: "Não" },
);
assert.deepEqual(
  automationStatus({ metadata: { state: "on", available: true } }),
  { className: "active", label: "Ativa" },
);
assert.deepEqual(
  automationStatus({ metadata: { state: "unavailable", available: false } }),
  { className: "unavailable", label: "Indisponível" },
);
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
const panelSource = await readFile(
  new URL("../custom_components/ha_flow_map/frontend/ha-flow-map.js", import.meta.url),
  "utf8",
);
assert.match(panelSource, /--bg:var\(--card-background-color\)/);
assert.match(panelSource, /--accent:var\(--primary-color\)/);
assert.match(panelSource, /themeColor\(name\)/);
assert.match(panelSource, /ha_flow_map\/flow/);
assert.match(panelSource, /Ver fluxo completo/);
assert.match(panelSource, /action:"AÇÃO"/);
assert.match(panelSource, /flow-map-model\.js\?v=/);
assert.match(panelSource, /nodeTitle\(node,role,edges,byId\)/);
assert.doesNotMatch(panelSource, /#[0-9a-fA-F]{3,8}|(?:rgb|hsl)a?\(/);
console.log("frontend model tests: ok");
