import { NextResponse } from "next/server";

import { inngest } from "@/inngest/client";
import { createRun } from "@/lib/run-store";
import { validateWorkflow } from "@/lib/workflow";

export async function POST(request) {
  const { nodes, edges, startNodeId } = await request.json();
  const validationError = validateWorkflow(nodes, edges);
  if (validationError) return NextResponse.json({ error: validationError }, { status: 400 });

  const runId = crypto.randomUUID();
  await createRun(runId);
  await inngest.send({ name: "workflow/execute", data: { runId, nodes, edges, startNodeId } });
  return NextResponse.json({ runId }, { status: 202 });
}
