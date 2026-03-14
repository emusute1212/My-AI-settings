---
name: gh-review-comments-by-url
description: Address GitHub PR review comments for a provided PR URL. Use only when the user explicitly invokes this skill and provides a pull request URL. Fetch review comments/threads, process them one by one, reply on each review thread using `review_threads[].id` and `addPullRequestReviewThreadReply`, include commit logs for addressed items, and post reasoned skip replies for non-actionable items.
---

# PR Review Comment Handler (URL Input)

## 1) Confirm prerequisites
- Ensure GitHub CLI is authenticated by running `gh auth status`.
- Run `gh` commands with elevated network permissions when sandboxing blocks access.
- If auth fails, ask the user to run `gh auth login` and retry.
- Require a URL in this format: `https://github.com/<owner>/<repo>/pull/<number>`.
- If the user did not provide a PR URL yet, ask for it before running any fetch steps.

## 2) Fetch review data from the PR URL
- Run `python3 scripts/fetch_pr_comments.py "<PR_URL>"`.
- Use the JSON output to enumerate items from `review_threads`, `reviews`, and `conversation_comments`.
- For each thread item, keep `review_threads[].id` as `THREAD_ID` for reply posting.
- Build a numbered list for processing.

## 3) Triage items
- Classify each item as either `actionable` or `skip`.
- Before deciding `actionable`, verify the review request itself against current code, tests, and repository conventions.
- Skip only when clearly justified.
- Common skip reason: already resolved or outdated without required code change.
- Common skip reason: outside the PR scope.
- Common skip reason: factually incorrect request based on code/tests.
- Common skip reason: pure preference that conflicts with established repository conventions.
- When uncertain, ask the user before skipping.

## 4) Address actionable items one by one
- Process sequentially, not in bulk.
- Use a strict per-item loop and do not move to the next item before finishing the current one:
  - Item N analysis
  - Item N implementation (working tree only)
  - Item N user confirmation
  - Item N commit
  - then move to Item N+1
- Before starting each actionable item, record `START_SHA=$(git rev-parse HEAD)`.
- Apply minimal and reversible changes per item in the working tree first (do not commit yet).
- Run targeted verification after each change (tests, lint, or build relevant to affected code).
- Review the patch quality before committing (for example `git diff` and affected file checks).
- Before commit, explicitly confirm all three points with the user for the current item:
  - the PR review comment interpretation is valid
  - the proposed fix approach is valid
  - the actual code changes are valid (show concrete changed files/hunks, not only a plan)
- Do not commit if any of the three points is not yet confirmed.
- If the user requests adjustments, revise the code and re-run verification before asking again.
- Create at least one commit for each actionable item only after explicit user approval.
- After commit for Item N, collect `COMMIT_LOG` and prepare the Item N reply body, but do not post yet.
- Build per-item commit log with `COMMIT_LOG=$(git log --reverse --pretty=format:'- %h %s' "${START_SHA}..HEAD")`.
- If `COMMIT_LOG` is empty, do not post a completion reply yet. Create the missing commit first.
- Record which item number each change addresses.

## 5) Compose per-thread reply body
- Write replies in Japanese by default.
- Use this template for actionable items:
```text
対応しました。ありがとうございます。

変更概要:
- <変更点1>
- <変更点2>

コミットログ:
<COMMIT_LOG>
```
- Use this template for skipped items:
```text
今回は対応を見送ります。
理由: <見送り理由>

コミット: なし（対応見送り）
```

## 6) Post per-thread reply via GraphQL
- Post one reply per processed thread using `THREAD_ID`.
- For actionable items, post only after user-approved commits exist.
- Post all replies only after all related commits have been pushed to remote successfully (`git push`).
- If `git push` has not been completed or failed, do not post completion replies.
- Use this command pattern and record the returned reply URL:
```bash
REPLY_URL=$(gh api graphql \
  -f query='
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
        comment { url }
      }
    }
  ' \
  -F threadId="$THREAD_ID" \
  -F body="$REPLY_BODY" \
  --jq '.data.addPullRequestReviewThreadReply.comment.url')
```
- If posting fails, re-check `gh auth status`, then retry once after re-authentication.

## 7) Report status
- Keep a running `Addressed` list: item number, change summary, `REPLY_URL`, and `COMMIT_LOG`.
- Keep a running `Skipped` list: item number, skip reason, and `REPLY_URL`.
- Ensure status updates are also reported per item in processing order (Item 1 -> Item 2 -> ...).
- End with a final summary covering all numbered items.

## 8) Verification checklist
- Case: multiple actionable items. Confirm each item has its own confirm->commit cycle before moving on.
- Case: pre-commit confirmation content. Confirm it includes issue interpretation, fix approach, and actual code diff summary.
- Case: before `git push`. Confirm no completion reply is posted yet.
- Case: after successful `git push`. Confirm per-thread completion replies are posted.
- Case: actionable item with one commit. Confirm reply body includes `- <short_sha> <subject>`.
- Case: actionable item with multiple commits. Confirm reply body includes all commits in chronological order.
- Case: actionable item before user confirmation. Confirm no commit is created yet.
- Case: actionable item with no commit. Confirm posting is blocked until commit exists.
- Case: skipped item. Confirm reply includes reason and `コミット: なし（対応見送り）`.
- Case: API/auth failure. Confirm `gh auth status` re-check guidance is shown.
