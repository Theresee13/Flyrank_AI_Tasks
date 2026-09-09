# Assignment Compliance Map

This portfolio contains both internship deliverables and earlier course projects. The names and functionality below identify which folders meet each supplied backend brief, and which items still need a dedicated implementation.

| Brief | Current repository status | Location / notes |
| --- | --- | --- |
| A1: In-memory Task API | Meets core requirements | `Assignment-01-fastapi-backend` now provides the required `/tasks` CRUD contract, health endpoint, and FastAPI docs. |
| A2: SQLite Task API | Meets core requirements | `Assignment-02-sqlite-task-api` preserves A1's task routes using seed-once SQLite persistence and parameterized queries. |
| A3: Postgres + Docker Task API | Meets core requirements | `Assignment-03-with FastAPi-PostgreSQL-Docker/a2-postgres` provides the task routes, parameterized persistence, Docker Compose, env example, and seeded database. |
| A4: Supabase Auth | Meets core requirements | `Assignment-04-jwt-auth-fastapi` delegates signup/login/logout and bearer-token validation to Supabase Auth. The configured project returned a successful Auth settings response. |
| A7: Inngest background job | Live verified | `Assignment-07-inngest-background-jobs` returns `202`, persists status, runs the eight-second task in durable retriable steps, and exposes an every-minute heartbeat cron. The README records successful, failed/retried, and cron verification evidence. |
| A8: PDF report generator | Live verified | `Assignment-08-pdf-report-generator` seeds 200 SQLite orders, renders a real Playwright PDF, prevents duplicate same-day reports, and includes force-request evidence. |
| A9: Polite scraper | Live verified | `Assignment-05-web-scrapper-fastapi/scraper` follows exactly three catalogue pages, produces 60 validated records, proves cache reuse, and isolates an intentional broken URL. |
| A17: LLM behind an API | Live verified with Gemini | `Assignment-07-ruleguard-ai` includes a narrow validated LLM endpoint, retry/timeout handling, a kill switch, live Gemini output, and evaluation cases. |
| BE-09: Visual AI workflow | Live verified with Gemini | `AI Fluency/FL-08-visual-ai-workflow` contains React Flow, Inngest, strict YES/NO branching, execution logs, active path visuals, local save/load/import/export, and screenshots of both branches. |
| FL-04: Automation workflow | Implementation present; live screenshots pending | `AI Fluency/FL-04-Agent-MCP-Build-Phase` includes the n8n workflow, MCP client, prompts, architecture notes, and tests. Capture three live MCP tasks and workflow runs for final evidence. |
| FL-05: Agent concepts and MCP | Explainer added; live MCP screenshots pending | `AI Fluency/FL-05-agent-concepts-and-mcp/README.md` contains the 600 to 900 word explainer. Add screenshots of three live MCP tasks. |
| FL-06: Personal agent design | Present | `AI Fluency/FL-06-ai-arch-copilot` contains the agent design document and implementation foundation. |
| FL-07: Build the agent | Implementation present; raw run capture pending | `AI Fluency/FL-07-ai-arch-copilot` contains the working agent, tests, and build documentation. Add an unedited successful run recording. |
| PF-04: Personal website | Missing external deliverable | Publish a personal website over HTTPS and provide the live URL plus the DNS walkthrough. |
| FL-09: Documentation and demo video | Missing external deliverable | Add the final agent README and a 3 to 5 minute unlisted demo video link. |

## Notes

- The local `mars/` folder is preserved as source material and intentionally excluded from the GitHub repository. It should not be described as a submitted deliverable until it is moved into a dedicated A2 folder with its own README and verification evidence.
- A1, A2, and A3 still need the assignment-specific database or Swagger screenshots in their README files. FL-04, FL-05, and FL-07 still need live evidence captures. PF-04 and FL-09 are hosted or recorded submission deliverables rather than repository-only work.
