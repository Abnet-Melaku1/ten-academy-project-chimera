### Functional Specification – Project Chimera

This document defines **user-facing behaviors, agent responsibilities, and end-to-end flows** for Project Chimera.  
It is the primary source of truth for how Chimera should behave from a **product and agent** perspective.

---

## 1. Primary Actors

- **Strategist (Human)** – Provides campaign briefs, constraints, and reviews sensitive or low‑confidence artifacts.
- **Chimera Planner (Agent)** – Decomposes briefs into DAGs of tasks and orchestrates Workers and Judges.
- **Chimera Worker (Agent)** – Executes a single task (e.g., draft content, fetch trends) and terminates.
- **Chimera Judge (Agent)** – Evaluates artifacts, assigns confidence scores, and decides routing (auto, HITL, retry).
- **External Channels** – Social platforms (TikTok, Telegram, X/Twitter, etc.) accessed via MCP tools/skills.
- **OpenClaw / Moltbook Network** – Agent social network providing trend signals and agent interactions via MCP.

### 1.2 Human–Agent Interaction (UI and Other Methods)

Humans (Strategists and operators) must be able to interact with the agent system through multiple modalities so that different workflows, tools, and preferences are supported. The following should be considered:

- **UI (primary)** – A dashboard or web application where Strategists can submit campaign briefs, view human‑readable campaign plans, manage the HITL review queue (approve, edit, reject artifacts), see Judge rationales, and monitor campaign status. This is the primary interface for day‑to‑day human–agent interaction.
- **API** – Programmatic access for brief submission, plan retrieval, artifact review, and status queries so that automation, integrations, and custom tooling can drive or complement the UI.
- **Other methods** – Chat interfaces (e.g. conversational brief submission or Q&A with the Planner), CLI tools for operators, notifications (e.g. when items enter the HITL queue or when campaigns complete), and future modalities should be considered in the architecture so that the system remains extensible and usable across contexts.

All human-facing interfaces MUST consume the same backend services (Planner, Judge, review queue) and respect the same HITL thresholds and safety rules; the choice of UI, API, chat, or CLI is a presentation-layer concern.

---

## 2. Core User Stories

### 2.1 Strategist–Planner Stories

1. **Create a campaign from a brief**

   - _As a Strategist_, I want to submit a high‑level brief (goal, target audience, channels, region, time window)  
     so that the Planner can produce a DAG of tasks for an Autonomous Influencer campaign.

2. **See a human‑readable campaign plan**

   - _As a Strategist_, I want to see a human‑friendly summary of the DAG (phases, tasks, dependencies)  
     so that I can validate the plan before content generation begins.

3. **Constrain the campaign**

   - _As a Strategist_, I want to specify hard constraints (banned topics, languages, tone, legal rules)  
     so that the Planner, Workers, and Judge respect these constraints automatically.

4. **Define agent persona via SOUL.md**

   - _As a Strategist_, I want to define agent personas via SOUL.md files (backstory, voice, values, directives)  
     so that personality remains consistent across thousands of posts and campaigns, ensuring brand identity is preserved.
   - _As a Strategist_, I want persona definitions to be version-controlled (GitOps)  
     so that persona changes are auditable and can be rolled back if needed.

5. **Ensure persona consistency in content**

   - _As a Planner/Worker Agent_, I want to load the agent's SOUL.md persona before generating content  
     so that all outputs reflect the defined personality, voice, and ethical boundaries.

6. **Interact with agents via UI**

   - _As a Strategist_, I want to use a dashboard or web UI to submit briefs, view campaign plans, and manage the HITL review queue  
     so that I can work with the agents in a single, human-friendly interface.

7. **Interact via API or other methods**
   - _As a Strategist or operator_, I want to use an API, chat, CLI, or notifications to submit briefs, query status, or respond to HITL items  
     so that I can integrate with existing tools or prefer a non-UI workflow when appropriate.

### 2.2 Planner–Worker Stories

8. **Fetch localized trend data**

   - _As a Planner Agent_, I want to call a trend‑fetching skill or MCP resource  
     so that I can ground my campaign plan in up‑to‑date, region‑specific trends.

9. **Generate channel‑specific content variants**

   - _As a Worker Agent_, I want to generate multiple content variants for a specific channel and audience  
     so that the Strategist (and Judge) can choose or test the best‑performing options.

10. **Enforce brief and brand constraints**

- _As a Worker Agent_, I want to receive explicit constraints (tone, banned terms, length limits)  
  so that all generated content stays within brand and compliance boundaries.

11. **Assemble persona context for content generation**

- _As a Worker Agent_, I want to assemble context from SOUL.md, recent episodic memory, and semantic long-term memory  
  so that generated content reflects both the immutable persona and relevant historical interactions.

