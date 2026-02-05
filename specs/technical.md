### Technical Specification – Project Chimera

This document captures **architecture, data models, APIs, and integration details** that implement the behavior defined in `functional.md`, following the FastRender Swarm and MCP‑based design.

---

## 1. High‑Level Architecture

### 1.1 Logical Components

- **Planner Service**

  - Ingests campaign briefs and constraints.
  - Generates DAGs of tasks.
  - Schedules tasks onto a task queue (Redis).

- **Worker Service**

  - Stateless workers that:
    - Pull a single task from the queue.
    - Fetch required context (Postgres + Weaviate).
    - Call internal skills or external MCP tools.
    - Persist artifacts and results back to storage.

- **Judge Service**

  - Evaluates artifacts produced by Workers.
  - Assigns confidence scores and routing decisions.
  - Emits events for:
    - Auto‑execution (publish via MCP).
    - HITL review queue updates.
    - Retry/re‑plan requests to Planner.

- **MCP Gateway**

  - Defines and exposes MCP Resources/Tools used by Chimera.
  - Handles authentication, rate limiting, and logging of external calls.

- **Data Layer**
  - **Postgres** – campaigns, tasks, artifacts, logs.
  - **Weaviate** – semantic memory (persona, history, embeddings).
  - **Redis** – task queue + short‑term cache.

---

## 2. Core Data Models (Conceptual)

> Note: This is a conceptual ERD; actual schema details will be refined during implementation.

### 2.1 Campaigns & Tasks

- **Campaign**

  - `id` (UUID)
  - `name` (string)
  - `brief` (text)
  - `market` (string)
  - `channels` (jsonb: array of strings)
  - `constraints` (jsonb)
  - `status` (enum: draft | active | completed | cancelled)
  - `created_at`, `updated_at`

- **Task**
  - `id` (UUID)
  - `campaign_id` (FK → Campaign)
  - `type` (enum: trend_fetch | content_generate | experiment_setup | engagement_analysis | …)
  - `payload` (jsonb) – task‑specific input.
  - `status` (enum: pending | running | succeeded | failed)
  - `worker_id` (string, optional) – logical worker identifier.
  - `created_at`, `updated_at`

### 2.2 Artifacts & Judgments

- **Artifact**

  - `id` (UUID)
  - `campaign_id` (FK → Campaign)
  - `task_id` (FK → Task)
  - `kind` (enum: content | trend_summary | experiment_plan | metric_summary)
  - `channel` (string, optional)
  - `language` (string, optional)
  - `body` (jsonb or text) – raw artifact content.
  - `metadata` (jsonb) – additional structured fields.
  - `created_at`

- **Judgment**
  - `id` (UUID)
  - `artifact_id` (FK → Artifact)
  - `score` (float, 0.0–1.0)
  - `decision` (enum: auto_execute | hitl_review | reject_retry)
  - `rationale` (text)
  - `created_at`

### 2.3 Semantic Memory (Weaviate)

Collections (classes) in Weaviate:

- `ChimeraPersona`
  - Embeddings and metadata for SOUL.md / long‑term directives.
- `CampaignContext`
  - Summaries of past campaigns, decisions, and outcomes.
- `ContentSnippet`
  - High‑quality content fragments tagged with performance metrics (for retrieval‑augmented generation).

---

## 3. Internal Skill API Contracts

The following JSON contracts mirror `skills/skill.md` and are callable by Workers.

### 3.1 `skill_trend_fetcher`

**Input (JSON Schema, informal):**

```json
{
  "region": "string",
  "channels": ["string"],
  "time_window": "string"
}
```

**Output:**

```json
{
  "trends": [
    {
      "id": "string",
      "label": "string",
      "score": 0.0,
      "evidence": ["string"]
    }
  ]
}
```

### 3.2 `skill_content_generator`

**Input:**

```json
{
  "brief": "string",
  "audience": "string",
  "channel": "string",
  "language": "string",
  "tone": "string",
  "constraints": {}
}
```

**Output:**

```json
{
  "variants": [
    {
      "id": "string",
      "text": "string",
      "channel": "string",
      "language": "string"
    }
  ]
}
```

### 3.3 `skill_engagement_analyzer`

**Input:**

```json
{
  "campaign_id": "string",
  "artifacts": [
    {
      "id": "string",
      "channel": "string",
      "metrics": {}
    }
  ]
}
```

**Output:**

```json
{
  "summary": {
    "top_performers": ["string"],
    "underperformers": ["string"],
    "insights": ["string"]
  },
  "recommendations": ["string"]
}
```

