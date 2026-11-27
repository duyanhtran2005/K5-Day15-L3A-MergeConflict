# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python standard library HTTP server (`http.server`) inside `codebase/app.py` serving a modern HTML/CSS/Vanilla JS single-page web application (`codebase/ui/`), launched via `python run.py` with zero external npm or pip dependencies required by default.

## Users

- **Primary user:** AI20K Class L3A learners currently working through a lab session and needing fast, reliable help to submit work or get unblocked.
- **Secondary / reviewer roles:** Lab coordinators / coaches who review escalated handoff drafts before dispatch, plus the MergeConflict team demonstrating system behavior, citations, and live trace metrics during hackathon evaluation.

## Product Purpose

Help L3A learners quickly resolve lab-session questions (submission deadlines, repo naming rules, where to find lab instructions on LMS vs program GitHub, and who to contact for help) without scanning scattered announcements or asking repeatedly across multiple channels.

## Positioning

A grounded Track A2 lab-support assistant that combines official lab announcements and coach/TA shift rosters to decide strictly between three safe paths:
1. Answer directly with verifiable source citations when an active official rule exists.
2. Ask targeted clarifying follow-up questions when critical learner context is missing.
3. Draft a structured handoff to the matching on-duty coach/TA for human coordinator approval, never sending external messages automatically.

## Operating Context

- **Single launch contract:** `python run.py` launches `codebase/app.py`, serving the web UI on localhost while preserving `python run.py eval`, `python run.py simulate`, and `python run.py check`.
- **Agent & tracing contracts:** `codebase/agent.py` exposes `answer(text: str) -> {"output": str, ...}`; `codebase/ai.py` uses `@model_call` and supports both `MODEL_PROVIDER=fake` (offline/unkeyed fallback) and real API keys via `.env`; `codebase/tools.py` exposes `@tool` functions logged by `codebase/tracing.py`.
- **Three core demo scenarios (from `canvas.md`):**
  1. Submission deadline inquiry answered with official source citation.
  2. Pre-lab repository naming convention inquiry (`K5-Day15-<lớp>-<tên nhóm>` / lab rules).
  3. Finding where afternoon lab instructions live (LMS vs program GitHub) and the appropriate support channel / coach roster.
- **Safety & governance (`AGENTS.md`, `canvas.md`):** External actions (escalating/routing to a coach) produce a draft awaiting human coordinator approval rather than auto-sending.

## Capabilities and Constraints

- **Must support:** Grounded answers with source IDs/timestamps, ambiguity clarification prompts, out-of-scope / policy refusal with safe redirection, draft handoff creation and coordinator approval/edit queue, and live Trace / Model / Token inspection per turn.
- **Offline / dual-mode capability:** Works smoothly with structured Track A2 sample data (`data/`) even when `.env` uses `MODEL_PROVIDER=fake`, and seamlessly switches to real LLM reasoning when a real provider/API key is configured in `.env`.
- **Framework boundaries:** Do NOT modify `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, or `run.py`. Do NOT commit `.env`, API keys, or real personal student PII.
- **Honesty boundary:** Sample announcements and coach rosters in `data/` must be clearly labeled as synthetic/sample demo data in `data/DATA_CARD.md` and UI notices, with no fabricated interview evidence or benchmark metrics.

## Brand Commitments

- **Team & identity:** MergeConflict · Class L3A · Track A (EdTech A2).

## Evidence on Hand

- Confirmed scope, users, 3 demo scenarios, and team roles in `canvas.md` and `TEAMS.md`.
- Pain evidence (`evidence/summary.md`, interviews/surveys/data-mining) and final evaluation runs (`eval/benchmark.csv`, `eval/run-*.csv`) are not yet collected/completed and must not be fabricated in the UI.

## Product Principles

1. **Verifiable Grounding Over Guessing:** Every factual lab rule or deadline states its source ID and effective date; missing or expired coverage triggers explicit clarification or escalation rather than fabrication.
2. **Human-in-the-Loop Escalation:** Routing a learner's question to a coach/TA produces an inspectable draft queued for coordinator approval; nothing is dispatched silently.
3. **Zero-Friction Local Demo:** `python run.py` starts the full web UI immediately with Python stdlib only, degrading gracefully between live LLM and deterministic offline mode.
4. **Transparent System Behavior:** Learners see clear citations and next actions; coordinators and demo evaluators can inspect tool calls, model usage, latency, and token counts per turn.

## Accessibility & Inclusion

- Primary UI language in clear, concise Vietnamese matching the L3A cohort context, with full keyboard navigation, WCAG AA text/control contrast, and `prefers-reduced-motion` support.
