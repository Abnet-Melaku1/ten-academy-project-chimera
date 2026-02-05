### OpenClaw / Moltbook Integration – Project Chimera

This document specifies how Project Chimera integrates with the **OpenClaw / Moltbook agent social network** as an Autonomous Influencer.

It builds on the research in `research/strategy_report.md` and the behaviors defined in `specs/functional.md` and `specs/technical.md`.

---

## 1. Integration Goals

- **Discoverability** – Other agents and sponsors on Moltbook can discover Chimera, its capabilities, and availability.
- **Signal Consumption** – Chimera can read relevant agent‑network signals (trends, opportunities, collaboration requests) in a safe, structured way.
- **Status Broadcasting** – Chimera can publish status updates about campaigns, availability, and performance back to the network without leaking sensitive data.
- **Economic Participation** – Chimera can receive sponsorship offers and, where allowed, trigger on‑chain flows via AgentKit under governance rules.

---

## 2. Identity & Presence

### 2.1 Chimera Agent Identity

- **Agent ID**: A stable identifier used on OpenClaw/Moltbook (e.g. `chimera-autonomous-influencer-et-v1`).
- **Profile Metadata** (stored on Moltbook / OpenClaw profile):
  - `display_name`: e.g. `"Chimera – Autonomous Influencer"`.
  - `description`: Short description of role and capabilities.
  - `capabilities`: List of skills (trend analysis, content generation, engagement optimization).
  - `markets`: e.g. `["ET", "regional-east-africa"]`.
  - `channels`: e.g. `["tiktok", "telegram", "twitter"]`.

Chimera’s identity must be **stable**, and changes to capabilities/markets should be reflected in the profile.

### 2.2 Presence / Availability

Chimera exposes a simple status model:

- `status` (enum): `idle` | `running_campaign` | `maintenance` | `offline`.
- `current_campaigns`: Optional list of active campaign IDs with basic descriptors.

Status is periodically published to the network via an MCP tool (see below).

---

## 3. MCP Resources – Reading from OpenClaw / Moltbook

Chimera treats OpenClaw / Moltbook data as **MCP Resources**. Examples:

- `openclaw://moltbook/feeds/global`

  - Global feed of agent activities and posts.

- `openclaw://moltbook/feeds/{topic_or_hashtag}`

  - Topic‑specific stream (e.g. `openclaw://moltbook/feeds/ethiopia`).

- `openclaw://moltbook/agent/{agent_id}`
  - Activity stream and profile for a specific agent (for collaboration or benchmarking).

Workers that consume these resources must:

- Treat them as **read‑only** inputs.
- Normalize relevant content into internal structures (e.g. `CampaignContext` in Weaviate, or `Artifact` records) without copying raw prompts or unsafe instructions directly into runtime context.

---

## 4. MCP Tools – Writing to OpenClaw / Moltbook

Chimera uses MCP tools to **publish** limited, governed information back to the network.

### 4.1 `openclaw.publish_status`

- **Purpose**: Announce or update Chimera’s status and availability.
- **Input (JSON)**:

```json
{
  "agent_id": "string",
  "status": "idle | running_campaign | maintenance | offline",
  "current_campaigns": [
    {
      "campaign_id": "string",
      "market": "string",
      "channels": ["string"]
    }
  ],
  "metadata": {}
}
```

- **Output**:

```json
{ "ok": true }
```

### 4.2 `openclaw.publish_update`

- **Purpose**: Publish high‑level, non‑sensitive campaign updates or insights.
- **Input (JSON)**:

```json
{
  "agent_id": "string",
  "campaign_id": "string",
  "summary": "string",
  "tags": ["string"],
  "metadata": {}
}
```

- **Output**:

```json
{ "ok": true }
```

**Rule:** Only **aggregated** or **redacted** information is posted; no raw user data, secrets, or proprietary content is shared.

---

## 5. Sponsorship & Economic Flows (High‑Level)

Chimera’s integration with sponsorships involves two layers:

1. **Discovery & Intent (OpenClaw / Moltbook)**

   - Sponsors or other agents can post offers or collaboration requests mentioning Chimera’s agent ID.
   - Chimera can read these via MCP resources and surface them to a Strategist or supervisory agent.

2. **Execution (AgentKit / ACP)**
   - If an offer is accepted (by a human or governance agent), a separate on‑chain flow is initiated via AgentKit, **not** directly on Moltbook.
   - Any on‑chain action must:
     - Respect spending caps and allowlists defined in internal config/spec.
     - Be logged in Postgres as an auditable economic event.

The detailed AgentKit contract is defined in other technical docs; here we only require that OpenClaw acts as the **discovery and coordination layer**, not the wallet layer.

---

## 6. Safety & Governance for Integration

- **Prompt Injection & Malicious Posts**

  - OpenClaw content is treated as untrusted.
  - Workers ingesting feeds must:
    - Strip executable instructions.
    - Only extract structured signals (topics, metrics, sentiment).

- **Rate Limiting & Abuse Prevention**

  - Status and update posts must respect:
    - Rate limits (e.g., max N posts per hour).
    - Content policies from the Strategist/specs.

- **Traceability**
  - Every call to `openclaw.publish_status` or `openclaw.publish_update` should:
    - Be triggered via a Judge‑approved decision.
    - Be logged with `campaign_id`, `decision_id`, and a timestamp.

---

## 7. Mapping to Specs

- Functional stories affected:

  - **2.4.12 Publish status back to the network**
  - **2.4.11 Consume agent‑network signals**
  - **2.4.13 Handle simple economic flows**

- Technical spec linkage:
  - MCP tools/resources described here should be reflected in `specs/technical.md` under **MCP Integration Points**.
  - Any changes to integration behavior must be mirrored in both this document and `technical.md`.
