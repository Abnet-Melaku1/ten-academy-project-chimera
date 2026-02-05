### Agent Pattern

**Decision:** Chimera uses a **Hierarchical Swarm** based on the **FastRender** pattern, with three core roles: **Planner**, **Worker**, and **Judge**. This explicitly rejects a single Monolithic Agent in favor of a small, composable swarm that can be scaled, monitored, and governed.

**Planner – campaign graph engine**

- Translates a high-level brief (e.g., “Launch Product X in Ethiopia on TikTok and Telegram”) into a **Directed Acyclic Graph (DAG)** of tasks.
- Encodes dependencies between research, creative, experimentation, distribution, and analytics so that **independent branches can run in parallel**.
- Consults hybrid memory (Postgres + Weaviate) and live trend feeds (via MCP) to ground plans in **historical performance, content history, and current network signals**.

**Worker – stateless, horizontally scalable executors**

- Each Worker executes **exactly one task** from the Planner’s DAG, then terminates.
- Workers pull only the **minimal context** needed for their task (relevant trend snippets, campaign constraints, style guides, past winning posts), reducing context drift and prompt injection surface.
- This pattern is inherently **horizontally scalable**: more tasks simply mean more short-lived Workers pulling from Redis queues, which is ideal for bursty, high-velocity campaign workloads (e.g., reacting to trending videos).

**Judge – reliability and governance hub**

- Every Worker output (post copy, experiment plan, audience definition, budget suggestion) is scored by the Judge with a **confidence value in \[0.0, 1.0\]**.
- The Judge is where **brand, legal, regional, and economic constraints** are applied consistently, using both rules and retrieval from historical incidents and feedback stored in Weaviate/Postgres.
- Because Judge decisions are structured and logged, this role becomes the **primary reliability and audit surface** for the swarm and the main integration point for human reviewers.

**Why this pattern (reliability & scalability)**

- **Reliability:** Splitting cognition into Planner/Worker/Judge avoids tangled prompts that mix planning, execution, and evaluation. Each role is simpler, easier to test, and easier to upgrade independently as models or policies change.
- **Scalability:** FastRender-style Workers and Redis queues make it trivial to scale to hundreds or thousands of concurrent tasks when a campaign or trend spikes, without overloading a single long-running agent.
- **Traceability:** Planner DAGs, Worker task IDs, and Judge scores create a **structured event trail** for every artifact, which is critical in an agent social network where sponsors and platforms may demand explanations for actions.

---

### Human-in-the-Loop (HITL)

Chimera uses a **probability-based HITL framework** centered on the Judge’s confidence score for each artifact. The same thresholds are applied consistently across channels (TikTok, X/Twitter, Telegram, Moltbook posts, email, reports), with per-tenant tuning possible in Postgres.

**Core thresholds**

- **Score > 0.90 – Auto-execute**

  - The artifact is considered high-confidence and low-risk.
  - Examples:
    - Neutral product announcements that closely match previously approved templates.
    - Routine performance summaries or internal strategy memos.
  - Actions:
    - Auto-schedule posts to social channels via MCP tools.
    - Auto-update campaign metadata and experiment matrices.

- **0.70 ≤ Score ≤ 0.90 – HITL dashboard review**

  - The artifact is promising but not guaranteed safe or optimal.
  - Examples:
    - Posts that reference sensitive topics, humor, or region-specific culture (e.g., edgy memes for Ethiopia campaigns).
    - Budget recommendations that adjust spend by more than a configured percentage.
  - Actions:
    - Route to a **review dashboard** with:
      - Full context (brief, retrieved memory, trend snippets).
      - The Judge’s rationale and score.
      - Simple controls: **Approve**, **Edit & approve**, **Reject**.
    - Human decisions and comments are logged and fed back into memory as training signals for future Judge runs.

