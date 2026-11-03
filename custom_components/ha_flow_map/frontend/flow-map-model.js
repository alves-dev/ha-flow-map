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

const localeData = {
  en: {
    actionVerb: {
      activate: "Activate",
      close_cover: "Close",
      lock: "Lock",
      open_cover: "Open",
      play_media: "Play",
      start: "Start",
      stop: "Stop",
      toggle: "Toggle",
      turn_off: "Turn off",
      turn_on: "Turn on",
      unlock: "Unlock",
    },
    domainNoun: {
      climate: "climate",
      cover: "cover",
      light: "light",
      lock: "lock",
      media_player: "media player",
      scene: "scene",
      script: "script",
      switch: "switch",
    },
  },
  "pt-BR": {
    actionVerb: {
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
    },
    domainNoun: {
      climate: "clima",
      cover: "cobertura",
      light: "luz",
      lock: "fechadura",
      media_player: "mídia",
      scene: "cena",
      script: "script",
      switch: "interruptor",
    },
  },
};

export function uiLanguage(locale) {
  return String(locale?.language || "en").toLowerCase().startsWith("pt")
    ? "pt-BR"
    : "en";
}

function localized(locale) {
  return localeData[uiLanguage(locale)] || localeData.en;
}

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

export function describeAction(node, byId, locale) {
  const strings = localized(locale);
  const service = node.metadata?.service || node.label;
  const [domain, action] = String(service).split(".");
  if (domain === "notify") return uiLanguage(locale) === "pt-BR" ? "Enviar notificação" : "Send notification";
  const verb = strings.actionVerb[action];
  if (!verb) return service;
  const targets = actionTargets(node);
  const noun = strings.domainNoun[domain];
  const data = node.metadata?.data || {};
  if (domain === "light" && action === "turn_on" && targets.length === 1) {
    const brightness = data.brightness_pct;
    if (typeof brightness === "number") {
      return uiLanguage(locale) === "pt-BR"
        ? `Ajustar ${targetLabel(targets[0], byId)} para ${brightness}%`
        : `Set ${targetLabel(targets[0], byId)} to ${brightness}%`;
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

export function describeCondition(node, edges, byId, locale) {
  const portuguese = uiLanguage(locale) === "pt-BR";
  const type = node.metadata?.condition || node.label;
  const entity = conditionEntity(node, edges, byId);
  const label = entity?.label;
  const state = node.metadata?.state;
  if (type === "and") return portuguese ? "Todas as condições são verdadeiras?" : "Are all conditions true?";
  if (type === "or") return portuguese ? "Alguma condição é verdadeira?" : "Is any condition true?";
  if (type === "not") return portuguese ? "A condição abaixo é falsa?" : "Is the condition below false?";
  if (type === "template") return portuguese ? "Avaliar condição personalizada" : "Evaluate custom condition";
  if (type === "numeric_state" && label) {
    if (node.metadata?.above != null && node.metadata?.below != null) {
      return portuguese
        ? `${label} está entre ${node.metadata.above} e ${node.metadata.below}?`
        : `${label} is between ${node.metadata.above} and ${node.metadata.below}?`;
    }
    if (node.metadata?.above != null) return portuguese ? `${label} está acima de ${node.metadata.above}?` : `${label} is above ${node.metadata.above}?`;
    if (node.metadata?.below != null) return portuguese ? `${label} está abaixo de ${node.metadata.below}?` : `${label} is below ${node.metadata.below}?`;
  }
  if (type === "state" && label && state !== "<template>") {
    if (state === "home") return portuguese ? `${label} está em casa?` : `${label} is home?`;
    if (state === "not_home") return portuguese ? `${label} está fora de casa?` : `${label} is away?`;
    if (state === "on") {
      return entity.metadata?.domain === "binary_sensor"
        ? portuguese ? `${label} está ativo?` : `${label} is active?`
        : entity.metadata?.domain === "light"
          ? portuguese ? `${label} está ligada?` : `${label} is on?`
          : portuguese ? `${label} está ligado?` : `${label} is on?`;
    }
    if (state === "off") {
      return entity.metadata?.domain === "binary_sensor"
        ? portuguese ? `${label} está inativo?` : `${label} is inactive?`
        : entity.metadata?.domain === "light"
          ? portuguese ? `${label} está desligada?` : `${label} is off?`
          : portuguese ? `${label} está desligado?` : `${label} is off?`;
    }
    if (state != null) return portuguese ? `${label} está em ${state}?` : `${label} is ${state}?`;
  }
  return label
    ? portuguese ? `Verificar ${label}` : `Check ${label}`
    : portuguese ? `Condição: ${type}` : `Condition: ${type}`;
}

export function describeTrigger(node, edges, locale) {
  const portuguese = uiLanguage(locale) === "pt-BR";
  const edge = edges.find(
    (item) => item.source === node.id && ["triggers", "listens_event"].includes(item.type),
  );
  const trigger = edge?.metadata?.trigger;
  const state = edge?.metadata?.to;
  if (node.type === "event") return portuguese ? `Evento ${node.label} recebido` : `Event ${node.label} received`;
  if (trigger === "state" && state !== "<template>") {
    if (state === "on") return portuguese ? `${node.label} foi ativado` : `${node.label} turned on`;
    if (state === "off") return portuguese ? `${node.label} foi desativado` : `${node.label} turned off`;
    if (state != null) return portuguese ? `${node.label} mudou para ${state}` : `${node.label} changed to ${state}`;
  }
  if (trigger === "numeric_state" && edge?.metadata?.above != null) {
    return portuguese ? `${node.label} passou de ${edge.metadata.above}` : `${node.label} went above ${edge.metadata.above}`;
  }
  return node.label;
}

/** Present an explicit graph relation without inferring execution history. */
export function edgePresentation(edge, locale) {
  const portuguese = uiLanguage(locale) === "pt-BR";
  const location = edge.location || "";
  if (location.includes(".else")) return { className: "no", label: portuguese ? "Não" : "No" };
  if (location.includes(".then")) return { className: "yes", label: portuguese ? "Sim" : "Yes" };
  if (location.includes(".parallel")) {
    return { className: "parallel", label: portuguese ? "Em paralelo" : "In parallel" };
  }
  if (["calls_script", "calls_automation", "activates_scene"].includes(edge.type)) {
    return { className: "calls-flow", label: portuguese ? "Chama fluxo" : "Calls flow" };
  }
  if (edge.type === "next") return { className: "sequence", label: "" };
  return { className: "", label: "" };
}

/** Current Home Assistant state, not an assertion about past flow execution. */
export function automationStatus(node, locale) {
  const portuguese = uiLanguage(locale) === "pt-BR";
  const state = node.metadata?.state;
  if (state === "on") return { className: "active", label: portuguese ? "Ativa" : "Active" };
  if (state === "off") return { className: "disabled", label: portuguese ? "Desativada" : "Disabled" };
  if (state === "unavailable" || node.metadata?.available === false) {
    return { className: "unavailable", label: portuguese ? "Indisponível" : "Unavailable" };
  }
  return { className: "unknown", label: portuguese ? "Estado desconhecido" : "Unknown state" };
}
