### Tooling Strategy – Project Chimera

This document describes the **development tooling (for humans and IDE agents)** and the **runtime skills (for Chimera Planner/Worker/Judge)**. The goal is to keep these two worlds clearly separated while still allowing fast iteration.

---

### 1. Development MCP Servers & Tools (FDE / IDE Only)

These tools are for the **foundational developer experience (FDE)** and MUST NOT be called by production Chimera agents at runtime. They exist to help humans (and IDE copilots) understand, refactor, and maintain the codebase.

**Examples of dev MCPs:**

- **Filesystem / workspace servers**

  - Capabilities: read/edit files, search, list directories.
  - Usage:
    - Navigate specs in `specs/` and research docs in `research/`.
    - Apply small, incremental code and spec changes under SDD.

- **Git / version-control MCP**

  - Capabilities: view diffs, commit history, branches, and status.
  - Usage:
    - Ensure small, well-scoped commits referencing spec sections.
    - Support code review and traceability from changes back to specs and SRS.

- **Tenx / analysis MCPs (e.g., Tenx MCP Sense)**
  - Capabilities: repository analysis, pattern detection, feedback analytics.
  - Usage:
    - Understand technical debt, hotspots, and agent usage patterns.
    - Inform updates to `specs/` and `research/` based on real usage.

**Key rule:**  
These MCPs operate in the **developer context only**. They are not part of the Planner/Worker/Judge runtime swarm and should never be wired into production campaign flows.

---

### 2. Runtime Skills & MCP Boundaries (Chimera Agents)

Runtime capabilities for Chimera are expressed as **skills** with JSON I/O contracts, documented in `skills/skill.md`. These are what the **Planner / Worker / Judge** roles call during campaign execution.

At minimum, the following skills are defined:

1. **`skill_trend_fetcher`**

   - **Role mapping:**
     - Primarily used by **Planner** to ground campaign DAGs in up-to-date trend signals.
     - May be invoked by **Workers** for localized trend refreshes.
   - **MCP boundary:**
     - Wraps external trend sources as MCP resources (e.g., `moltbook://trends`, `news://{region}/headlines`).
   - **Data flow:**
     - Writes structured trend snapshots into Weaviate and Postgres, with Redis caching for fast Planner access.

2. **`skill_content_generator`**

   - **Role mapping:**
     - Invoked by **Workers** handling “generate creative” tasks in the Planner DAG.
     - Outputs are later evaluated by the **Judge**.
   - **MCP boundary:**
     - Exposed as an MCP tool (e.g., `chimera.content.generate`) with the JSON contract in `skills/skill.md`.
   - **Data flow:**
     - Persists artifacts in Postgres and embeddings in Weaviate; drafts are cached in Redis during active tasks.

3. **`skill_engagement_analyzer`**
   - **Role mapping:**
     - Triggered by **Workers** or background processes to analyze metrics for published content.
     - Feeds the **Judge** (for risk and performance signals) and the **Planner** (for DAG mutation recommendations).
   - **MCP boundary:**
     - Exposed as an MCP tool (e.g., `chimera.engagement.analyze`).
   - **Data flow:**
     - Stores engagement snapshots in Postgres and insights in Weaviate; recent snapshot IDs live in Redis.

All runtime skills **must**:

- Respect the **FastRender Swarm** pattern:
  - Planner builds DAGs.
  - Workers execute single, stateless tasks.
  - Judge evaluates outputs and drives HITL thresholds.
- Use MCP tools/resources for all external I/O instead of direct, ad hoc API calls.
- Conform to the JSON contracts defined in `skills/skill.md` for traceability and testing.

---

### 3. Separation of Concerns: Dev MCPs vs Runtime Skills

To keep the system safe and auditable:

- **Dev MCPs (for FDE / IDE):**

  - Operate only in the **development environment**.
  - Are used to read/write files, run analyses, and interact with git.
  - May view and update specs in `specs/`, research in `research/`, and code/tests in source directories.
  - **Never** participate directly in campaign execution or call external social networks or financial systems.

- **Runtime skills (for Chimera Planner/Worker/Judge):**
  - Are the only capabilities that production agents should use to:
    - Fetch trends and context from the agent social network or the wider web (via MCP).
    - Generate and analyze content.
    - Interact with economic or orchestration layers (e.g., AgentKit, queues).
  - Are designed with strong input/output contracts and logging to support Judge confidence scoring and HITL.

This separation ensures that:

- Developer tooling remains powerful but **sandboxed** to the engineering loop.
- Chimera agents in production rely exclusively on **well-specified skills** and MCP integrations that can be governed, tested, and audited.
