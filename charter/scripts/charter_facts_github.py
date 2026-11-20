#!/usr/bin/env python3
"""Collect the facts of a change request from GitHub, into the facts file of the gates.

This is the only script that knows GitHub. Python 3.11 or later, standard library only.

Commands:
  find    --repo owner/name (--pr N | --sha SHA)        Print "number=N" and "sha=SHA" of the change request.
  record  --repo owner/name --pr N --file record.json   Put the evidence record on the change request,
                                                        as one comment that each run updates.
  records --repo owner/name --last N                    Print the records of the last merged change requests.
  collect --repo owner/name --pr N --out facts.json     Write the facts file.
          [--sha SHA]                                   The commit that the facts describe.
          [--check name=result]...                      A check result given by the caller.
          [--check-run name]...                         A check read from the check runs of the head commit.
          [--review-workflow FILE]                      The repo has this reviewer workflow: read the severity line
                                                        of each report of the reviewer on the change request, and
                                                        the commit of the newest.
          [--code-review-workflow FILE]                 The repo has this reviewer of the code: read the severity
                                                        line of each of its reports, and the commit of the newest.

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

CMD_FIND, CMD_COLLECT, CMD_RECORD, CMD_RECORDS = "find", "collect", "record", "records"
ENV_TOKEN = "GITHUB_TOKEN"
API = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "charter-facts"
PAGE_SIZE = 100
RECORD_PAGES = 3   # closed change requests examined for the list of records
HTTP_NOT_FOUND = 404
OUTPUT_NUMBER, OUTPUT_SHA = "number", "sha"

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

# The text of a change request. A link to an issue is a closing keyword of the code host followed by `#N`
# (`Closes #N`, `Fixes #N`, `Resolves #N`; the case does not matter; a colon may follow the keyword), or
# `Part of #N`, which links without closing: the form of a change request of the Plan phase, the intent
# alone (#76). A bare `#N` in the text is a mention, not a link.
LINKED_ISSUE = re.compile(r"\b(?:clos(?:e|es|ed)|fix(?:es|ed)?|resolv(?:e|es|ed)|part of)\s*:?\s+#(\d+)\b", re.IGNORECASE)
REASON_LINE = re.compile(r"^No document change:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
FALSE_FAILURE_LINE = re.compile(r"^False failure:\s*([a-z0-9_-]+)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
DROPPED_FINDING_LINE = re.compile(r"^Dropped finding:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
FALSE_FINDING_LINE = re.compile(r"^False finding:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# The text of an issue: the line that names the intent of the work item, `Intent: intents/<part>.md`, or
# the older form, a heading `## Intent` with the path on the next line. The path keeps its case; a plan
# file at the old place, `intents/<part>.plan.md`, is not an intent.
INTENT_PATH = (re.escape(cg.INTENTS_DIR) + r"[A-Za-z0-9._/-]+(?<!" + re.escape(cg.OLD_PLAN_SUFFIX[:-len(cg.INTENT_SUFFIX)]) + r")"
               + re.escape(cg.INTENT_SUFFIX))
INTENT_LINE = re.compile(r"^(?:[Ii]ntent:|## Intent\s*\n+)\s*`?(" + INTENT_PATH + r")`?\s*$", re.MULTILINE)
ISSUE_BODY = "body"

# A report of the intent reviewer: a comment by the workflow account, with the marker of the skill. Each run
# posts a new comment, so each report stays on the change request.
REVIEW_MARKER = "<!-- charter-intent-review -->"
# A report of the reviewer of the code: the same form, with its own marker, so that the two reviews stay apart.
CODE_REVIEW_MARKER = "<!-- charter-code-review -->"
COMMIT_LINE = re.compile(r"^Commit:\s*([0-9a-fA-F]+)\s*$", re.MULTILINE)
SEVERITY_LINE = re.compile(r"^Highest open severity:\s*(" + "|".join(cg.SEVERITIES) + r")\b", re.IGNORECASE | re.MULTILINE)

# The record comment on a change request.
RECORD_MARKER = "<!-- charter-record -->"
RECORD_TITLE = "## Evidence record"
RECORD_FENCE_OPEN, RECORD_FENCE_CLOSE = "````json", "````"   # four backticks: a reason may contain three
RECORD_AUTHOR = "github-actions[bot]"   # the account that the token of a workflow uses
COMMENT_BODY, COMMENT_ID, COMMENT_USER, USER_LOGIN = "body", "id", "user", "login"
PR_MERGED_AT = "merged_at"

# Results of a job or a check run, mapped to the state of a check in the facts file.
CONCLUSION_SUCCESS = "success"
CHECK_FAIL, CHECK_PENDING = "fail", "pending"

# Keys of the API responses that this script reads.
PR_BODY, PR_TITLE, PR_NUMBER, PR_HEAD, HEAD_SHA = "body", "title", "number", "head", "sha"
PR_STATE, PR_OPEN, PR_BASE, BASE_REF, COMPARE_FILES = "state", "open", "base", "ref", "files"
FILE_NAME, FILE_STATUS, FILE_PREVIOUS = "filename", "status", "previous_filename"
STATUS_REMOVED, STATUS_RENAMED = "removed", "renamed"
ISSUE_STATE, ISSUE_IS_PR = "state", "pull_request"
RUNS, RUN_NAME, RUN_CONCLUSION, RUN_STATUS, RUN_COMPLETED = "check_runs", "name", "conclusion", "status", "completed"

MSG = {
    "no_token": f"no token: set the environment variable {ENV_TOKEN}",
    "bad_repo": "the repo must be owner/name: {repo}",
    "bad_check": "a check must be name=result: {check}",
    "no_pr_for_sha": "no open change request has the head commit {sha}",
    "http": "GitHub answered {code} for {url}: {detail}",
    "network": "GitHub is not reachable: {url}: {error}",
    "graphql": "GitHub answered errors for the review threads: {errors}",
    "record_done": "record {action} on change request {number}",
    "record_line": "#{number}\t{verdict}\ttier {tier}\t{time}\tscripts {scripts}\tfalse failures {false}",
    "written": "facts written: {path} ({files} files, {issues} issues, {threads} unresolved threads, checks {checks})",
}


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


# ---------------------------------------------------------------------------
# Pure functions: from API data to facts. Tested without a network.
# ---------------------------------------------------------------------------


def issue_numbers(text: str) -> list[int]:
    """The issues that a text links with a closing keyword or with `Part of`, in order, each once. A bare `#N`
    is a mention and links nothing: a sentence that names a later issue must not make the verdict demand its plan."""
    seen: list[int] = []
    for match in LINKED_ISSUE.finditer(text or ""):
        number = int(match.group(1))
        if number not in seen:
            seen.append(number)
    return seen


def recorded_reason(text: str) -> str | None:
    match = REASON_LINE.search(text or "")
    return match.group(1) if match else None


def false_failures(text: str) -> list[dict]:
    """The false failures that a person recorded in the text: one line each."""
    return [{cg.JSON_KEY_GATE: gate.lower(), "reason": reason} for gate, reason in FALSE_FAILURE_LINE.findall(text or "")]


def finding_lines(text: str) -> tuple[list[str], list[str]]:
    """The findings that the author dropped, and the findings that the leader marked as false."""
    return DROPPED_FINDING_LINE.findall(text or ""), FALSE_FINDING_LINE.findall(text or "")


def removed_paths(files: list[dict]) -> set[str]:
    """The paths that the change request removes: the files with the status removed, and the previous name of
    the files with the status renamed. An intent among them needs no plan (#71)."""
    gone = {f[FILE_NAME] for f in files if f.get(FILE_STATUS) == STATUS_REMOVED}
    gone |= {f[FILE_PREVIOUS] for f in files if f.get(FILE_STATUS) == STATUS_RENAMED and f.get(FILE_PREVIOUS)}
    return gone


def intent_paths(issues: dict[int, dict | None]) -> list[str]:
    """The intents that the linked issues name, in order, each once."""
    seen: list[str] = []
    for issue in issues.values():
        if issue is None or ISSUE_IS_PR in issue:
            continue
        for path in INTENT_LINE.findall(issue.get(ISSUE_BODY) or ""):
            if path not in seen:
                seen.append(path)
    return seen


def highest_severity(comments: list[dict], author: str) -> str | None:
    """The severity line of the newest report of the reviewer; None before the first report or when the
    newest report has no such line. The API lists the comments oldest first; a reviewer that posts a new
    comment instead of an update must not leave an old severity in force."""
    for comment in reversed(comments):
        body = comment.get(COMMENT_BODY) or ""
        if (comment.get(COMMENT_USER) or {}).get(USER_LOGIN) == author and REVIEW_MARKER in body:
            match = SEVERITY_LINE.search(body)
            return match.group(1).lower() if match else None
    return None


def review_reports(comments: list[dict], author: str, marker: str = REVIEW_MARKER) -> list[str | None]:
    """The severity line of each report with the marker, oldest first, as the API lists the comments. A report
    without the line gives None for its place. A comment of another author is no report."""
    out: list[str | None] = []
    for comment in comments:
        body = comment.get(COMMENT_BODY) or ""
        if (comment.get(COMMENT_USER) or {}).get(USER_LOGIN) == author and marker in body:
            match = SEVERITY_LINE.search(body)
            out.append(match.group(1).lower() if match else None)
    return out


def report_commit(comments: list[dict], author: str, marker: str) -> str | None:
    """The line `Commit:` of the newest report with the marker; None before the first report, or when the
    newest report has no such line."""
    for comment in reversed(comments):
        body = comment.get(COMMENT_BODY) or ""
        if (comment.get(COMMENT_USER) or {}).get(USER_LOGIN) == author and marker in body:
            match = COMMIT_LINE.search(body)
            return match.group(1).lower() if match else None
    return None


def comment_body(record: dict) -> str:
    """The comment that carries the record: a marker, a short table, and the JSON."""
    checks = ", ".join(f"{name} {state}" for name, state in record.get(cg.FACT_CHECKS, {}).items())
    rows = [
        ("Verdict", record.get(cg.JSON_KEY_VERDICT)),
        ("Tier", f"{record.get(cg.JSON_KEY_TIER)}, the {record.get(cg.JSON_KEY_APPROVER)} merges"),
        ("Checks", checks or "none"),
        ("Source", record.get(cg.JSON_KEY_SOURCE)),
        ("Scripts", record.get(cg.RECORD_KEYS[3]) or "unknown"),
        ("Time", record.get(cg.RECORD_KEYS[2])),
    ]
    table = "\n".join(f"| {k} | {v} |" for k, v in rows)
    return (f"{RECORD_MARKER}\n{RECORD_TITLE}\n\n| | |\n|---|---|\n{table}\n\n"
            f"{RECORD_FENCE_OPEN}\n{json.dumps(record, indent=2)}\n{RECORD_FENCE_CLOSE}\n")


def record_from_comment(body: str) -> dict | None:
    """The record inside a comment, or None when the comment is not a record."""
    if not body or RECORD_MARKER not in body or RECORD_FENCE_OPEN not in body:
        return None
    start = body.index(RECORD_FENCE_OPEN) + len(RECORD_FENCE_OPEN)
    end = body.rfind(RECORD_FENCE_CLOSE)
    if end <= start:
        return None
    try:
        return json.loads(body[start:end])
    except json.JSONDecodeError:
        return None


def is_record_comment(comment: dict, author: str) -> bool:
    """Only a comment by the workflow account counts; a person cannot forge or hijack the record."""
    return ((comment.get(COMMENT_USER) or {}).get(USER_LOGIN) == author
            and RECORD_MARKER in (comment.get(COMMENT_BODY) or ""))


def check_state(conclusion: str | None) -> str:
    """The state of a check from a job result or a check-run conclusion."""
    if conclusion == CONCLUSION_SUCCESS:
        return cg.CHECK_PASS
    return CHECK_PENDING if conclusion is None else CHECK_FAIL


def conclusions(runs: list[dict], names: list[str]) -> dict[str, str | None]:
    """The conclusion of the newest completed check run of each name; None when none completed."""
    out: dict[str, str | None] = {name: None for name in names}
    for run in runs:                                   # the API lists the newest first
        name = run.get(RUN_NAME)
        if name in out and out[name] is None and run.get(RUN_STATUS) == RUN_COMPLETED:
            out[name] = run.get(RUN_CONCLUSION)
    return out


def build_facts(pr: dict, files: list[dict], issues: dict[int, dict | None], unresolved: int,
                checks: dict[str, str | None], review: list[str | None] | None = None,
                plans: dict[str, bool] | None = None, removed: set[str] | None = None,
                code_review: list[str | None] | None = None, code_commit: str | None = None,
                head: str | None = None, review_commit: str | None = None) -> dict:
    """The facts file, from the API data. Numbers that are not issues are left out. The review loop
    facts are written only when the caller named a reviewer workflow: `review` holds the severity line of each
    report, oldest first; the round count and the newest severity come from it; `review_commit` is the line
    `Commit:` of the newest report. `plans` says, for each intent that
    a linked issue names, whether its plan exists at the commit; `removed` holds the paths that the change
    request removes or renames away, and an intent among them is marked, so that the gate asks no plan for it.
    The facts of the code review are written only when the caller named the reviewer of the code: `code_review`
    holds the severity line of each of its reports, oldest first, and `code_commit` the commit of the newest.
    `head` is the commit that the facts describe."""
    linked = [
        {cg.ISSUE_NUMBER: number, cg.ISSUE_STATE: issue[ISSUE_STATE]}
        for number, issue in issues.items()
        if issue is not None and ISSUE_IS_PR not in issue
    ]
    text = f"{pr.get(PR_TITLE) or ''}\n{pr.get(PR_BODY) or ''}"
    loop = {} if review is None else {cg.FACT_REVIEW_REPORTS: review, cg.FACT_REVIEW_ROUNDS: len(review),
                                      cg.FACT_REVIEW_SEVERITY: review[-1] if review else None,
                                      cg.FACT_REVIEW_COMMIT: review_commit}
    code = {} if code_review is None else {cg.FACT_CODE_REVIEW_REPORTS: code_review, cg.FACT_CODE_REVIEW_COMMIT: code_commit}
    return {
        cg.FACT_CHANGE_REQUEST: pr[PR_NUMBER],
        cg.FACT_LINKED_ISSUES: linked,
        cg.FACT_CHANGED_FILES: [f[FILE_NAME] for f in files],
        cg.FACT_REASON: recorded_reason(text),
        cg.FACT_UNRESOLVED_THREADS: unresolved,
        cg.FACT_CHECKS: {name: check_state(result) for name, result in checks.items()},
        cg.FACT_FALSE_FAILURES: false_failures(text),
        cg.FACT_DROPPED_FINDINGS: finding_lines(text)[0],
        cg.FACT_FALSE_FINDINGS: finding_lines(text)[1],
        cg.FACT_INTENTS: [{cg.INTENT_PATH: path, cg.INTENT_PLAN: bool(exists), cg.INTENT_REMOVED: path in (removed or set())}
                          for path, exists in (plans or {}).items()],
        cg.FACT_HEAD_COMMIT: head,
        **loop,
        **code,
    }


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------


class GitHub:
    def __init__(self, token: str):
        self.token = token

    def _request(self, url: str, data: dict | None = None, optional: bool = False, method: str | None = None) -> object:
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(url, data=body, method=method, headers={
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
            if optional and e.code == HTTP_NOT_FOUND:
                return None
            raise cc.CannotRun(msg("http", code=e.code, url=url, detail=e.read().decode(errors="replace")[:200]))
        except urllib.error.URLError as e:
            raise cc.CannotRun(msg("network", url=url, error=e.reason))

    def get(self, path: str, optional: bool = False) -> object:
        return self._request(f"{API}{path}", optional=optional)

    def send(self, path: str, data: dict, method: str) -> object:
        return self._request(f"{API}{path}", data=data, method=method)

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


def open_change_request(prs: list[dict]) -> dict | None:
    """The first open change request of a list; a closed one never counts."""
    return next((pr for pr in prs if pr.get(PR_STATE) == PR_OPEN), None)


def find(repo: str, github: GitHub, number: int | None, sha: str | None) -> tuple[int, str]:
    """The number and the head commit of a change request, from its number or its head commit."""
    if number is not None:
        pr = github.get(f"/repos/{repo}/pulls/{number}")
        return pr[PR_NUMBER], pr[PR_HEAD][HEAD_SHA]
    pr = open_change_request(github.get(f"/repos/{repo}/commits/{sha}/pulls"))
    if pr is None:
        raise cc.CannotRun(msg("no_pr_for_sha", sha=sha))
    return pr[PR_NUMBER], sha


def collect(repo: str, number: int, given: dict[str, str], run_names: list[str], github: GitHub,
            sha: str | None = None, review_workflow: str | None = None, author: str = RECORD_AUTHOR,
            code_review_workflow: str | None = None) -> dict:
    """The facts of a change request. With a commit, the files and the check runs are those of that commit,
    so that they agree with the check that is published on it."""
    owner, name = repo.split("/", 1)
    pr = github.get(f"/repos/{repo}/pulls/{number}")
    commit = sha or pr[PR_HEAD][HEAD_SHA]
    if sha and sha != pr[PR_HEAD][HEAD_SHA]:
        files = github.get(f"/repos/{repo}/compare/{pr[PR_BASE][BASE_REF]}...{sha}").get(COMPARE_FILES, [])
    else:
        files = github.pages(f"/repos/{repo}/pulls/{number}/files")
    text = f"{pr.get(PR_TITLE) or ''}\n{pr.get(PR_BODY) or ''}"
    issues = {k: github.get(f"/repos/{repo}/issues/{k}", optional=True) for k in issue_numbers(text) if k != number}
    unresolved = github.unresolved_threads(owner, name, number)
    checks: dict[str, str | None] = dict(given)
    if run_names:
        runs = github.get(f"/repos/{repo}/commits/{commit}/check-runs?per_page={PAGE_SIZE}")
        checks.update(conclusions(runs.get(RUNS, []), run_names))
    review, review_commit, code_review, code_commit = None, None, None, None
    if review_workflow or code_review_workflow:
        comments = github.pages(f"/repos/{repo}/issues/{number}/comments")
        if review_workflow:
            review = review_reports(comments, author)
            review_commit = report_commit(comments, author, REVIEW_MARKER)
        if code_review_workflow:
            code_review = review_reports(comments, author, CODE_REVIEW_MARKER)
            code_commit = report_commit(comments, author, CODE_REVIEW_MARKER)
    # The plan exists at `plans/<part>.md`, or at the old place `intents/<part>.plan.md`.
    plans = {intent: any(github.get(f"/repos/{repo}/contents/{place(intent)}?ref={commit}", optional=True) is not None
                         for place in (cg.plan_of, cg.old_plan_of))
             for intent in intent_paths(issues)}
    return build_facts(pr, files, issues, unresolved, checks, review, plans, removed_paths(files),
                       code_review, code_commit, commit, review_commit)


def put_record(repo: str, number: int, record: dict, github: GitHub, author: str) -> str:
    """Create or update the one record comment of a change request. Returns 'created' or 'updated'."""
    body = comment_body(record)
    for comment in github.pages(f"/repos/{repo}/issues/{number}/comments"):
        if is_record_comment(comment, author):
            github.send(f"/repos/{repo}/issues/comments/{comment[COMMENT_ID]}", {COMMENT_BODY: body}, "PATCH")
            return "updated"
    github.send(f"/repos/{repo}/issues/{number}/comments", {COMMENT_BODY: body}, "POST")
    return "created"


def merged_records(repo: str, last: int, github: GitHub, author: str) -> list[dict]:
    """The records of the last merged change requests, by the time of the merge, newest first."""
    merged: list[dict] = []
    for page in range(1, RECORD_PAGES + 1):
        prs = github.get(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page={PAGE_SIZE}&page={page}")
        merged += [pr for pr in prs if pr.get(PR_MERGED_AT)]
        if len(prs) < PAGE_SIZE:
            break
    merged.sort(key=lambda pr: pr[PR_MERGED_AT], reverse=True)
    out: list[dict] = []
    for pr in merged[:last]:
        for comment in github.pages(f"/repos/{repo}/issues/{pr[PR_NUMBER]}/comments"):
            if is_record_comment(comment, author):
                record = record_from_comment(comment.get(COMMENT_BODY))
                if record:
                    out.append(record)
                break
    return out


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
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser(CMD_FIND)
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--pr", type=int)
    p.add_argument("--sha")
    p = sub.add_parser(CMD_RECORD)
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--file", type=Path, required=True, help="the record, as JSON")
    p.add_argument("--author", default=RECORD_AUTHOR, help="the account whose comments carry the record")
    p = sub.add_parser(CMD_RECORDS)
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--last", type=int, default=10)
    p.add_argument("--author", default=RECORD_AUTHOR, help="the account whose comments carry the record")
    p = sub.add_parser(CMD_COLLECT)
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--check", action="append", default=[], help="name=result, given by the caller")
    p.add_argument("--check-run", action="append", default=[], help="name of a check run to read")
    p.add_argument("--sha", help="the commit that the facts describe; default: the current head")
    p.add_argument("--review-workflow", help="the file name of the reviewer workflow: the repo has a reviewer")
    p.add_argument("--code-review-workflow", help="the file name of the workflow of the reviewer of the code")
    p.add_argument("--author", default=RECORD_AUTHOR, help="the account whose comment carries the review")
    p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if "/" not in args.repo:
            raise cc.CannotRun(msg("bad_repo", repo=args.repo))
        token = os.environ.get(ENV_TOKEN)
        if not token:
            raise cc.CannotRun(msg("no_token"))
        github = GitHub(token)
        if args.command == CMD_FIND:
            if args.pr is None and not args.sha:
                parser.error("find needs --pr or --sha")
            number, sha = find(args.repo, github, args.pr, args.sha)
            print(f"{OUTPUT_NUMBER}={number}\n{OUTPUT_SHA}={sha}")
            return cc.PASS
        if args.command == CMD_RECORD:
            record = json.loads(cc.read_text(args.file))
            print(msg("record_done", action=put_record(args.repo, args.pr, record, github, args.author), number=args.pr))
            return cc.PASS
        if args.command == CMD_RECORDS:
            for record in merged_records(args.repo, args.last, github, args.author):
                print(msg("record_line", number=record.get(cg.FACT_CHANGE_REQUEST), verdict=record.get(cg.JSON_KEY_VERDICT),
                          tier=record.get(cg.JSON_KEY_TIER), time=record.get(cg.RECORD_KEYS[2]),
                          scripts=(record.get(cg.RECORD_KEYS[3]) or "unknown")[:12],
                          false=len(record.get(cg.RECORD_KEYS[4]) or [])))
            return cc.PASS
        facts = collect(args.repo, args.pr, parse_checks(args.check), args.check_run, github, args.sha,
                        args.review_workflow, args.author, args.code_review_workflow)
        args.out.write_text(json.dumps(facts, indent=2))
        print(msg("written", path=args.out, files=len(facts[cg.FACT_CHANGED_FILES]),
                  issues=len(facts[cg.FACT_LINKED_ISSUES]), threads=facts[cg.FACT_UNRESOLVED_THREADS],
                  checks=facts[cg.FACT_CHECKS]))
        return cc.PASS
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
