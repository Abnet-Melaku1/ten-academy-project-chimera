---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md, while enforcing Chimera’s Spec-Driven Development and FastRender Swarm architecture.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Respect Spec-Driven Development (SDD)**

   - Before changing any files, briefly explain your plan:
     - What you are going to change.
     - Which files will be touched.
     - How changes map back to:
       - `specs/functional.md` and `specs/technical.md`
       - `research/strategy_report.md` and `research/architecture_strategy.md`
       - `skills/skill.md` (for any runtime skills).
   - NEVER implement behavior that is not traceable to these documents.

2. **Load Chimera implementation context**

   - From the repo root, load the following (read-only):
     - `specs/functional.md` – user-facing flows and behaviors.
     - `specs/technical.md` – architecture, data models, skill contracts.
     - `research/strategy_report.md` – overall strategy and constraints.
     - `research/architecture_strategy.md` – FastRender Swarm, HITL, data stack.
     - `skills/skill.md` – runtime skills and JSON I/O contracts.
     - `tasks.md` – global task list for this challenge (if present).
   - Use these documents as the **single source of truth** for implementation decisions.

3. **Check checklists status (if using feature-specific checklists)**

   - If a `checklists/` directory exists for the current feature or spec:

     - Scan all checklist files and compute:
       - Total items: lines matching `- [ ]` or `- [X]` or `- [x]`
       - Completed items: lines matching `- [X]` or `- [x]`
       - Incomplete items: lines matching `- [ ]`
     - Produce a status table similar to:

       ```text
       | Checklist   | Total | Completed | Incomplete | Status |
       |-------------|-------|-----------|------------|--------|
       | requirements.md | 20 | 18        | 2          | ✗ FAIL |
       ```

   - If any checklist is incomplete:
     - Display the table.
     - Ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Honor the user’s choice; do not proceed if they say "no"/"wait"/"stop".

4. **Parse tasks.md structure and extract execution plan**

   - Treat `tasks.md` as the canonical execution plan for this repo.
   - Parse:
     - **Task phases**: Setup, Tests, Core, Integration, Polish.
     - **Task dependencies**: sequential vs `[P]` parallel markers.
     - **Task details**: ID, description, file paths, story labels, Planner/Worker/Judge implications where applicable.
   - NEVER invent new tasks silently; if tasks are missing, pause and suggest updating `tasks.md` via `/speckit.tasks`.

5. **Execute implementation in FastRender-aligned phases**

   - **Setup first**:
     - Ensure Python environment, Dockerfile, Makefile, and CI config match `pyproject.toml` and `research/tooling_strategy.md`.
   - **Tests before code**:
     - For each task that adds or updates a runtime skill or service, prefer writing/updating tests under `tests/` first.
   - **Planner / Worker / Judge separation**:
     - When editing or adding code, be explicit about which role it belongs to:
       - Planner: DAG construction, task scheduling.
       - Worker: stateless task execution calling skills/MCP tools.
       - Judge: scoring, HITL thresholds, routing.
     - Avoid mixing Planner, Worker, and Judge concerns in the same module.

6. **File-based coordination and safety**

   - Tasks affecting the same files MUST run sequentially.
   - For any external I/O or platform interaction:
     - Ensure it is routed through MCP tools/resources or well-defined skills.
     - Do NOT add ad hoc direct API calls in agent logic.

7. **Progress tracking and error handling**

   - After each completed task:
     - Report concise progress (e.g., "Completed T00X: <description>").
     - Optionally mark the task as `[X]` in `tasks.md` if this repo is using that convention.
   - If a task fails:
     - Stop and report the error with context.
     - Suggest whether to:
       - Fix the spec/plan (`specs/`), or
       - Adjust the task definition (`tasks.md`), or
       - Fix implementation code.

8. **Completion validation**
   - Verify:
     - All in-scope tasks in `tasks.md` are completed or explicitly deferred.
     - Implemented behavior matches `specs/functional.md` and `specs/technical.md`.
     - Tests in `tests/` run (via `make test`) and fail only where implementation is intentionally incomplete.
   - Summarize:
     - Key files changed.
     - Which parts of Planner/Worker/Judge were touched.
     - Any remaining gaps that require spec or task updates.

Note: This command assumes a Chimera-style SDD workflow where `specs/` and `research/` are the authoritative sources. If they are missing or clearly outdated for the requested feature, pause and recommend updating specs before further implementation.
