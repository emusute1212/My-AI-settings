---
name: "create-skill"
description: "Use when the user asks Codex to create a new skill or update an existing one. This wrapper skill exists only to decide where the skill should live, ensure the produced skill is written in Japanese, and then delegate the actual skill-authoring work to $skill-creator."
---

# Create Skill

## Purpose

Use this skill as a thin wrapper around `$skill-creator`.

Do not re-explain the full skill creation procedure here. For the actual authoring workflow, read and follow `../.system/skill-creator/SKILL.md`.

This wrapper is responsible for only three things:

1. Decide the target skill name and target directory.
2. Decide whether the skill should be created in user scope or project scope.
3. Ensure the generated skill content and UI text are written in Japanese.

## Scope Selection

Support exactly these two destinations:

- User scope: `~/.agents/skills/{skill-name}`
- Project scope: `$PWD/.agents/skills/{skill-name}`

Rules:

- If the user explicitly chooses a scope, use it.
- If the user does not specify a scope, ask before creating or updating anything.
- If the target directory already exists in the chosen scope, treat the request as an update instead of a new skill creation.

## Language Rules

When creating or updating the target skill:

- Write the target skill's `SKILL.md` content in Japanese.
- Write user-facing UI text in `agents/openai.yaml` in Japanese.
- Keep the target skill's slug, folder name, and frontmatter `name` in ASCII hyphen-case.
- If the user provides only a Japanese title, derive a separate ASCII slug.

## Delegation Rules

After the scope and slug are clear, hand off the actual skill-authoring process to `$skill-creator`.

That means:

- Follow `$skill-creator` for structure, resource selection, initialization, editing, regeneration, and validation.
- Do not invent a parallel workflow here.
- Keep this wrapper short and focused on scope choice and Japanese-writing requirements.

## Completion

Before reporting completion, confirm:

- The skill exists in the selected scope.
- The target `SKILL.md` is written in Japanese.
- The target `agents/openai.yaml` is written in Japanese.
- The target skill name remains valid hyphen-case.
- The delegated `$skill-creator` workflow finished successfully.
