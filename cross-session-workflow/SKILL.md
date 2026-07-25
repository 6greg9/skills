---
name: cross-session-workflow
description: Establish or maintain a durable Codex project workflow that survives multiple chats or sessions. Use when Codex needs to create, repair, or continue AGENTS.md, planning, progress-handoff, and ADR decision-record structures for a repository.
---

# Cross-Session Workflow

Create a small, maintained project-memory system. `AGENTS.md` is the only automatic Codex instruction surface; the other Markdown files become reliable only when `AGENTS.md` tells future sessions to read and update them.

## Select the scope

- For a new project, create the root documents and `docs/decisions/` from `assets/`.
- For an existing project, read its guidance and documents first. Preserve its conventions; add only missing cross-session sections. Never replace an existing `AGENTS.md` wholesale.
- For a task that only needs a handoff, update the existing `PROGRESS.md` and, if needed, `PLAN.md`; do not create unnecessary files.

Do not use `PLAN.mc`: Codex gives it no special meaning. Do not create a single growing `DECISION.md`; use one ADR per material decision in `docs/decisions/`.

## Bootstrap or repair the structure

1. Inspect `AGENTS.md`, `README.md`, `PLAN.md`, `PROGRESS.md`, and `docs/decisions/`, plus the repository status.
2. For a new structure, copy and tailor these assets:
   - `assets/AGENTS.md.template`
   - `assets/PLAN.md.template`
   - `assets/PROGRESS.md.template`
   - `assets/ADR-template.md`
3. Give each document a non-overlapping responsibility:
   - `AGENTS.md`: durable operating rules and the required start/end-of-session protocol.
   - `PLAN.md`: current goal, milestones, scope, and acceptance criteria.
   - `PROGRESS.md`: a rolling handoff with completed work, present state, next action, blockers, and verification.
   - `docs/decisions/`: append-only ADRs for decisions whose rationale will matter later.
4. Adapt the templates to the actual project. Remove placeholder text and do not invent product requirements.
5. Ensure `AGENTS.md` requires every future session to read the plan, progress record, and relevant ADRs before work, and to update the records after a meaningful work unit.

## Maintain the system

At the start of a session, read the documents in the order specified by `AGENTS.md`, inspect the current tree and uncommitted changes, then reconcile the request with `PLAN.md`.

During work:

- Update `PLAN.md` when the goal, milestones, scope, or acceptance criteria change.
- Create an ADR before or with a decision that changes architecture, data models, public interfaces, dependencies, security posture, or a long-lived operating rule.
- Keep ADRs immutable after adoption. Supersede an old decision with a new ADR instead of rewriting history.

Before finishing a meaningful work unit, update `PROGRESS.md` with facts only: what changed, what remains, blockers or assumptions, and what verification ran or did not run. Avoid transcripts, raw logs, and temporary speculation.

## Verify

- Confirm every file referenced by `AGENTS.md` exists or is intentionally absent.
- Confirm `PLAN.md` and `PROGRESS.md` do not contradict the working tree or each other.
- Confirm each ADR has an identifier, date, status, context, decision, and consequences.
- Keep the structure lean. Prefer removing stale text over adding another status document.

