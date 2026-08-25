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
export function flowLayout(nodes, edges) {
  const rank = new Map(nodes.map((node) => [node.id, 0]));
  for (let pass = 0; pass < nodes.length; pass += 1) {
    let changed = false;
    for (const edge of edges) {
      if (!rank.has(edge.source) || !rank.has(edge.target)) continue;
      const next = Math.min(nodes.length - 1, rank.get(edge.source) + 1);
      if (next > rank.get(edge.target)) { rank.set(edge.target, next); changed = true; }
    }
    if (!changed) break;
  }
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
