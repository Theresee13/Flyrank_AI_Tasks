"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Download, FileUp, Play, Plus, Save, Trash2 } from "lucide-react";

import { DecisionNode } from "@/components/decision-node";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { initialEdges, initialNodes, validateWorkflow } from "@/lib/workflow";

const nodeTypes = { decision: DecisionNode };
const storageKey = "flyrank-decision-flow";

export default function WorkflowPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNodeId, setSelectedNodeId] = useState("triage");
  const [run, setRun] = useState(null);
  const [message, setMessage] = useState("");
  const selectedNode = nodes.find((node) => node.id === selectedNodeId);
  const activeNodeIds = new Set(run?.steps.map((step) => step.nodeId));
  const activeEdgeIds = new Set(run?.steps.map((step) => step.edgeId).filter(Boolean));

  const decoratedNodes = useMemo(() => nodes.map((node) => ({
    ...node,
    className: activeNodeIds.has(node.id) ? "is-executed" : "",
  })), [nodes, run]);
  const decoratedEdges = useMemo(() => edges.map((edge) => ({
    ...edge,
    animated: activeEdgeIds.has(edge.id),
    className: activeEdgeIds.has(edge.id) ? "is-executed" : "",
  })), [edges, run]);

  useEffect(() => {
    if (!run?.id || ["completed", "failed"].includes(run.status)) return undefined;
    const timer = window.setInterval(async () => {
      const response = await fetch(`/api/workflows/runs/${run.id}`);
      if (response.ok) setRun(await response.json());
    }, 800);
    return () => window.clearInterval(timer);
  }, [run?.id, run?.status]);

  const onConnect = useCallback((connection) => {
    if (!connection.sourceHandle) return;
    const outcome = connection.sourceHandle.toUpperCase();
    setEdges((current) => addEdge({
      ...connection,
      id: `${connection.source}-${outcome}-${connection.target}-${crypto.randomUUID()}`,
      label: outcome,
      data: { outcome },
      type: "smoothstep",
    }, current));
  }, [setEdges]);

  function addNode() {
    const id = `decision-${crypto.randomUUID().slice(0, 8)}`;
    setNodes((current) => [...current, {
      id,
      type: "decision",
      position: { x: 240 + current.length * 55, y: 160 + current.length * 35 },
      data: { title: "New decision", prompt: "Is this condition true?" },
    }]);
    setSelectedNodeId(id);
  }

  function updateSelectedNode(field, value) {
    setNodes((current) => current.map((node) => node.id === selectedNodeId
      ? { ...node, data: { ...node.data, [field]: value } }
      : node));
  }

  function removeSelectedNode() {
    if (!selectedNodeId) return;
    setNodes((current) => current.filter((node) => node.id !== selectedNodeId));
    setEdges((current) => current.filter((edge) => edge.source !== selectedNodeId && edge.target !== selectedNodeId));
    setSelectedNodeId(null);
  }

  function saveWorkflow() {
    localStorage.setItem(storageKey, JSON.stringify({ nodes, edges }));
    setMessage("Workflow saved in this browser.");
  }

  function loadWorkflow() {
    const saved = localStorage.getItem(storageKey);
    if (!saved) return setMessage("No saved workflow found.");
    const workflow = JSON.parse(saved);
    setNodes(workflow.nodes || initialNodes);
    setEdges(workflow.edges || initialEdges);
    setMessage("Saved workflow loaded.");
  }

  function exportWorkflow() {
    const file = new Blob([JSON.stringify({ nodes, edges }, null, 2)], { type: "application/json" });
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(file);
    anchor.download = "decision-flow.json";
    anchor.click();
    URL.revokeObjectURL(anchor.href);
  }

  async function importWorkflow(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const workflow = JSON.parse(await file.text());
      const validationError = validateWorkflow(workflow.nodes, workflow.edges);
      if (validationError) throw new Error(validationError);
      setNodes(workflow.nodes);
      setEdges(workflow.edges);
      setMessage("Workflow imported.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not import this file.");
    }
    event.target.value = "";
  }

  async function execute() {
    const validationError = validateWorkflow(nodes, edges);
    if (validationError) return setMessage(validationError);
    setMessage("");
    const response = await fetch("/api/workflows/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes, edges, startNodeId: nodes[0]?.id }),
    });
    const payload = await response.json();
    if (!response.ok) return setMessage(payload.error || "Could not start workflow.");
    setRun({ id: payload.runId, status: "queued", steps: [] });
  }

  return (
    <main className="studio">
      <header className="studio__header">
        <div><p>FlyRank AI Fluency</p><h1>Decision Flow Studio</h1></div>
        <div className="toolbar">
          <Button variant="outline" onClick={saveWorkflow}><Save size={15} />Save</Button>
          <Button variant="outline" onClick={loadWorkflow}>Load</Button>
          <Button variant="outline" onClick={exportWorkflow}><Download size={15} />Export</Button>
          <label className="import-button"><FileUp size={15} />Import<input type="file" accept="application/json" onChange={importWorkflow} /></label>
          <Button onClick={execute} disabled={run && !["completed", "failed"].includes(run.status)}><Play size={15} />Run flow</Button>
        </div>
      </header>
      {message && <div className="studio__notice">{message}</div>}
      <section className="studio__body">
        <aside className="panel panel--editor">
          <div className="panel__title"><span>Node editor</span><Button variant="ghost" onClick={addNode} title="Add decision node"><Plus size={18} /></Button></div>
          {selectedNode ? <>
            <label>Title<input value={selectedNode.data.title} onChange={(event) => updateSelectedNode("title", event.target.value)} /></label>
            <label>Decision prompt<Textarea value={selectedNode.data.prompt} onChange={(event) => updateSelectedNode("prompt", event.target.value)} /></label>
            <p className="hint">Connect the YES or NO handle on the canvas to choose the next decision.</p>
            <Button variant="danger" onClick={removeSelectedNode}><Trash2 size={15} />Remove node</Button>
          </> : <p className="hint">Select a decision node to edit it.</p>}
        </aside>
        <div className="canvas">
          <ReactFlow nodes={decoratedNodes} edges={decoratedEdges} nodeTypes={nodeTypes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeClick={(_event, node) => setSelectedNodeId(node.id)} fitView>
            <Background gap={20} size={1} />
            <MiniMap zoomable pannable />
            <Controls />
          </ReactFlow>
        </div>
        <aside className="panel panel--logs">
          <div className="panel__title"><span>Execution log</span>{run && <b className={`status status--${run.status}`}>{run.status}</b>}</div>
          {!run && <p className="hint">Run the flow to see each AI decision and the selected path.</p>}
          {run?.steps.map((step, index) => <article className="log-entry" key={`${step.nodeId}-${index}`}><span>{index + 1}</span><div><strong>{step.title}</strong><p>{step.outcome} selected</p></div></article>)}
          {run?.error && <p className="error">{run.error}</p>}
        </aside>
      </section>
    </main>
  );
}
