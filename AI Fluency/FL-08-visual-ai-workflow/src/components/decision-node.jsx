"use client";

import { Handle, Position } from "@xyflow/react";

export function DecisionNode({ data, selected }) {
  return (
    <div className={`decision-node ${selected ? "decision-node--selected" : ""}`}>
      <Handle type="target" position={Position.Left} className="decision-node__target" />
      <div className="decision-node__eyebrow">AI decision</div>
      <strong>{data.title}</strong>
      <p>{data.prompt || "Add a YES/NO prompt"}</p>
      <div className="decision-node__handles">
        <span><Handle id="yes" type="source" position={Position.Right} style={{ top: "72%" }} />YES</span>
        <span><Handle id="no" type="source" position={Position.Right} style={{ top: "88%" }} />NO</span>
      </div>
    </div>
  );
}
