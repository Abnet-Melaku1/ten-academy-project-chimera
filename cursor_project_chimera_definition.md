# Project-chimera definition
_Exported on 2/6/2026 at 22:30:35 GMT+3 from Cursor (2.4.27)_

---

**User**

what is project-chimera

---

**Cursor**


Answering from the project's specs and docs.



**Project Chimera** is an **autonomous influencer system**—an agent swarm that runs multi-channel social campaigns inside the **OpenClaw / Moltbook** agent social network.

### Mission
Build **Autonomous Influencers**: persistent, goal-directed agent swarms that can plan, run, and adapt campaigns with strong safety and governance.

### How it works
- **Planner / Worker / Judge (FastRender Swarm)**  
  - **Planner**: builds DAGs of campaign tasks.  
  - **Worker**: runs single, stateless tasks.  
  - **Judge**: scores outputs, assigns confidence (0–1), and drives **HITL** (human-in-the-loop) routing.

- **Spec-driven**  
  Behavior and architecture are defined first in `specs/functional.md` and `specs/technical.md`; code follows those specs.

- **MCP as boundary**  
  External social/data I/O and tools are modeled as MCP resources/tools (see `specs/openclaw_integration.md`).

### Scope (v1)
- End-to-end campaign flows for a small set of markets (e.g. Ethiopia) and channels (TikTok, Telegram, X/Twitter).
- Planner → Worker → Judge orchestration.
- MCP and AgentKit integration at design level.

### Where to read more
- **Behavior & flows**: `specs/functional.md`
- **Architecture & data**: `specs/technical.md`
- **OpenClaw/Moltbook**: `specs/openclaw_integration.md`
- **Spec overview**: `specs/_meta.md`
- **Strategy & architecture rationale**: `research/strategy_report.md`, `research/architecture_strategy.md`

---

**User**

how does chimra integrated with openclaw?

---

**Cursor**


Here’s how Chimera integrates with OpenClaw according to **`specs/openclaw_integration.md`**:

---

## Integration goals

1. **Discoverability** – Other agents and sponsors on Moltbook can find Chimera, its capabilities, and availability.
2. **Signal consumption** – Chimera reads agent-network signals (trends, opportunities, collaboration requests) in a safe, structured way.
3. **Status broadcasting** – Chimera publishes campaign status, availability, and performance back to the network without leaking sensitive data.
4. **Economic participation** – Chimera can receive sponsorship offers and, under governance rules, trigger on-chain flows via AgentKit.

---

## Identity and presence

- **Agent ID**: A stable identifier on OpenClaw/Moltbook (e.g. `chimera-autonomous-influencer-et-v1`).
- **Profile metadata** on Moltbook/OpenClaw: `display_name`, `description`, `capabilities`, `markets`, `channels`.
- **Status model**: `idle` | `running_campaign` | `maintenance` | `offline`, plus optional `current_campaigns`. Status is published periodically via an MCP tool.

---

## MCP resources (reading from OpenClaw/Moltbook)

OpenClaw/Moltbook data is exposed as **MCP resources** (read-only):

- `openclaw://moltbook/feeds/global` – global feed of agent activities.
- `openclaw://moltbook/feeds/{topic_or_hashtag}` – topic streams (e.g. `openclaw://moltbook/feeds/ethiopia`).
- `openclaw://moltbook/agent/{agent_id}` – activity stream and profile for a specific agent.

Workers that consume these must treat them as read-only and normalize content into internal structures (e.g. `CampaignContext`, `Artifact`) without copying raw prompts or unsafe instructions into runtime context.

---

## MCP tools (writing to OpenClaw/Moltbook)

Chimera **publishes** via MCP tools:

- **`openclaw.publish_status`** – announce/update Chimera’s status and availability (`agent_id`, `status`, `current_campaigns`, optional `metadata`).
- **`openclaw.publish_update`** – publish high-level, non-sensitive campaign updates (`agent_id`, `campaign_id`, `summary`, `tags`, optional `metadata`).

Only aggregated or redacted information is posted; no raw user data, secrets, or proprietary content.

---

## Sponsorship and economic flows

- **Discovery & intent (OpenClaw/Moltbook)**: Sponsors or agents post offers or collaboration requests (e.g. mentioning Chimera’s agent ID). Chimera reads these via MCP resources and surfaces them to a Strategist or supervisory agent.
- **Execution (AgentKit/ACP)**: If an offer is accepted (by a human or governance agent), the on-chain flow runs via **AgentKit**, not Moltbook. On-chain actions must respect spending caps and allowlists and be logged in Postgres as auditable economic events. OpenClaw is the **discovery and coordination layer**, not the wallet layer.

---

## Safety and governance

- **Untrusted content**: OpenClaw content is untrusted; workers strip executable instructions and extract only structured signals (topics, metrics, sentiment).
- **Rate limiting**: Status and update posts must respect rate limits and content policies.
- **Traceability**: Every `openclaw.publish_status` or `openclaw.publish_update` call should be triggered by a Judge-approved decision and logged with `campaign_id`, `decision_id`, and timestamp.

---

For full contracts and linkage to functional/technical specs, see **`specs/openclaw_integration.md`** and the MCP Integration Points section in **`specs/technical.md`**.

