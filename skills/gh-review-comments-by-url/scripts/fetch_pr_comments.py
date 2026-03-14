#!/usr/bin/env python3
"""
Fetch PR conversation comments, reviews, and review threads for a PR URL.

Usage:
  python3 fetch_pr_comments.py https://github.com/<owner>/<repo>/pull/<number>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse

QUERY = """\
query(
  $owner: String!,
  $repo: String!,
  $number: Int!,
  $commentsCursor: String,
  $reviewsCursor: String,
  $threadsCursor: String
) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      url
      title
      state

      comments(first: 100, after: $commentsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          body
          createdAt
          updatedAt
          author { login }
        }
      }

      reviews(first: 100, after: $reviewsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          state
          body
          submittedAt
          author { login }
        }
      }

      reviewThreads(first: 100, after: $threadsCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          diffSide
          startLine
          startDiffSide
          originalLine
          originalStartLine
          resolvedBy { login }
          comments(first: 100) {
            nodes {
              id
              body
              createdAt
              updatedAt
              author { login }
            }
          }
        }
      }
    }
  }
}
"""


def _run(cmd: list[str], stdin: str | None = None) -> str:
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout


def _run_json(cmd: list[str], stdin: str | None = None) -> dict[str, Any]:
    output = _run(cmd, stdin=stdin)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON output: {exc}") from exc


def _ensure_gh_authenticated() -> None:
    try:
        _run(["gh", "auth", "status"])
    except RuntimeError:
        print("`gh auth status` failed. Run `gh auth login` and retry.", file=sys.stderr)
        raise


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    parsed = urlparse(pr_url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("PR URL must start with http:// or https://.")

    host = parsed.netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise ValueError("PR URL host must be github.com.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 4 or parts[2] != "pull" or not parts[3].isdigit():
        raise ValueError("PR URL must be like https://github.com/<owner>/<repo>/pull/<number>.")

    owner, repo, number = parts[0], parts[1], int(parts[3])
    return owner, repo, number


def gh_api_graphql(
    owner: str,
    repo: str,
    number: int,
    comments_cursor: str | None = None,
    reviews_cursor: str | None = None,
    threads_cursor: str | None = None,
) -> dict[str, Any]:
    cmd = [
        "gh",
        "api",
        "graphql",
        "-F",
        "query=@-",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"number={number}",
    ]
    if comments_cursor:
        cmd += ["-F", f"commentsCursor={comments_cursor}"]
    if reviews_cursor:
        cmd += ["-F", f"reviewsCursor={reviews_cursor}"]
    if threads_cursor:
        cmd += ["-F", f"threadsCursor={threads_cursor}"]

    return _run_json(cmd, stdin=QUERY)


def fetch_all(owner: str, repo: str, number: int) -> dict[str, Any]:
    conversation_comments: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    review_threads: list[dict[str, Any]] = []

    comments_cursor: str | None = None
    reviews_cursor: str | None = None
    threads_cursor: str | None = None
    pr_meta: dict[str, Any] | None = None

    while True:
        payload = gh_api_graphql(
            owner=owner,
            repo=repo,
            number=number,
            comments_cursor=comments_cursor,
            reviews_cursor=reviews_cursor,
            threads_cursor=threads_cursor,
        )
        if payload.get("errors"):
            raise RuntimeError(f"GitHub GraphQL errors: {json.dumps(payload['errors'], indent=2)}")

        pr = payload["data"]["repository"]["pullRequest"]
        if pr is None:
            raise RuntimeError("Pull request was not found or is not accessible.")

        if pr_meta is None:
            pr_meta = {
                "number": pr["number"],
                "url": pr["url"],
                "title": pr["title"],
                "state": pr["state"],
                "owner": owner,
                "repo": repo,
            }

        comments = pr["comments"]
        review_data = pr["reviews"]
        threads = pr["reviewThreads"]

        conversation_comments.extend(comments.get("nodes") or [])
        reviews.extend(review_data.get("nodes") or [])
        review_threads.extend(threads.get("nodes") or [])

        comments_cursor = comments["pageInfo"]["endCursor"] if comments["pageInfo"]["hasNextPage"] else None
        reviews_cursor = review_data["pageInfo"]["endCursor"] if review_data["pageInfo"]["hasNextPage"] else None
        threads_cursor = threads["pageInfo"]["endCursor"] if threads["pageInfo"]["hasNextPage"] else None

        if not (comments_cursor or reviews_cursor or threads_cursor):
            break

    if pr_meta is None:
        raise RuntimeError("Unexpected empty PR metadata response.")

    return {
        "pull_request": pr_meta,
        "conversation_comments": conversation_comments,
        "reviews": reviews,
        "review_threads": review_threads,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub PR comments/reviews/threads by PR URL.")
    parser.add_argument("pr_url", help="GitHub PR URL (https://github.com/<owner>/<repo>/pull/<number>)")
    args = parser.parse_args()

    try:
        owner, repo, number = parse_pr_url(args.pr_url)
        _ensure_gh_authenticated()
        result = fetch_all(owner, repo, number)
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
