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
- When defining command-line arguments or environment variables:
  - Start with the minimum set required to make the feature work.
  - Avoid adding optional knobs unless they are clearly justified.
  - Confirm proposed arguments and environment variables with the user before adding them.
- Always include a verification step (tests, build, run, or a repro checklist).
