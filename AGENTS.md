# User-Level Agent Instructions

## Rough Or High-Level Requests

Use this when the user gives a high-level or rough request or requirements are still fuzzy.

- Restate the goal as a concrete deliverable (what will exist when done).
- Surface unknowns early:
  - If blocked, ask up to 3 targeted questions.
  - If not blocked, proceed with reasonable defaults and state assumptions explicitly.
- Split the work and deliver iteratively:
  - MVP first (smallest working version).
  - Confirm direction before expanding scope or doing broad refactors.
- Prefer minimal, reversible changes over "big-bang" rewrites.
- Always include a verification step (tests, build, run, or a repro checklist).

## Skill Authoring Requests

Use this when the user asks to add or create a new skill.

- Write `SKILL.md` content in English.
- Keep all user-facing conversation in Japanese.
