# Project Chimera Constitution

## Core Principles

### I. Spec-Driven Development (SDD) – Non-Negotiable

All implementation work MUST be driven by written specifications.

- `specs/functional.md` and `specs/technical.md` are the **primary sources of truth** for behavior and architecture.
- Implementation code MUST NOT be created or modified without first reading the relevant sections in `specs/` and, when relevant, `research/strategy_report.md` and `research/architecture_strategy.md`.
- If behavior is missing, ambiguous, or contradicts these documents, the spec MUST be updated and agreed before implementation proceeds.

### II. FastRender Swarm Architecture (Planner / Worker / Judge)

The runtime system MUST follow the FastRender Swarm pattern:

- **Planner**:
  - Owns DAG construction, task decomposition, and scheduling.
  - Is responsible for mapping user briefs to ordered, dependency-aware tasks.
- **Worker**:
  - Executes a single, stateless task at a time.
  - Retrieves only the minimal context required (Postgres + Weaviate) and calls well-defined skills/MCP tools.
- **Judge**:
  - Scores outputs in \[0.0, 1.0\], enforces HITL thresholds, and drives routing (auto-execute vs review vs retry).

Code MUST clearly belong to one of these roles and avoid mixing concerns in the same module.

### III. MCP-First Connectivity & Skills

All external I/O MUST go through Model Context Protocol (MCP) resources/tools or well-specified skills:

- Runtime agents MUST NOT call raw platform APIs directly from core logic.
- Skills MUST have JSON input/output contracts documented in `skills/skill.md`.
- Dev-only MCPs (filesystem, git, analysis tools) are for engineers and IDE agents only; production Chimera agents MUST NOT depend on them.

### IV. Test-Driven Development (TDD) & Contracts

Tests are the definition of "Done":

- Write failing tests first for new features and important bug fixes.
- Contract tests MUST reflect the JSON shapes and behaviors defined in `specs/technical.md` and `skills/skill.md`.
- The CI pipeline (GitHub Actions) MUST run `make test` on every push/PR; changes are not done until tests pass.

### V. Safety, HITL, and Observability

Safety and governance are first-class:

- The Judge’s confidence thresholds (e.g., >0.90 auto-execute, 0.70–0.90 HITL, <0.70 reject/retry) MUST be respected by all publishing and high-risk actions.
- Logs MUST include traceable IDs (`trace_id`, `task_id`, `campaign_id`) to support audit and incident review.
- Sensitive actions (posting content, on-chain spend) MUST be gateable by Judge + HITL and never bypass governance in code.

## Additional Constraints & Standards

- **Data & Storage**:
  - Use Postgres for transactional data, Weaviate for semantic memory, and Redis for queues/episodic state, as described in `research/architecture_strategy.md`.
  - Schema and class changes MUST be reflected in `specs/technical.md` before implementation.
- **Security**:
  - No secrets committed to the repo; configuration via environment or secrets managers.
  - External integrations must be treated as untrusted; mitigate prompt injection and data exfiltration via MCP boundaries.
- **Performance & Reliability**:
  - Planner and Judge are critical services; designs MUST include retry, backoff, and health monitoring strategies.

## Development Workflow & Quality Gates

- Every meaningful change SHOULD:
  - Reference the relevant spec and/or research section in description or commit message.
  - Include or update tests under `tests/` when touching runtime logic or skills.
- Speckit flows (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`) MUST:
  - Treat this constitution and `specs/` as authoritative.
  - Avoid generating implementation tasks that contradict FastRender Swarm or MCP-first constraints.
- AI-assisted changes (via IDE agents or review tools) MUST:
  - Explain their plan before editing files.
  - Maintain traceability to `specs/` and `research/`.

## Governance

- This constitution supersedes ad hoc practices for Project Chimera.
- Amendments:
  - MUST be proposed and documented as edits to this file.
  - MUST include a version bump and a short rationale in the commit message.
  - SHOULD be reflected in `.cursor/rules/agent.mdc` and `.coderabbit.yaml` if they affect AI behavior or review policies.
- Compliance:
  - Code review (human or AI) SHOULD check for adherence to:
    - SDD (spec alignment),
    - FastRender Swarm role separation,
    - MCP-only external I/O,
    - TDD and safety/HITL rules.

**Version**: 1.0.0 | **Ratified**: 2026-02-04 | **Last Amended**: 2026-02-04
