### Project Chimera – Specs Meta

This folder contains the **source of truth** for how Project Chimera should behave and how it should be implemented.  
All implementation work MUST trace back to these specs before code is written.

---

### 1. Vision & Scope

**Vision**  
Project Chimera builds **Autonomous Influencers**—agent swarms that can research trends, generate content, and manage engagement in the OpenClaw / Moltbook agent social network with strong safety and governance.

**Scope (v1)**

- Support end‑to‑end campaign flows for a small set of markets (e.g. Ethiopia) and channels (TikTok, Telegram, X/Twitter).
- Provide a clear Planner → Worker → Judge orchestration pattern (FastRender swarm).
- Integrate with MCP (for social/data I/O) and AgentKit (for basic economic actions) at the **design level**; full runtime implementation can come later.

Out of scope for v1:

- Full video rendering or media production pipelines.
- Sophisticated multi‑agent reputation systems on Moltbook.
- Advanced economic strategies (e.g. automated trading, complex DeFi).

---

### 2. Key Constraints & Assumptions

- **Specs > Code**: No feature is considered “real” unless it is defined here first (functional + technical).
- **HITL by Confidence**: The Judge’s 0–1 confidence score drives governance; thresholds are part of the spec.
- **Hybrid Persistence**: Postgres + Weaviate + Redis are treated as baseline assumptions for storage and memory.
- **MCP as Boundary**: All external integrations should be modeled as MCP resources/tools unless there is a strong reason otherwise.
- **Agent Roles Fixed (for v1)**: Planner, Worker, Judge exist as distinct logical roles; adding new roles requires updating specs first.

---

### 3. Specs Folder Map

- `functional.md`

  - Product‑level behavior and user stories.
  - End‑to‑end flows (e.g. Ethiopia launch campaign).
  - Non‑functional requirements that affect agent behavior (safety, latency, explainability).

- `technical.md`

  - System architecture and component interactions.
  - API contracts for internal skills and external MCP tools.
  - Data models and schema sketches (ERD‑style descriptions).

- `openclaw_integration.md`
  - How Chimera advertises status/availability into OpenClaw/Moltbook.
  - Protocols for posting updates, consuming signals, and managing identity.

---

### 4. Traceability Rules

- Each major feature or flow in `functional.md` should have a corresponding section or reference in `technical.md`.
- Commit messages that implement features should reference the relevant spec sections (e.g. `specs/functional.md#hitl-governance`).
- If behavior diverges from the spec, the spec MUST be updated before or alongside the code change.

---

### 5. SRS Mapping

| **SRS requirement / theme**                                 | **Covered in specs**                                                                                           |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Autonomous Influencer agents using Planner / Worker / Judge | `functional.md` (actors, user stories, flows) + `technical.md` (high-level architecture, services)             |
| MCP-based integration with external platforms and tools     | `technical.md` (MCP Integration Points) + `openclaw_integration.md` (resources, tools, safety rules)           |
| HITL governance via Judge confidence thresholds             | `functional.md` (HITL stories, NFRs) + `technical.md` (Judge thresholds, decisions, routing)                   |
| Data and memory stack (Postgres, Weaviate, Redis, ledger)   | `technical.md` (Data Layer, core data models, semantic memory) + `functional.md` (flows referencing storage)   |
| OpenClaw / Moltbook agent-network presence and signals      | `openclaw_integration.md` (identity, presence, MCP resources/tools) + `functional.md` (social network stories) |
| Agentic commerce and sponsorship / economic flows           | `openclaw_integration.md` (sponsorship & economic flows) + `technical.md` (MCP tools for economic actions)     |
