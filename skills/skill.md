## Chimera Core Skills (Draft)

This document outlines the initial **runtime skills** that the Chimera Agent will use.  
Each skill is a capability package (code + config) with a clear input/output contract.  
Implementation will follow after specs and tests are finalized.

For each skill we define:

- **Role integration** (Planner / Worker / Judge, and DAG position).
- **MCP boundary** (resource/tool name and key parameters).
- **Persistence contract** (Postgres / Weaviate / Redis).
- **Input/output validation** (required vs optional, enums, limits).
- **Error semantics** (how the Planner/Judge should react).

---

### 1. `skill_trend_fetcher`

**Version:** `v0.1`

**Purpose**  
Fetch and normalize trend signals (topics, hashtags, entities) from external sources (e.g., OpenClaw/Moltbook feeds, news APIs, social platforms) for a given region and time window.

**Role integration**

- Called by the **Planner** near the start of a campaign DAG to ground planning in current signals.
- May also be called by a **Worker** on demand for localized rechecks during long-running campaigns.
- Outputs are written into semantic memory so future plans can reuse historical trend snapshots.

**MCP & storage boundary**

- **MCP**: wraps one or more resources/tools, e.g.:
  - `mcp.resource: "moltbook://trends"`
  - `mcp.resource: "news://{region}/headlines"`
- **Persistence**:
  - **Weaviate**: store each trend snapshot as `TrendSnapshot` with embeddings of `label` and `evidence`.
  - **Postgres**: optional `trend_snapshots` table with `id`, `region`, `time_window`, `snapshot_time`.
  - **Redis**: cache latest snapshot IDs per `region` for fast Planner access.

**Inputs (JSON)**  
All payloads MUST include correlation metadata so artifacts can be traced through the DAG.

- `trace_id` (string, required): Correlates this call with a Planner DAG instance.
- `region` (string, required): ISO country code or market name, e.g. `"ET"` or `"ethiopia"`.
- `channels` (array[string], optional): Channels or sources to focus on.
  - Allowed values (initial): `"tiktok"`, `"telegram"`, `"twitter"`, `"news"`, `"moltbook"`.
- `time_window` (string, optional, default `"24h"`): Relative time window, e.g. `"24h"`, `"7d"`.
  - MUST match regex `^[0-9]+(h|d)$`.

**Outputs (JSON)**

- `trace_id` (string): Echo of input `trace_id`.
- `region` (string)
- `time_window` (string)
- `trends` (array[object]):
  - `id` (string): Stable identifier for the trend (e.g., hash of label + region + time window).
  - `label` (string): Human-readable label, e.g. hashtag or topic name.
  - `score` (number): Normalized importance score in \[0, 1\].
  - `channel_sources` (array[string]): Channels that contributed most to this trend.
  - `evidence` (array[string]): Example posts/headlines used to derive the trend.
- `errors` (array[object], optional):
  - `code` (string): e.g. `"NO_TRENDS_FOUND"`, `"UPSTREAM_RATE_LIMIT"`, `"INVALID_INPUT"`.
  - `message` (string): Human-readable explanation.
  - `retryable` (boolean): Whether the Planner should retry automatically.

**Planner/Judge behavior on errors**

- If `errors` contains only non-retryable issues → Planner should fallback to:
  - Prior `TrendSnapshot` from Weaviate (if available), or
  - A template-based generic plan.
- If `errors.retryable == true` and no trends returned → Planner may retry with a backoff or escalate to HITL if repeated.

---

### 2. `skill_content_generator`

**Version:** `v0.1`

**Purpose**  
Generate channel-specific content drafts (posts, captions, scripts) given a brief, target audience, and channel constraints.

**Role integration**

- Invoked by **Worker** agents responsible for “create copy / creative spec” tasks in the Planner DAG.
- The **Judge** consumes its outputs downstream, scoring each variant and deciding which go to HITL vs auto-schedule.
- May also be used by **Planner** for high-level narrative scaffolds (e.g., campaign story arcs).

