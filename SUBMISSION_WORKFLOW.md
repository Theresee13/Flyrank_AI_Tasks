# Remaining Submission Workflow

The repository now contains the code and run instructions for the supplied backend and AI Fluency assignments. The items below require a live local runtime, personal account, camera, or portal access, so they cannot be truthfully generated from source code alone.

## 1. Capture A1 Swagger evidence

1. In `Assignment-01-fastapi-backend`, activate the virtual environment and run `uvicorn app.main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Use **Try it out** to create, read, update, and delete a task.
4. Take one screenshot showing the Swagger page and at least one successful response. Keep it locally or add it under `Assignment-01-fastapi-backend/docs/` with no secrets visible.

## 2. Run A7 in the Inngest dashboard

Completed locally on 2026-09-09. The A7 README contains the real request IDs, statuses, durations, and dashboard outcomes. Repeat these steps only when you need fresh screenshots for a portal submission.

1. In `Assignment-07-inngest-background-jobs`, create and activate a virtual environment, then run `pip install -r requirements.txt`.
2. Terminal one: `uvicorn main:app --reload`.
3. Terminal two: `inngest dev -u http://localhost:8000/api/inngest`.
4. Send `POST /reports` with `{ "topic": "cats" }`, then poll the returned URL until it becomes `done`.
5. Send `{ "topic": "fail" }` and capture the dashboard showing three failed attempts. Wait two minutes and capture two heartbeat runs.
6. Paste the real responses and screenshots into the A7 README. Do not invent timestamps or dashboard output.

## 3. Render and inspect A8's PDF

1. In `Assignment-08-pdf-report-generator`, create and activate a virtual environment.
2. Run `pip install -r requirements.txt`, then `playwright install chromium`.
3. Run `python seed.py` and `uvicorn main:app --reload`.
4. `POST /reports`, download the returned file URL, and open the PDF.
5. Confirm the report has at least two pages, repeated table headers, and no split rows. Capture page one and add the real response and screenshot to the A8 README.
6. Send a second `POST /reports` on the same day and confirm it returns the same ID. Send `{ "force": true }` to confirm a new report is created.

## 4. Run A9 against the practice sandbox

Completed locally on 2026-09-09. The A9 README records the real outcomes: 60 validated, de-duplicated records from three catalogue pages; a 1.81-second cache rerun with 63 cache hits and no live content pages fetched; and the intentionally injected 404 recorded in `errors.json` while all 60 good records remained. The included unit suite also passed (`3 passed`).

## 5. Verify Gemini-backed projects

1. Revoke the API key previously pasted in chat and create a replacement in Google AI Studio.
2. Put the replacement only in ignored local `.env` or `.env.local` files. Never commit it.
3. Decision Flow Studio was verified locally on 2026-09-09 with real Gemini calls: one completed `YES` support-triage run and one completed `NO` sales-triage run. The project README contains both run IDs and outcomes. Capture the completed execution-log UI manually if portal evidence is required.
4. RuleGuard was verified locally on 2026-09-09 with a real Gemini FAISS index, a successful HTTP 200 judgement, backend tests (`39 passed`), frontend tests (`21 passed`), a passing frontend build, and a live evaluation score of `7/8 (87.5%)`. The one mismatch was case-05: expected `data_security`, received `authentication`. Capture the RuleGuard result UI manually if portal evidence is required.

## 6. Complete the AI Fluency submission items

1. Record a 3–5 minute live demo of the chosen agent or workflow. Show a real end-to-end run, explain one design decision and one limitation, then upload it as an unlisted video.
2. Add the video URL, actual evaluation results, limitations, and a short AI-use transparency note to that project README.
3. Write the 500–800 word retrospective in your own voice. Include what changed, what you would build next, and three transferable lessons.
4. Complete the hours log, publish the personal FlyRank-domain site and build-in-public post, then submit for the required human review. These portal and publishing actions must be performed by you under your own account.

## Commit History

The repository has five authentic commits. The original briefs ask for one meaningful commit per stage, but those staged historical commits cannot be recreated honestly after the work. Keep future verification changes in focused commits with the real command output or screenshot they add.
