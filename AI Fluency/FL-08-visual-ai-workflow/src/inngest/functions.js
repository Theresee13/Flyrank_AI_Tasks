import OpenAI from "openai";

import { inngest } from "@/inngest/client";
import { appendRunStep, failRun, finishRun, markRunRunning } from "@/lib/run-store";
import { findOutgoingEdge } from "@/lib/workflow";

const decisionInstruction = "Return exactly one token: YES or NO. Do not add punctuation or explanation.";

function normalizeDecision(answer) {
  const decision = answer?.trim().toUpperCase();
  if (decision !== "YES" && decision !== "NO") {
    throw new Error("The AI provider did not return YES or NO.");
  }

  return decision;
}

async function decideWithGemini(prompt, apiKey) {
  const model = process.env.GEMINI_MODEL || "gemini-3.6-flash";
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": apiKey,
      },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: decisionInstruction }] },
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0, maxOutputTokens: 64 },
      }),
    },
  );

  if (!response.ok) {
    const details = await response.text();
    throw new Error(`Gemini request failed (${response.status}): ${details}`);
  }

  const payload = await response.json();
  return normalizeDecision(payload.candidates?.[0]?.content?.parts?.[0]?.text);
}

async function decideWithOpenAI(prompt, apiKey) {
  const client = new OpenAI({ apiKey });
  const completion = await client.chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-4o-mini",
    temperature: 0,
    messages: [
      { role: "system", content: decisionInstruction },
      { role: "user", content: prompt },
    ],
  });
  return normalizeDecision(completion.choices[0]?.message?.content);
}

async function decide(prompt) {
  if (process.env.GEMINI_API_KEY) {
    return decideWithGemini(prompt, process.env.GEMINI_API_KEY);
  }

  if (process.env.OPENAI_API_KEY) {
    return decideWithOpenAI(prompt, process.env.OPENAI_API_KEY);
  }

  throw new Error("Configure GEMINI_API_KEY or OPENAI_API_KEY before executing a workflow.");
}

export const executeWorkflow = inngest.createFunction(
  { id: "execute-yes-no-workflow", retries: 2 },
  { event: "workflow/execute" },
  async ({ event, step }) => {
    const { runId, nodes, edges, startNodeId } = event.data;
    await markRunRunning(runId);
    const nodesById = new Map(nodes.map((node) => [node.id, node]));
    let currentNodeId = startNodeId || nodes[0]?.id;
    const visited = new Set();

    try {
      while (currentNodeId && !visited.has(currentNodeId)) {
        const node = nodesById.get(currentNodeId);
        if (!node) throw new Error(`Node ${currentNodeId} does not exist.`);
        visited.add(currentNodeId);
        const outcome = await step.run(`decide-${currentNodeId}`, () => decide(node.data.prompt));
        const nextEdge = findOutgoingEdge(edges, currentNodeId, outcome);
        await step.run(`record-${currentNodeId}`, () => appendRunStep(runId, {
          nodeId: currentNodeId,
          title: node.data.title,
          prompt: node.data.prompt,
          outcome,
          edgeId: nextEdge?.id || null,
        }));
        currentNodeId = nextEdge?.target;
      }
      if (currentNodeId) throw new Error("The workflow contains a cycle.");
      await finishRun(runId);
    } catch (error) {
      await failRun(runId, error instanceof Error ? error.message : "Workflow execution failed.");
      throw error;
    }
  },
);