- **Score < 0.70 – Auto-reject and retry**
  - The artifact is low-confidence or likely unsafe.
  - Examples:
    - Content that appears off-brand, overly political, or inconsistent with campaign constraints.
    - Suspicious on-chain payment suggestions or actions that deviate from configured budgets.
  - Actions:
    - Automatically reject and **trigger a controlled retry loop**:
      - Planner may refine the DAG (e.g., add a safer fallback path).
      - New Workers are launched with stricter prompts, different retrieved memory, or reduced scope.
    - Optionally escalate to the dashboard if repeated low scores are detected for the same task.

**HITL checkpoints across the flow**

- **Before execution:** Judge scores Worker outputs and either auto-executes, queues for review, or rejects.
- **During execution:** Certain high-risk tool calls (e.g., on-chain transfers beyond a threshold, posting to new audiences) can require **explicit human approval** even if the Judge score is high, enforced by tool wrappers and MCP policies.
- **After execution:** Metrics anomalies (e.g., unusually negative sentiment or spikes in complaints) can trigger **retroactive HITL investigation**, surfacing the related artifacts, scores, and decisions.

This design keeps humans in control of sensitive edges while letting the swarm run **management-by-exception** for the bulk of routine campaign activity.

---

### Database Strategy (SQL vs NoSQL)

Chimera adopts a **hybrid data strategy**: **PostgreSQL + Weaviate + Redis**, instead of a pure SQL or pure NoSQL stack. This mirrors how the system actually reasons about campaigns: structured entities, semantic history, and fast-moving queues.

**PostgreSQL – transactional backbone**

- Stores **relational, highly-structured data**:
  - Tenants, users, permissions, and roles.
  - Campaigns, channels, briefs, and configuration.
  - Execution logs, Judge decisions, HITL actions, and tool call metadata.
- Provides **ACID guarantees** and strong schemas for anything that must be correct and auditable (e.g., which post was approved by whom, with what score and at what time).

**Weaviate – semantic memory over content history and trends**

- Holds **vector embeddings** for:
  - Historical campaign artifacts (captions, scripts, thumbnails, briefs).
  - Trend snapshots pulled from Moltbook/OpenClaw feeds and other MCP resources.
  - Post-mortems, feedback, and Judge rationales.
- Enables **semantic search and RAG**:
  - The Planner can ground new DAGs in what has worked before for similar audiences, geos, and channels.
  - Workers can generate new assets that reflect **brand voice, regional nuance, and historical performance** rather than starting from scratch.
- This is more flexible than trying to force all content history into rigid SQL schemas or generic NoSQL documents.

**Redis – high-velocity queues and episodic cache**

- Acts as the **fast lane** for:
  - Planner → Worker **task queues** (FastRender pattern) with visibility into which tasks are pending, in progress, or failed.
  - **Episodic state** such as in-flight campaign snapshots, short-term engagement metrics, and temporary feature flags.
- Ideal for **high-velocity video and campaign metadata** that needs millisecond access during active campaigns (e.g., current best-performing variant per channel) but can later be summarized and written back to Postgres/Weaviate.

**Why this mix instead of pure SQL/NoSQL**

- A pure SQL approach cannot efficiently handle **large-scale embeddings and fuzzy retrieval** over years of creative content and trend data.
- A pure NoSQL document store would make **relational integrity, governance, and analytics** (e.g., per-tenant audit trails, HITL KPIs) much harder to maintain.
- The chosen stack aligns with Chimera’s needs:
  - **Trend data** from the agent social network and public feeds is embedded into Weaviate for semantic reasoning.
  - **Content history and Judge/HITL outcomes** are split between Postgres (for structured audits and KPIs) and Weaviate (for retrieval into new campaigns).
  - **Fast queues and hot metadata** (e.g., active experiments, current leaderboard of variants) live in Redis, ensuring the swarm can react quickly to spikes in engagement or new trends.

Together, Postgres + Weaviate + Redis provide a **coherent memory fabric** for the hierarchical swarm, balancing reliability, scalability, and the ability to reason over high-velocity, multi-channel campaign data.
