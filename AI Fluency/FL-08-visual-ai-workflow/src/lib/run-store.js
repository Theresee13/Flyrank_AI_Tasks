import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";

const dataDirectory = path.join(process.cwd(), ".data");
const runStorePath = path.join(dataDirectory, "workflow-runs.json");

async function readRuns() {
  try {
    return JSON.parse(await readFile(runStorePath, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") return {};
    throw error;
  }
}

async function writeRuns(runs) {
  await mkdir(dataDirectory, { recursive: true });
  const temporaryPath = `${runStorePath}.tmp`;
  await writeFile(temporaryPath, JSON.stringify(runs, null, 2), "utf8");
  await rename(temporaryPath, runStorePath);
}

async function updateRun(runId, update) {
  const runs = await readRuns();
  const run = runs[runId];
  if (!run) return undefined;
  const nextRun = update(run);
  runs[runId] = nextRun;
  await writeRuns(runs);
  return nextRun;
}

export async function createRun(runId) {
  const runs = await readRuns();
  const run = { id: runId, status: "queued", steps: [], createdAt: new Date().toISOString() };
  runs[runId] = run;
  await writeRuns(runs);
  return run;
}

export async function getRun(runId) {
  const runs = await readRuns();
  return runs[runId];
}

export function markRunRunning(runId) {
  return updateRun(runId, (run) => ({ ...run, status: "running" }));
}

export function appendRunStep(runId, step) {
  return updateRun(runId, (run) => ({
    ...run,
    steps: [...run.steps, { ...step, completedAt: new Date().toISOString() }],
  }));
}

export function finishRun(runId) {
  return updateRun(runId, (run) => ({ ...run, status: "completed" }));
}

export function failRun(runId, message) {
  return updateRun(runId, (run) => ({ ...run, status: "failed", error: message }));
}