**MCP & storage boundary**

- **MCP**:
  - Exposed as `mcp.tool: "chimera.content.generate"` with the JSON contract below.
- **Persistence**:
  - **Postgres**:
    - `campaign_artifacts` table: `artifact_id`, `campaign_id`, `channel`, `language`, `text`, `created_by_role`, `source_skill_version`.
  - **Weaviate**:
    - Class `ArtifactEmbedding` storing embeddings of `text` plus metadata for semantic reuse.
  - **Redis**:
    - Temporary cache of draft variants keyed by `task_id` during active DAG execution.

**Inputs (JSON)**

- `trace_id` (string, required): Correlates with Planner DAG instance.
- `task_id` (string, required): ID of the Worker task in the DAG.
- `campaign_id` (string, required)
- `brief` (string, required): High-level description of the campaign or message.
  - Recommended max length: 2,000 characters.
- `audience` (string, required): Target audience description, e.g. `"Ethiopian university students"`.
- `channel` (string, required): Target channel.
  - Allowed values (initial): `"tiktok"`, `"telegram"`, `"twitter"`, `"moltbook"`, `"youtube_short"`.
- `language` (string, optional, default `"en"`): Content language, e.g. `"am"` for Amharic, `"en"` for English.
- `tone` (string, optional): Desired tone, e.g. `"informative"`, `"playful"`, `"formal"`.
  - Should be mapped to a small controlled set in implementation.
- `constraints` (object, optional):
  - `max_length` (integer, optional): Hard cap on `text` length.
  - `banned_terms` (array[string], optional)
  - `required_phrases` (array[string], optional)
  - `safety_profile` (string, optional): e.g. `"strict"`, `"standard"`.

**Outputs (JSON)**

- `trace_id` (string)
- `task_id` (string)
- `campaign_id` (string)
- `variants` (array[object]):
  - `id` (string): Variant identifier (unique within the task).
  - `text` (string): The generated content body.
  - `channel` (string): Copy of the requested channel.
  - `language` (string): Final language used.
  - `estimated_read_time_sec` (number, optional)
  - `quality_score` (number, optional): Model-estimated quality in \[0, 1\] to help the Judge prioritize review.
- `errors` (array[object], optional):
  - `code` (string): e.g. `"CONSTRAINT_VIOLATION"`, `"INVALID_INPUT"`.
  - `message` (string)
  - `retryable` (boolean)

**Planner/Judge behavior on outputs**

- **Judge** uses `quality_score` and policy prompts to compute its own confidence score and route variants:
  - High-confidence, low-risk → auto-schedule via channel-specific MCP tools.
  - Borderline or sensitive → HITL dashboard.
- If `variants` is empty and `errors` is present:
  - Retry if `retryable == true` and constraints allow.
  - Otherwise escalate to HITL and/or ask Planner to adjust the DAG (e.g., relax constraints or change channel).

---

### 3. `skill_engagement_analyzer`

**Version:** `v0.1`

**Purpose**  
Analyze engagement metrics for published content and produce structured feedback for the Planner, Workers, and Judge.

**Role integration**

- Called periodically by a **Worker** or background process once metrics are available.
- Feeds **Judge** with artifact-level engagement and risk signals.
- Provides the **Planner** with recommendations to mutate or regenerate portions of the DAG (e.g., scale up winning variants, pause underperformers).

**MCP & storage boundary**

- **MCP**:
  - Exposed as `mcp.tool: "chimera.engagement.analyze"`.
- **Persistence**:
  - **Postgres**:
    - `engagement_snapshots`: `id`, `campaign_id`, `artifact_id`, `channel`, raw metrics, computed scores.
  - **Weaviate**:
    - Class `EngagementInsight` capturing text summaries and associated embeddings for retrieval into future plans.
  - **Redis**:
    - Recent snapshot IDs per `campaign_id` to accelerate repeated analyses during active experiments.

**Inputs (JSON)**

