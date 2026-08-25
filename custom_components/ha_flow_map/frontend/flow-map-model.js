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