---

## 4. MCP Integration Points

### 4.1 Resources

Examples of MCP resources the Planner/Workers may consume:

- `news://{region}/trends` – region‑specific news and social signals.
- `openclaw://moltbook/feeds/{agent_or_topic}` – agent network activity streams.

Workers treat these as **read‑only** sources; results may be normalized and stored as `CampaignContext` in Weaviate or as Artifacts in Postgres.

### 4.2 Tools

Examples of MCP tools the system may expose/use:

- `social.post_content`
  - Input: `{ "channel": "string", "content": "string", "metadata": {} }`
  - Output: `{ "post_id": "string", "url": "string" }`
- `openclaw.publish_status`

  - Input: `{ "agent_id": "string", "status": "string", "metadata": {} }`
  - Output: `{ "ok": true }`

- `openclaw.publish_update`
  - Purpose: publish high‑level, non‑sensitive campaign updates or insights to the agent network.
  - Input: `{ "agent_id": "string", "campaign_id": "string", "summary": "string", "tags": ["string"], "metadata": {} }`
  - Output: `{ "ok": true }`

For full JSON contracts of the OpenClaw tools, see `specs/openclaw_integration.md`. All calls to these tools must:

- Be **initiated via Judge‑approved decisions** (e.g., `decision = auto_execute` or an explicit “publish update” recommendation).
- Be logged with `campaign_id`, `decision_id` (or `judgment_id`), and timestamps for auditing.

---

## 5. Judge Thresholds (Operationalized)

The following thresholds implement the HITL policy from the functional spec:

- `score > 0.90` → `decision = auto_execute`

  - If `artifact.kind == "content"`, enqueue a `social.post_content` MCP tool call.

- `0.70 <= score <= 0.90` → `decision = hitl_review`

  - Artifact is written to a `review_queue` table or external dashboard backend.

- `score < 0.70` → `decision = reject_retry`
  - Planner receives a `retry` event with context:
    - Original artifact ID.
    - Judge rationale.
    - Suggested adjustments (e.g., stricter constraints or different prompt template).

These thresholds and behaviors MUST remain configurable (e.g., via environment or config files), but any changes must be reflected back into this spec.

---

## 6. Mapping to Functional User Stories

This section summarizes how the major behaviors in `functional.md` are implemented in this technical design and related integration specs:

- **Create a campaign from a brief / See a human‑readable campaign plan (Stories 2.1.1–2.1.2)**

  - Implemented by the **Planner Service** and the `Campaign` / `Task` models (Sections 1.1 and 2.1). Briefs, markets, channels, and constraints are stored on `Campaign`, and DAG construction is captured via `Task` records.

- **Constrain the campaign (Story 2.1.3)**

  - Constraints are represented in the `constraints` field on `Campaign` and propagated into Worker payloads and skill inputs (e.g., the `constraints` object on `skill_content_generator`).

- **Fetch localized trend data (Story 2.2.4)**

  - Implemented via `Task.type = "trend_fetch"` plus the `skill_trend_fetcher` contract and MCP resources such as `news://{region}/trends` and `openclaw://moltbook/feeds/{...}` (Sections 2.1, 3.1, and 4.1).

- **Generate channel‑specific content variants / Enforce brief and brand constraints (Stories 2.2.5–2.2.6)**

  - Implemented by `Task.type = "content_generate"`, the `skill_content_generator` contract (Section 3.2), and the `Artifact` model with `kind = "content"` plus constraint fields in the skill input schema.

- **Auto‑approve / route to dashboard / retry low‑confidence content / explain decisions (Stories 2.3.7–2.3.10)**

  - Implemented by the **Judge Service**, the `Judgment` model, and the thresholds and routing logic in Section 5 (`auto_execute`, `hitl_review`, `reject_retry`, with rationale text).

- **Consume agent‑network signals / Publish status back to the network (Stories 2.4.11–2.4.12)**

  - Read‑side behavior is covered by OpenClaw MCP resources in Section 4.1 and detailed in `openclaw_integration.md`.
  - Write‑side behavior is implemented via `openclaw.publish_status` and `openclaw.publish_update` tools (Section 4.2 and `openclaw_integration.md`).

- **Handle simple economic flows (Story 2.4.13)**
  - High‑level behavior is defined in `specs/openclaw_integration.md` (Section 5, sponsorship & economic flows) and linked to an AgentKit/ACP wallet layer. This technical spec assumes those flows are exposed as additional MCP tools (e.g., AgentKit transaction tools) invoked from Planner/Worker tasks under Judge‑ and config‑governed policies.
