export const initialNodes = [
  {
    id: "triage",
    type: "decision",
    position: { x: 90, y: 170 },
    data: { title: "Triage", prompt: "Is this a support request?" },
  },
  {
    id: "support",
    type: "decision",
    position: { x: 450, y: 70 },
    data: { title: "Support", prompt: "Does the request require an urgent response?" },
  },
  {
    id: "sales",
    type: "decision",
    position: { x: 450, y: 300 },
    data: { title: "Sales", prompt: "Is the request about pricing or a product demo?" },
  },
];

export const initialEdges = [
  { id: "triage-yes-support", source: "triage", sourceHandle: "yes", target: "support", label: "YES", data: { outcome: "YES" } },
  { id: "triage-no-sales", source: "triage", sourceHandle: "no", target: "sales", label: "NO", data: { outcome: "NO" } },
];

export function findOutgoingEdge(edges, nodeId, outcome) {
  return edges.find((edge) => edge.source === nodeId && (edge.data?.outcome || edge.label) === outcome);
}

export function validateWorkflow(nodes, edges) {
  if (!Array.isArray(nodes) || nodes.length === 0) return "Add at least one decision node.";
  if (!nodes.every((node) => node.data?.prompt?.trim())) return "Every decision node needs a prompt.";
  if (!edges.every((edge) => ["YES", "NO"].includes(edge.data?.outcome || edge.label))) {
    return "Connections must use a YES or NO handle.";
  }
  return null;
}
