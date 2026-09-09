# FL-05: Agent Concepts and MCP Basics

## Workflow versus agent

An AI workflow is a fixed sequence of steps. The builder decides the order, the inputs, the output format, and the conditions that move work from one step to the next. A workflow can still contain AI calls, branching, retries, validation, and human review, but its overall shape is known before it runs. This makes a workflow easier to test because each stage has a defined responsibility and an expected result.

An agent is more open-ended. It receives a goal, chooses which available tools to use, decides what to do next, and continues until it has completed the task or needs a person to intervene. The model is involved in selecting actions, not only in producing text inside a predetermined step. That flexibility is useful when the path cannot be known in advance, but it also introduces more risk. An agent needs clear tool permissions, limits on repeated actions, validation of important outputs, and an explicit rule for when to ask a human.

The FL-04 research assistant is primarily a workflow. Its stages gather source material, summarize it, draft a report, review the draft, format the result, and notify the user. The order is deliberately controlled because research reports need provenance and review. The MCP filesystem integration gives the workflow access to tools, and the editor stage has agent-like behavior because it can inspect files and make a bounded revision. That extension does not make every part of the pipeline an autonomous agent. A precise description is more useful: it is a structured workflow with one constrained agentic review stage.

## What MCP adds

The Model Context Protocol is a common way for an AI client to discover and call external capabilities. Instead of placing every integration directly into one model prompt, an MCP server exposes a set of named tools and resources with a defined interface. The client can then provide those capabilities to an assistant while keeping the implementation behind the server boundary.

The three important MCP primitives are tools, resources, and prompts. A tool is an action that can be called, such as listing a directory, reading a file, or writing a reviewed report. A resource is information that can be read by the client, such as a document, a project file, or a generated artifact. A prompt is a reusable instruction template that helps a client or user request a consistent operation. These primitives are related but should not be confused. A resource supplies context, a tool performs an operation, and a prompt describes how an interaction should be carried out.

In this repository, the FL-04 package includes a filesystem MCP client and an MCP-enabled n8n workflow. The client is restricted to the project directory through configuration, which is an important safety boundary. The workflow can inspect the research assistant files, pass selected content into the editor stage, and stage the resulting report. Keeping the file root narrow reduces the chance that an AI action can read or modify unrelated personal files.

## What would make the workflow an agent

The research pipeline would become more agentic if it received a goal such as "prepare this week's engineering brief" and then selected the sources, decided whether more research was needed, chose which review tools to call, and revised the report based on the review results. Those decisions would need to be visible in the run record. A human should approve publication, and the agent should never send an external message or overwrite a source document without confirmation.

The practical design would keep the current deterministic stages as guardrails around the agent. The agent could choose among approved search, file, and formatting tools, but it would have a limited filesystem root, a maximum number of tool calls, a timeout, and a schema for the final report. Source URLs and quoted evidence should remain separate from model-written interpretation. A failed tool call should stop or return for review rather than causing the agent to invent a result. This gives the system useful flexibility without turning every action into an opaque model decision.

## Evidence and limitations

The repository contains the FL-04 workflow definitions, MCP client, prompts, architecture notes, and test utilities. The remaining submission evidence is operational: capture three live MCP tasks, keep the tool calls visible, and avoid exposing credentials or unrelated files. The screenshots should show the task requested, the MCP tool selected, the returned result, and the final outcome. The implementation files demonstrate how the integration is configured, while the screenshots demonstrate that the configured client actually worked in a live run.

The main lesson is that an agent is not defined by adding the word "agent" to a workflow name. It is defined by delegated decision-making, usable tools, bounded permissions, and an observable stopping condition. Starting with a workflow keeps the system understandable. Adding agent behavior only where it removes real uncertainty keeps the result easier to test, review, and maintain.
