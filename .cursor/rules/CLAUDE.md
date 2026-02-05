# Project Chimera: AI Engineering Rules

## 1. The Prime Directive: Spec-Driven Development (SDD)

- NEVER generate implementation code without first reading the relevant file in `specs/`.
- If a spec is missing or ambiguous, ask the user to clarify the spec BEFORE writing code.
- Intent (Specs) > Implementation (Code).

## 2. Architecture Constraints

- **Pattern:** Use the FastRender Swarm (Planner -> Worker -> Judge).
- **Protocol:** All external data MUST be accessed via MCP Resources/Tools. No direct API calls in agent logic.
- **State:** Use Redis for short-term queues and Weaviate for long-term memory.

## 3. Testing Standards (TDD)

- Write the FAILING test first.
- Tests are the definition of "Done."
- Place tests in `tests/` mirroring the source structure.
