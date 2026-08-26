/** Pure graph helpers used by the panel and executable in Node tests. */
export function displayGraph(data, showServices) {
  if (showServices) return { nodes: data.nodes, edges: data.edges };
  const services = new Set(data.nodes.filter((node) => node.type === "service").map((node) => node.id));
  const bySource = new Map();
  for (const edge of data.edges) {
    if (!bySource.has(edge.source)) bySource.set(edge.source, []);
    bySource.get(edge.source).push(edge);
  }
  const edges = data.edges.flatMap((edge) => {
    if (!services.has(edge.target)) return services.has(edge.source) ? [] : [edge];
    return (bySource.get(edge.target) || [])
      .filter((next) => !services.has(next.target))
      .map((next) => ({ ...next, source: edge.source, type: `${edge.type} · ${next.type}` }));
  });
  const unique = new Map(edges.map((edge) => [`${edge.source}|${edge.target}|${edge.type}|${edge.confidence}`, edge]));
  return { nodes: data.nodes.filter((node) => !services.has(node.id)), edges: [...unique.values()] };
}

export function gridLayout(nodes, columns = 4) {
  return new Map(nodes.map((node, index) => [node.id, {
    x: 120 + (index % columns) * 250,
    y: 115 + Math.floor(index / columns) * 150,
    node,
  }]));
}

/** Arrange graph layers in the direction of the relation: source → target. */
export function flowLayout(nodes, edges, rootId) {
  const rank = new Map();
  const referenceEdges = new Set(["reads_state", "used_in_condition"]);
  const children = new Map(nodes.map((node) => [node.id, []]));
  for (const edge of edges) {
    if (referenceEdges.has(edge.type) || !children.has(edge.source) || !children.has(edge.target)) continue;
    children.get(edge.source).push(edge.target);
  }
  const root = nodes.some((node) => node.id === rootId) ? rootId : nodes[0]?.id;
  const queue = [];
  const add = (id, level) => { if (!rank.has(id)) { rank.set(id, level); queue.push(id); } };
  if (root) {
    add(root, 1);
    for (const edge of edges) if (edge.target === root && ["triggers", "listens_event"].includes(edge.type)) add(edge.source, 0);
  }
  const walk = () => {
    while (queue.length) {
      const source = queue.shift();
      for (const target of children.get(source)) {
        const edge = edges.find((item) => item.source === source && item.target === target && !referenceEdges.has(item.type));
        if (edge?.type === "triggers" && rank.get(source) !== 0) continue;
        add(target, rank.get(source) + 1);
      }
    }
  };
  walk();
  for (const node of nodes) { add(node.id, 0); walk(); }
  const layers = new Map();
  for (const node of nodes) {
    const level = rank.get(node.id);
    if (!layers.has(level)) layers.set(level, []);
    layers.get(level).push(node);
  }
  const layout = new Map();
  for (const [level, layer] of layers) {
    layer.forEach((node, index) => layout.set(node.id, {
      x: 500 + (index - (layer.length - 1) / 2) * 250,
      y: 85 + level * 130,
      node,
    }));
  }
  return layout;
}
