#!/usr/bin/env python3
"""Collect the facts of a change request from GitHub, into the facts file of the gates.

This is the only script that knows GitHub. Python 3.11 or later, standard library only.

  python3 scripts/charter_facts_github.py --repo owner/name --pr 24 --check quality=success --out facts.json

The token comes from the environment variable GITHUB_TOKEN. The workflow of GitHub sets it.

Exit codes: 0 done, 2 the collection could not run. The message names the cause.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charter_check as cc  # noqa: E402
import charter_gate as cg  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ENV_TOKEN = "GITHUB_TOKEN"
API = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "charter-facts"
PAGE_SIZE = 100
GRAPHQL_THREADS = """
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        nodes { isResolved }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""

# The text of a change request.
ISSUE_REFERENCE = re.compile(r"(?<![\w/])#(\d+)\b")
REASON_LINE = re.compile(r"^No document change:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# Results of a job in a workflow, mapped to the state of a check in the facts file.
JOB_SUCCESS = "success"
CHECK_FAIL = "fail"

# Keys of the API responses that this script reads.
PR_BODY, PR_TITLE, PR_NUMBER = "body", "title", "number"
FILE_NAME = "filename"
ISSUE_STATE, ISSUE_IS_PR = "state", "pull_request"

MSG = {
    "no_token": f"no token: set the environment variable {ENV_TOKEN}",
    "bad_repo": "the repo must be owner/name: {repo}",
    "bad_check": "a check must be name=result: {check}",
    "http": "GitHub answered {code} for {url}: {detail}",
    "network": "GitHub is not reachable: {url}: {error}",
    "graphql": "GitHub answered errors for the review threads: {errors}",
    "written": "facts written: {path} ({files} files, {issues} issues, {threads} unresolved threads)",
}


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


# ---------------------------------------------------------------------------
# Pure functions: from API data to facts. Tested without a network.
# ---------------------------------------------------------------------------


def issue_numbers(text: str) -> list[int]:
    """The issue numbers named in a text, in order, each once."""
    seen: list[int] = []
    for match in ISSUE_REFERENCE.finditer(text or ""):
        number = int(match.group(1))
        if number not in seen:
            seen.append(number)
    return seen


def recorded_reason(text: str) -> str | None:
    match = REASON_LINE.search(text or "")
    return match.group(1) if match else None


def check_state(job_result: str) -> str:
    return cg.CHECK_PASS if job_result == JOB_SUCCESS else CHECK_FAIL


def build_facts(pr: dict, files: list[dict], issues: dict[int, dict], unresolved: int,
                checks: dict[str, str]) -> dict:
    """The facts file, from the API data. Issues that are change requests are left out."""
    linked = [
        {cg.ISSUE_NUMBER: number, cg.ISSUE_STATE: issue[ISSUE_STATE]}
        for number, issue in issues.items()
        if ISSUE_IS_PR not in issue
    ]
    text = f"{pr.get(PR_TITLE) or ''}\n{pr.get(PR_BODY) or ''}"
    return {
        cg.FACT_CHANGE_REQUEST: pr[PR_NUMBER],
        cg.FACT_LINKED_ISSUES: linked,
        cg.FACT_CHANGED_FILES: [f[FILE_NAME] for f in files],
        cg.FACT_REASON: recorded_reason(text),
        cg.FACT_UNRESOLVED_THREADS: unresolved,
        cg.FACT_CHECKS: {name: check_state(result) for name, result in checks.items()},
    }


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------


class GitHub:
    def __init__(self, token: str):
        self.token = token

    def _request(self, url: str, data: dict | None = None) -> object:
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(request) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            raise cc.CannotRun(msg("http", code=e.code, url=url, detail=e.read().decode(errors="replace")[:200]))
        except urllib.error.URLError as e:
            raise cc.CannotRun(msg("network", url=url, error=e.reason))

    def get(self, path: str) -> object:
        return self._request(f"{API}{path}")

    def pages(self, path: str) -> list:
        items: list = []
        page = 1
        while True:
            batch = self.get(f"{path}?per_page={PAGE_SIZE}&page={page}")
            items.extend(batch)
            if len(batch) < PAGE_SIZE:
                return items
            page += 1

    def unresolved_threads(self, owner: str, name: str, number: int) -> int:
        unresolved = 0
        after = None
        while True:
            data = self._request(f"{API}/graphql", {"query": GRAPHQL_THREADS,
                                                    "variables": {"owner": owner, "name": name, "number": number, "after": after}})
            if data.get("errors"):
                raise cc.CannotRun(msg("graphql", errors=data["errors"]))
            threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]
            unresolved += sum(1 for t in threads["nodes"] if not t["isResolved"])
            if not threads["pageInfo"]["hasNextPage"]:
                return unresolved
            after = threads["pageInfo"]["endCursor"]


def collect(repo: str, number: int, checks: dict[str, str], token: str) -> dict:
    owner, name = repo.split("/", 1)
    github = GitHub(token)
    pr = github.get(f"/repos/{repo}/pulls/{number}")
    files = github.pages(f"/repos/{repo}/pulls/{number}/files")
    text = f"{pr.get(PR_TITLE) or ''}\n{pr.get(PR_BODY) or ''}"
    issues = {k: github.get(f"/repos/{repo}/issues/{k}") for k in issue_numbers(text) if k != number}
    unresolved = github.unresolved_threads(owner, name, number)
    return build_facts(pr, files, issues, unresolved, checks)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


def parse_checks(items: list[str]) -> dict[str, str]:
    checks: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise cc.CannotRun(msg("bad_check", check=item))
        name, result = item.split("=", 1)
        checks[name.strip()] = result.strip()
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="charter_facts_github", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--check", action="append", default=[], help="name=result, for each job that ran")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if "/" not in args.repo:
            raise cc.CannotRun(msg("bad_repo", repo=args.repo))
        token = os.environ.get(ENV_TOKEN)
        if not token:
            raise cc.CannotRun(msg("no_token"))
        facts = collect(args.repo, args.pr, parse_checks(args.check), token)
        args.out.write_text(json.dumps(facts, indent=2))
        print(msg("written", path=args.out, files=len(facts[cg.FACT_CHANGED_FILES]),
                  issues=len(facts[cg.FACT_LINKED_ISSUES]), threads=facts[cg.FACT_UNRESOLVED_THREADS]))
        return cc.PASS
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