- `trace_id` (string, required)
- `campaign_id` (string, required): Identifier of the campaign.
- `artifacts` (array[object], required; non-empty):
  - `id` (string, required): Content/post identifier.
  - `channel` (string, required): Channel where content was published.
  - `metrics` (object, required):
    - `impressions` (number, optional)
    - `views` (number, optional)
    - `likes` (number, optional)
    - `comments` (number, optional)
    - `shares` (number, optional)
    - `clicks` (number, optional)
    - `conversions` (number, optional)
    - Additional channel-specific metrics MAY be included.

**Outputs (JSON)**

- `trace_id` (string)
- `campaign_id` (string)
- `summary` (object):
  - `top_performers` (array[string]): IDs of high-performing artifacts.
  - `underperformers` (array[string]): IDs of low-performing artifacts.
  - `insights` (array[string]): Human-readable observations (e.g., “short Amharic captions perform better on TikTok at night”).
- `artifact_scores` (array[object]):
  - `id` (string): Artifact ID.
  - `engagement_score` (number): Normalized score in \[0, 1\].
  - `risk_score` (number, optional): Anomaly or risk indicator in \[0, 1\] (e.g., suspicious spikes or negative sentiment).
  - `requires_human_review` (boolean, optional): Whether Judge/HITL should be alerted.
- `dag_recommendations` (array[object]):
  - `type` (string): e.g., `"SCALE_UP"`, `"PAUSE"`, `"REGENERATE"`, `"SHIFT_CHANNEL"`.
  - `target_artifact_ids` (array[string], optional)
  - `rationale` (string)
- `recommendations` (array[string]): High-level, human-readable next steps for Planner/Workers (e.g., “create more Variant B-style posts for Telegram”).
- `errors` (array[object], optional):
  - `code` (string): e.g. `"NO_VALID_METRICS"`, `"INVALID_INPUT"`.
  - `message` (string)
  - `retryable` (boolean)

**Planner/Judge behavior on outputs**

- **Judge**:
  - Uses `engagement_score` and `risk_score` to adjust future confidence thresholds or trigger HITL investigation when `requires_human_review == true`.
- **Planner**:
  - Consumes `dag_recommendations` to:
    - Spawn new Worker tasks to exploit winners.
    - Pause or regenerate campaigns that consistently underperform.
    - Rebalance channel mix for subsequent DAGs.

**Future extensions**

- Support multi-touch attribution and cohort-based analysis.
- Ingest sentiment analysis results as additional signals for `risk_score`.

---

### 4. `skill_persona_loader`

**Version:** `v0.1`

**Purpose**  
Loads and assembles the agent's persona context from SOUL.md (immutable DNA), episodic memory (Redis), and semantic long-term memory (Weaviate) into a formatted context string for injection into LLM system prompts.

**Role integration**

- Called by the **Planner** at campaign start to load persona constraints and ensure all DAG tasks respect personality boundaries.
- Called by **Workers** before content generation to assemble full context (SOUL.md + recent actions + relevant historical memories).
- Called by **Judge** to validate that generated artifacts align with the persona (persona consistency check).

**MCP & storage boundary**

- **File System / Git**: Reads SOUL.md from the path specified in `Persona.soul_md_path` (version-controlled repository).
- **Postgres**: Reads `Persona` table to get active persona version and file path for `agent_id`.
- **Redis**: Fetches episodic memory (last N hours) from keys `agent:{agent_id}:episodic:{timestamp}`.
- **Weaviate**:
  - Queries `ChimeraPersona` collection for persona embeddings and metadata.
  - Queries `PersonaMemory` collection for mutable memories (successful interactions, evolved traits).
- **No MCP tools/resources**: This is an internal skill that orchestrates data layer access.

**Inputs (JSON)**

- `trace_id` (string, required): Correlates with Planner DAG instance or Worker task.
- `agent_id` (string, required): Stable identifier for the agent (e.g., `"chimera-autonomous-influencer-et-v1"`).
- `include_episodic` (boolean, optional, default `true`): Whether to fetch recent episodic memory from Redis.
- `include_semantic` (boolean, optional, default `true`): Whether to query Weaviate for semantic memories.
- `episodic_window_hours` (number, optional, default `1`): How many hours of episodic memory to retrieve (max 24).
- `semantic_limit` (number, optional, default `5`): Maximum number of semantic memories to retrieve from Weaviate.

