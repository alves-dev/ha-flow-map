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

const actionVerb = {
  activate: "Ativar",
  close_cover: "Fechar",
  lock: "Trancar",
  open_cover: "Abrir",
  play_media: "Reproduzir",
  start: "Iniciar",
  stop: "Parar",
  toggle: "Alternar",
  turn_off: "Desligar",
  turn_on: "Ligar",
  unlock: "Destrancar",
};

const domainNoun = {
  climate: "clima",
  cover: "cobertura",
  light: "luz",
  lock: "fechadura",
  media_player: "mídia",
  scene: "cena",
  script: "script",
  switch: "interruptor",
};

function entityIds(value) {
  if (typeof value === "string") return value === "<template>" ? [] : [value];
  if (Array.isArray(value)) return value.flatMap(entityIds);
  return [];
}

function actionTargets(node) {
  const target = node.metadata?.target || {};
  return entityIds(target.entity_id ?? target.entity_ids);
}

function targetLabel(entityId, byId) {
  return byId?.get(`entity:${entityId}`)?.label || entityId;
}

export function describeAction(node, byId) {
  const service = node.metadata?.service || node.label;
  const [domain, action] = String(service).split(".");
  if (domain === "notify") return "Enviar notificação";
  const verb = actionVerb[action];
  if (!verb) return service;
  const targets = actionTargets(node);
  const noun = domainNoun[domain];
  const data = node.metadata?.data || {};
  if (domain === "light" && action === "turn_on" && targets.length === 1) {
    const brightness = data.brightness_pct;
    if (typeof brightness === "number") {
      return `Ajustar ${targetLabel(targets[0], byId)} para ${brightness}%`;
    }
  }
  if (targets.length === 1) return `${verb} ${targetLabel(targets[0], byId)}`;
  if (targets.length > 1 && noun) return `${verb} ${targets.length} ${noun}s`;
  return noun ? `${verb} ${noun}` : verb;
}

function conditionEntity(node, edges, byId) {
  const edge = edges.find(
    (item) => item.target === node.id && item.type === "used_in_condition",
  );
  return edge && byId?.get(edge.source);
}

export function describeCondition(node, edges, byId) {
  const type = node.metadata?.condition || node.label;
  const entity = conditionEntity(node, edges, byId);
  const label = entity?.label;
  const state = node.metadata?.state;
  if (type === "and") return "Todas as condições são verdadeiras?";
  if (type === "or") return "Alguma condição é verdadeira?";
  if (type === "not") return "A condição abaixo é falsa?";
  if (type === "template") return "Avaliar condição personalizada";
  if (type === "numeric_state" && label) {
    if (node.metadata?.above != null && node.metadata?.below != null) {
      return `${label} está entre ${node.metadata.above} e ${node.metadata.below}?`;
    }
    if (node.metadata?.above != null) return `${label} está acima de ${node.metadata.above}?`;
    if (node.metadata?.below != null) return `${label} está abaixo de ${node.metadata.below}?`;
  }
  if (type === "state" && label && state !== "<template>") {
    if (state === "home") return `${label} está em casa?`;
    if (state === "not_home") return `${label} está fora de casa?`;
    if (state === "on") {
      return entity.metadata?.domain === "binary_sensor"
        ? `${label} está ativo?`
        : entity.metadata?.domain === "light"
          ? `${label} está ligada?`
          : `${label} está ligado?`;
    }
    if (state === "off") {
      return entity.metadata?.domain === "binary_sensor"
        ? `${label} está inativo?`
        : entity.metadata?.domain === "light"
          ? `${label} está desligada?`
          : `${label} está desligado?`;
    }
    if (state != null) return `${label} está em ${state}?`;
  }
  return label ? `Verificar ${label}` : `Condição: ${type}`;
}

export function describeTrigger(node, edges) {
  const edge = edges.find(
    (item) => item.source === node.id && ["triggers", "listens_event"].includes(item.type),
  );
  const trigger = edge?.metadata?.trigger;
  const state = edge?.metadata?.to;
  if (node.type === "event") return `Evento ${node.label} recebido`;
  if (trigger === "state" && state !== "<template>") {
    if (state === "on") return `${node.label} foi ativado`;
    if (state === "off") return `${node.label} foi desativado`;
    if (state != null) return `${node.label} mudou para ${state}`;
  }
  if (trigger === "numeric_state" && edge?.metadata?.above != null) {
    return `${node.label} passou de ${edge.metadata.above}`;
  }
  return node.label;
}

/** Present an explicit graph relation without inferring execution history. */
export function edgePresentation(edge) {
  const location = edge.location || "";
  if (location.includes(".else")) return { className: "no", label: "Não" };
  if (location.includes(".then")) return { className: "yes", label: "Sim" };
  if (location.includes(".parallel")) {
    return { className: "parallel", label: "Em paralelo" };
  }
  if (["calls_script", "calls_automation", "activates_scene"].includes(edge.type)) {
    return { className: "calls-flow", label: "Chama fluxo" };
  }
  if (edge.type === "next") return { className: "sequence", label: "" };
  return { className: "", label: "" };
}

/** Current Home Assistant state, not an assertion about past flow execution. */
export function automationStatus(node) {
  const state = node.metadata?.state;
  if (state === "on") return { className: "active", label: "Ativa" };
  if (state === "off") return { className: "disabled", label: "Desativada" };
  if (state === "unavailable" || node.metadata?.available === false) {
    return { className: "unavailable", label: "Indisponível" };
  }
  return { className: "unknown", label: "Estado desconhecido" };
}
