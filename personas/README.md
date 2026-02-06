# Persona Definitions (SOUL.md)

This directory contains **SOUL.md** files that define the immutable persona "DNA" for each Chimera agent.

## What is SOUL.md?

SOUL.md is a standardized markdown file with YAML frontmatter that serves as the **immutable DNA** of an agent persona. It ensures personality consistency across thousands of posts and campaigns.

## File Structure

Each SOUL.md file MUST contain:

1. **YAML Frontmatter** (required fields):

   - `name`: Display name
   - `agent_id`: Stable identifier (e.g., `chimera-autonomous-influencer-et-v1`)
   - `version`: Semantic version or Git commit SHA
   - `voice_traits`: Array of voice characteristics
   - `core_beliefs`: Array of core values
   - `directives`: Array of hard constraints

2. **Markdown Body** (required sections):
   - `# Backstory`: Narrative history
   - `# Voice & Tone Guidelines`: Stylistic characteristics
   - `# Core Values`: Ethical principles
   - `# Personality Traits`: Behavioral characteristics
   - `# Content Themes & Interests`: Focus areas
   - `# Interaction Style`: Engagement patterns

See `SOUL.md.template` for a complete example.

## Usage

1. **Create a new persona:**

   ```bash
   cp SOUL.md.template agents/{agent_id}/SOUL.md
   # Edit the file with agent-specific details
   ```

2. **Version control:**

   - Commit SOUL.md files to Git (GitOps pattern)
   - Update the `Persona` table in Postgres with the new `soul_md_path` and `version`

3. **Runtime loading:**
   - The `skill_persona_loader` skill reads SOUL.md files at runtime
   - Persona context is assembled and injected into LLM system prompts

## Directory Structure

```
personas/
├── README.md (this file)
├── SOUL.md.template
└── agents/
    ├── chimera-autonomous-influencer-et-v1/
    │   └── SOUL.md
    └── chimera-autonomous-influencer-ke-v1/
        └── SOUL.md
```

## Integration with Specs

- **Functional Spec**: `specs/functional.md` Section 2.1.4-2.1.5 (persona definition stories)
- **Technical Spec**: `specs/technical.md` Section 2.3 (Persona data model)
- **Skills Spec**: `skills/skill.md` Section 4 (`skill_persona_loader`)

## Best Practices

1. **Immutability**: SOUL.md defines the core, unchanging personality. For evolving traits, use the `PersonaMemory` collection in Weaviate.

2. **Specificity**: Be detailed in backstory and voice guidelines. Vague personas lead to inconsistent content.

3. **Testability**: After creating/updating SOUL.md, generate sample content and validate it matches the persona.

4. **Versioning**: Always increment version numbers and commit to Git before activating in production.
