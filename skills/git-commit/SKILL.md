---
name: "git-commit"
description: "Use when the user asks to create git commits, split work into small commits, or improve commit messages."
metadata:
  short-description: "Create small, prefix-based git commits"
---

# Git Commit Skill

Create small, reviewable commits with a single clear purpose. The default rule is `1 commit = 1 intent = 1 prefix`.

## When to use
- The user asks you to commit changes.
- The user asks you to split work into multiple commits.
- The user asks you to write or clean up commit messages.

## Allowed prefixes
- `feat:` add a new feature or capability
- `fix:` correct incorrect behavior or a regression
- `docs:` update documentation or documentation-style comments
- `chore:` change build files, dependencies, tooling, config, or repository maintenance
- `test:` add or update tests without changing production behavior
- `refactor:` improve production code structure without changing behavior

## Core rules
- Always use exactly one allowed prefix per commit.
- Keep commit scope as small as possible.
- Split mixed-purpose work until a single prefix clearly applies.
- If reshaping existing commits is the clearest way to reach that split, use rebase.
- Do not combine unrelated changes just because they touch the same file.
- Do not stage or commit unrelated user changes.
- Prefer multiple small commits over one broad commit.

## Granularity standard
A commit is small enough only if all of the following are true:
- It does one thing.
- It can be described with exactly one allowed prefix.
- Its diff can be summarized in one short sentence.
- It can be reverted independently without losing unrelated work.

If any item above is false, split the changes further.

## Workflow
1. Inspect the working tree with `git status`, `git diff`, and `git diff --cached`.
2. Group changes by intent, not by file count.
3. Choose the prefix for each group.
4. If a group needs more than one prefix, split it again.
5. If existing commits are already present and rebase would split or reorder them more cleanly, use rebase before finalizing the history.
6. Stage only the files or hunks for the current group.
7. Run targeted verification for that group when possible.
8. Commit using `<prefix>: <short imperative summary>`.
9. Repeat until all intended changes are committed.

## Prefix selection rules
- Use `feat:` for a new capability or user-visible enhancement.
- Use `fix:` for bug fixes, regressions, or incorrect behavior.
- Use `docs:` for documentation-only changes.
- Use `chore:` for build, tooling, dependency, config, or maintenance-only changes.
- Use `test:` for test-only updates.
- Use `refactor:` for internal code cleanup with no behavior change.

When production code changes and tests are required to support the same logical feature or fix, keep them in the same `feat:` or `fix:` commit. When tests or docs are independent follow-up work, keep them in separate `test:` or `docs:` commits.

## Commit message format
Use:

```text
<prefix>: <short imperative summary>
```

If the change is too large or nuanced to explain with the short subject alone, keep the first line short and add details on the following lines.

```text
<prefix>: <short imperative summary>

<detail line 1>
<detail line 2>
```

Examples:
- `feat: add retry support to webhook delivery`
- `fix: handle empty response bodies in parser`
- `docs: document local development setup`
- `chore: bump gradle wrapper to 8.10`
- `test: cover timeout handling in api client`
- `refactor: simplify invoice total calculation`

Avoid vague subjects such as:
- `update stuff`
- `misc changes`
- `fix and refactor parser`

When adding detail lines:
- Explain what changed and why.
- Keep the subject line short even when a body is present.
- Use the additional lines only when the subject alone is not enough.

## Pre-commit checks
- Confirm the staged diff matches one intent.
- Confirm the chosen prefix is unambiguous.
- Confirm no unrelated files are staged.
- Confirm verification was run, or state why it was not possible.

## Response expectations
When applying this skill:
- Explain how the changes should be split if the work is non-trivial.
- Present the planned commit subjects before committing when the split is not obvious.
- After each commit, report the commit subject and the verification result.