**Outputs (JSON)**

- `trace_id` (string): Echo of input `trace_id`.
- `agent_id` (string)
- `persona` (object):
  - `name` (string): Display name from SOUL.md frontmatter.
  - `agent_id` (string): Agent identifier.
  - `version` (string): Persona version (Git commit SHA or semantic version).
  - `voice_traits` (array[string]): List of voice characteristics (e.g., `["witty", "empathetic"]`).
  - `core_beliefs` (array[string]): Core values and beliefs (e.g., `["sustainability-focused"]`).
  - `directives` (array[string]): Hard constraints (e.g., `["Never discuss politics"]`).
  - `backstory` (string): Full backstory text from SOUL.md body.
  - `voice_guidelines` (string): Voice and tone guidelines from SOUL.md.
  - `core_values` (string): Core values section from SOUL.md.
- `episodic_memory` (array[object], optional):
  - `timestamp` (string): ISO 8601 timestamp.
  - `action` (string): Brief description of the action (e.g., `"replied_to_comment"`).
  - `context` (string): Relevant context snippet.
- `semantic_memories` (array[object], optional):
  - `id` (string): Weaviate object ID.
  - `content` (string): Memory content text.
  - `relevance_score` (number): Semantic similarity score [0, 1].
- `assembled_context` (string): **Formatted system prompt string** ready for LLM injection. Structure:

  ```
  # Agent Persona

  Name: {persona.name}
  Voice Traits: {persona.voice_traits.join(", ")}
  Core Beliefs: {persona.core_beliefs.join(", ")}

  ## Backstory
  {persona.backstory}

  ## Directives
  {persona.directives.map(d => `- ${d}`).join("\n")}

  ## Recent Context (Last {episodic_window_hours} hours)
  {episodic_memory.map(m => `[${m.timestamp}] ${m.action}: ${m.context}`).join("\n")}

  ## Relevant Memories
  {semantic_memories.map(m => `- ${m.content}`).join("\n")}
  ```

- `errors` (array[object], optional):
  - `code` (string): e.g., `"PERSONA_NOT_FOUND"`, `"REDIS_UNAVAILABLE"`, `"WEAVIATE_UNAVAILABLE"`, `"INVALID_SOUL_MD"`.
  - `message` (string): Human-readable explanation.
  - `retryable` (boolean): Whether the caller should retry.

**Planner/Worker/Judge behavior on outputs**

- **Planner**: Uses `assembled_context` to inject persona constraints into DAG planning prompts. If `persona.directives` conflict with campaign brief, Planner MUST escalate to HITL.
- **Worker**: Uses `assembled_context` as the system prompt prefix before generating content. Ensures all outputs reflect persona voice and values.
- **Judge**: Compares generated artifacts against `persona.voice_traits` and `persona.directives` to detect personality drift. If drift detected → lower confidence score or route to HITL.

**Error handling**

- If `PERSONA_NOT_FOUND` → non-retryable, escalate to HITL (agent cannot operate without persona).
- If `REDIS_UNAVAILABLE` or `WEAVIATE_UNAVAILABLE` → return persona-only context (degraded mode), log warning, continue execution.
- If `INVALID_SOUL_MD` → non-retryable, escalate to HITL (SOUL.md file is corrupted or malformed).

**Implementation notes**

- SOUL.md files MUST be stored in a version-controlled Git repository (GitOps pattern).
- The `Persona` table in Postgres tracks which SOUL.md version is active for each `agent_id`.
- Episodic memory in Redis should be TTL'd (e.g., expire after 24 hours) to prevent unbounded growth.
- Semantic memories in Weaviate are permanent and evolve over time (per FR 1.2: Dynamic Persona Evolution).