### 2.3 Judge–Strategist Stories (HITL)

12. **Auto‑approve high‑confidence content**

- _As a Judge Agent_, I want to auto‑approve and schedule content when confidence > 0.90  
  so that the system can operate autonomously for low‑risk artifacts.

13. **Route medium‑confidence content to dashboard**

- _As a Judge Agent_, I want to send content with 0.70 ≤ confidence ≤ 0.90 to a human review queue  
  so that Strategists can approve, edit, or reject borderline artifacts.

14. **Flag and retry low‑confidence content**

- _As a Judge Agent_, I want to reject and trigger a retry or re‑plan when confidence < 0.70  
  so that unsafe or low‑quality content never reaches external channels.

15. **Explain decisions**

    - _As a Strategist_, I want to see why the Judge approved, rejected, or escalated an artifact  
      so that I can trust and tune the governance logic.

16. **Validate persona consistency**
    - _As a Judge Agent_, I want to verify that generated content aligns with the agent's SOUL.md persona  
      so that personality drift is detected and corrected before publication.

### 2.4 Social Network & Economic Stories

17. **Consume agent‑network signals**

    - _As a Planner Agent_, I want to read from OpenClaw/Moltbook feeds (via MCP resources)  
      so that campaigns can leverage current agent‑level activity and collaborations.

18. **Publish status back to the network**

    - _As an Autonomous Influencer_, I want to post status updates and availability to the agent social network  
      so that other agents and sponsors can discover and collaborate with me.

19. **Handle simple economic flows**
    - _As an Autonomous Influencer_, I want to track a small on‑chain budget and basic P&L (via AgentKit)  
      so that I can pay for compute or receive sponsorship funds under configured limits.

---

## 3. End‑to‑End Flows

### 3.1 Ethiopia Launch Campaign (Happy Path)

**Goal:** Launch Product X in Ethiopia targeting university students on TikTok and Telegram over 2 weeks.

1. **Brief submission**
   - Strategist submits a campaign brief (goal, audience, channels, constraints) via a UI or API.
2. **Planning**
   - Planner reads the brief + historical context (Postgres + Weaviate).
   - Planner loads the agent's SOUL.md persona to ensure all tasks respect personality constraints.
   - Planner calls a trend skill/MCP resource (e.g., `news://ethiopia/trends`) and constructs a DAG:
     - Collect and summarize local trends.
     - Draft TikTok and Telegram content variants (Amharic + English).
     - Define experiment matrix (variants × channels × schedule).
3. **Task execution**
   - Workers execute DAG tasks one by one:
     - Trend Worker normalizes trends into a standard structure.
     - Content Worker assembles context (SOUL.md + episodic memory + semantic memory) and generates multiple caption variants per channel.
     - Experiment Worker builds an experiment setup object (with metadata for Judge).
4. **Judging & HITL**
   - Judge evaluates each artifact, assigns confidence, and routes:
     - High confidence → auto‑schedule via MCP posting tools.
     - Medium confidence → human review queue/dashboard.
     - Low confidence → auto‑reject and retry planning or generation.
5. **Monitoring & adaptation**
   - Engagement Analyzer skill ingests metrics from channels.
   - Planner uses these insights to spawn new Worker tasks (iteration on best‑performing variants).

**Outcome:**  
The campaign runs with a mix of autonomous and human‑approved content, while all actions remain traceable and spec‑aligned.

### 3.2 Failing Content & Re‑Plan (Error Path)

1. Worker generates content that is off‑tone or borderline sensitive.
2. Judge assigns a low confidence score (< 0.70) and rejects it.
3. Planner receives a signal to:
   - Adjust constraints (e.g., tone, banned phrases) or
   - Break the task into smaller, clearer subtasks.
4. A new Worker run produces revised content; Judge re‑evaluates and either:
   - Escalates to human review, or
   - Approves if confidence is now sufficiently high.

---

## 4. Non‑Functional Requirements (Functional Impact)

- **Safety & Brand Protection**

  - All content that touches external channels must pass through the Judge and respect HITL thresholds.
  - The system must log decisions and confidence scores for post‑hoc audits.

- **Explainability**

  - For each decision (approve, reject, escalate), the Judge must provide a short textual rationale.

- **Latency (Agent UX)**

  - For interactive Strategist flows (e.g., previewing a campaign plan), responses should typically be under a few seconds.

- **Spec Alignment**

  - When behavior changes (e.g., new thresholds, new channels), the functional spec must be updated first, then technical spec, then implementation.

- **Persona Consistency**
  - All content generated by Workers MUST be evaluated by the Judge against the agent's SOUL.md persona to prevent personality drift.
  - Persona definitions are immutable at runtime; changes require version-controlled updates and agent restart/reload.
