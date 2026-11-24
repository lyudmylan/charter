#!/usr/bin/env python3
"""Charter gates. Python 3.11 or later, standard library only. No model call.

A gate checks one change of a repo. The facts of the change request come from one JSON file
that a collecting step writes on the code host. The gates know no code host.

Commands:
  link      --facts F --contract C     The change request links an open issue (`Closes #N`).
  documents --facts F --contract C     A change under a code path changes a necessary document,
                                       or the change request records a reason.
  quality   --contract C [--repo-only]  The quality checks of the contract run and pass. With --repo-only
                                       the repo contract is read alone, without its organization source.
  product   --contract C [--repo-only]  The product test of the contract, checks.product, runs and passes, as
                                       quality does. With no command and a reason for none, it passes and
                                       prints the reason.
  boundary  --contract C --changed F   No path that a run without a person changed is under a pattern of
                                       boundary.no_write. F lists the changed paths: each added, changed,
                                       or deleted path, and both names of a rename. With a NUL character
                                       between the paths (`-z` of git) any name is read; else one path
                                       on each line, and a line in the quotes of git fails.
  verdict   --facts F --contract C     One verdict: ready or not ready, with the reasons.
            [--record FILE] [--scripts-version V]   Also write the evidence record, as JSON.
  tier      --contract C --changed F   The tier of the changed paths in F, and the depth of its review, one on
            [--repo-only]              each line. F is read as for boundary.
  answer    --facts F --contract C     Whether an agent answers the findings of the reviewers on the change
            [--by factory|person]      request of a run now. Prints `start=true` or `start=false`, the reason,
                                       and for a start the issue, the branch, the head commit, the round, and
                                       the threshold, one `name=value` on each line. The factory starts an
                                       answer only when the contract says so, `run.answer_start`.

Options:
  --schema PATH, --source PATH, --cache-dir DIR   As in charter_check.
  --json                                          Print the result as one JSON object.

Exit codes: 0 pass, 1 fail, 2 the check could not run. The message names the cause.
"""

from __future__ import annotations

import argparse
import datetime
import json
import posixpath
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charter_check as cc  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration. Every name, key, and message lives here, once.
# ---------------------------------------------------------------------------

CMD_LINK, CMD_DOCUMENTS, CMD_QUALITY, CMD_VERDICT = "link", "documents", "quality", "verdict"
CMD_PLAN = "plan"      # a part of the verdict, not a command of its own
CMD_PRODUCT = "product"
CMD_BOUNDARY = cc.CMD_BOUNDARY
CMD_TIER = "tier"
CMD_ANSWER = "answer"
ARG_FACTS = "facts"
ARG_CHANGED = "changed"
PARENT_SEGMENT = ".."
NUL = "\0"                 # between the paths of a list that git wrote with `-z`: no quotes, no escapes
GIT_QUOTE = '"'            # git starts a path that holds a special character with it, in a list of lines
ARG_REPO_ONLY = "repo_only"
ARG_BY = "by"   # who starts the answer: the factory, after a report, or a person

# Keys of the facts file.
FACT_CHANGE_REQUEST = "change_request"
FACT_LINKED_ISSUES = "linked_issues"        # [{"number": 22, "state": "open"}]
FACT_CHANGED_FILES = "changed_files"        # ["docs/product.md"]
FACT_REASON = "reason_for_no_document_change"   # text or null
FACT_UNRESOLVED_THREADS = "unresolved_review_threads"   # whole number
FACT_APPROVALS = "approvals"                # ["login"]
FACT_CHECKS = "checks"                      # {"tests": "pass"}
FACT_FALSE_FAILURES = "false_failures"    # optional: [{"gate": "documents", "reason": "..."}], recorded by a person
FACT_DROPPED_FINDINGS = "dropped_findings"   # optional: ["reason"], the findings of the reviewer that the author dropped
FACT_FALSE_FINDINGS = "false_findings"       # optional: ["reason"], the findings of the reviewer that the leader marked as false
FACT_REVIEW_ROUNDS = "review_rounds"         # optional: whole number, the number of the reports of the reviewer; an older collector counted its runs
FACT_REVIEW_REPORTS = "review_reports"       # optional: [severity or null], the severity line of each report, oldest first
FACT_REVIEW_SEVERITY = "review_highest_severity"   # optional: the last reported severity, or null before the first report
FACT_INTENTS = "intents"                     # optional: [{"path": "intents/x.md", "plan": true, "removed": false}], from the linked issues
FACT_CODE_REVIEW_REPORTS = "code_review_reports"   # optional: [severity or null], each report of the reviewer of the code, oldest first
FACT_CODE_REVIEW_COMMIT = "code_review_commit"     # optional: the line `Commit:` of the newest report of the code review, or null
FACT_HEAD_COMMIT = "head_commit"                   # optional: the commit that the facts describe
FACT_REVIEW_COMMIT = "review_commit"               # optional: the line `Commit:` of the newest report of the intent reviewer, or null
FACT_RUN = "run"                                   # optional: {"commit": "...", "turns": n or null, "duration_seconds": n or null, "cost_usd": n or null}
# FACT_APPROVALS is optional and not checked in this version: the merge by the approver is the approval.
ISSUE_NUMBER, ISSUE_STATE = "number", "state"
INTENT_PATH, INTENT_PLAN, INTENT_REMOVED = "path", "plan", "removed"   # removed: the change request removes or renames the intent away
STATE_OPEN = "open"
CHECK_PASS = "pass"
CHECK_PRODUCT = "product"                   # the check of the job `product` of the workflow `tests`

# The plan of a work item: `plans/<part>.md` for the intent `intents/<part>.md`, accepted before the code.
FIELD_PLAN_BEFORE_CODE = "build.plan_before_code"
INTENTS_DIR, PLANS_DIR = cc.INTENTS_DIR, cc.PLANS_DIR
INTENT_SUFFIX, OLD_PLAN_SUFFIX = cc.INTENT_SUFFIX, cc.OLD_PLAN_SUFFIX

# The review loop. A finding at the threshold or above keeps the loop open; the loop ends below it,
# or when the rounds reach the limit. Then a person decides. Shadow mode: the loop blocks nothing yet.
# A round is a report in the current loop. A loop starts with the first report, and again with the first
# report after one whose severity is below the threshold. A report without a severity line counts as open.
SEVERITIES = ("none", "low", "medium", "high", "blocker")   # from the lowest
FIELD_REVIEW_LOOP = "limits.review_loop"
FIELD_REVIEW_THRESHOLD = "review.threshold"
DEFAULT_REVIEW_THRESHOLD = "medium"

# The reviewer of the code. It reviews a change of a file outside intents/ and plans/. Without the flag, or with
# false, it is in its shadow period: the verdict prints its state and blocks nothing.
FIELD_CODE_BLOCKS = "review.code_blocks"
# The answer to the findings of the reviewers on the change request of a run. The factory starts it only when
# the contract says so; without a value a person starts each answer.
FIELD_ANSWER_START = "run.answer_start"
ANSWER_BY_FACTORY, ANSWER_BY_PERSON = "factory", "person"
# A dropped finding of an agent of a run starts with these words, after `Dropped finding:`. The script that
# writes the text of the change request puts them there, so a person tells such a line from the line of a
# person, and the verdict merges no change request that holds one.
AGENT_DROP = "by the agent of a run: "
FACT_ANSWERED = "answered_commits"   # optional: [commit], the head commits that an answer of an agent already handled
# Facts on the branch of the change request, for the answer of an agent: all optional.
FACT_HEAD_BRANCH, FACT_STATE, FACT_FROM_FORK = "head_branch", "state", "from_fork"
# The branch of a run, `run/<number of the issue>`, and the lines that the command `answer` prints.
RUN_BRANCH_FORM = "run/{number}"
RUN_BRANCH = re.compile(r"^run/([1-9][0-9]*)$")
OUT_START, OUT_REASON, OUT_ISSUE, OUT_BRANCH, OUT_COMMIT, OUT_ROUND, OUT_THRESHOLD = (
    "start", "reason", "issue", "branch", "commit", "round", "threshold")

# The merge by the verdict. Only a tier whose approver is this role is merged by the verdict; a person merges
# every other tier, and also this one when a condition of the merge does not hold or a fact is missing.
APPROVER_AGENT = "agent"

# The record of an agent run. The publishing step of the workflow `run` writes a block at the end of the text of
# the change request: the marker line, then one line `Run:` with the four values `name=value`. A value that
# Claude Code did not report is `none`. The collector reads the block into the fact `run`. The outcome is
# information only: it changes no readiness and no merge.
RUN_MARKER = "<!-- charter-run -->"
RUN_LINE = "Run:"
RUN_COMMIT, RUN_TURNS, RUN_DURATION, RUN_COST = "commit", "turns", "duration_seconds", "cost_usd"
RUN_NUMBERS = (RUN_TURNS, RUN_DURATION, RUN_COST)
RUN_COUNT = "agent_runs"   # in the fact `run` with more than one block: the number of the blocks; the three numbers are their sums
RUN_NONE = "none"
RUN_SUCCESS, RUN_FLAWED, RUN_MANUAL = "success", "flawed", "manual"
RUN_OUTCOME = "outcome"

# Fields of the contract that the gates read.
FIELD_CODE_PATHS = "documents.code_paths"
FIELD_NECESSARY = "documents.necessary"
FIELD_QUALITY = "checks.quality"
FIELD_PRODUCT = cc.FIELD_PRODUCT
FIELD_NO_PRODUCT_REASON = cc.FIELD_NO_PRODUCT_REASON
FIELD_ROLE = "roles.{role}"
TIERS_PREFIX = "tiers."
TIER_PATHS, TIER_APPROVER, TIER_REVIEW = "paths", "approver", "review"

# A quality command runs without a shell. Unquoted operators would need one.
SHELL_OPERATOR_CHARS = "();<>|&"
OUTPUT_TAIL_LINES = 20

# Output.
VERDICT_READY, VERDICT_NOT_READY = "ready", "not ready"
OUT_GATE_PASS, OUT_GATE_FAIL = cc.OUT_PASS, cc.OUT_FAIL
JSON_KEY_GATE, JSON_KEY_RESULT, JSON_KEY_REASONS, JSON_KEY_VERDICT = "gate", "result", "reasons", "verdict"
JSON_KEY_TIER, JSON_KEY_APPROVER, JSON_KEY_MERGES, JSON_KEY_GATES, JSON_KEY_SOURCE = "tier", "approver", "merges", "gates", cc.OUT_SOURCE
ARG_RECORD, ARG_SCRIPTS_VERSION = "record", "scripts_version"

# The evidence record: the verdict, plus these fields.
RECORD_FORM = 1
CODE_REVIEW_ROUND, CODE_REVIEW_SEVERITY = "code_review_round", "code_review_highest_severity"   # the round of the current loop
RECORD_MERGE_BY_VERDICT = "merge_by_verdict"   # true when the verdict merges the change request, else a person merges
RECORD_KEYS = ("record_form", "change_request", "time", "scripts_version", "false_failures", "dropped_findings", "false_findings",
               FACT_REVIEW_ROUNDS, FACT_REVIEW_SEVERITY, FACT_INTENTS, FACT_REVIEW_REPORTS, "review_round",
               FACT_CODE_REVIEW_REPORTS, CODE_REVIEW_ROUND, CODE_REVIEW_SEVERITY, RECORD_MERGE_BY_VERDICT, FACT_RUN)
RECORD_REVIEW_ROUND = RECORD_KEYS[11]        # the round of the current loop; `review_rounds` is the number of all reports

MSG = {
    "facts_not_json": "not JSON: {path}, {error}",
    "facts_not_object": "the facts file is not a JSON object: {path}",
    "facts_bad_value": "the facts file has a wrong value for {key}: {path}",
    "facts_missing_key": "the facts file has no key {key}: {path}",
    "no_linked_issue": "the change request links no issue (a closing keyword and the number: `Closes #N`)",
    "no_open_issue": "the change request links no open issue: {issues}",
    "link_ok": "the change request links the open issue {issues}",
    "no_code_paths": "the contract declares no code paths, so this gate checks nothing",
    "no_code_change": "no file under a code path changed",
    "document_changed": "a necessary document changed: {documents}",
    "reason_recorded": "no document changed; the recorded reason: {reason}",
    "no_document_no_reason": "a file under a code path changed ({files}), but no necessary document changed and no reason is recorded",
    "quality_none": "the contract declares no quality checks",
    "quality_ok": "passed: {command}",
    "quality_failed": "failed with exit code {code}: {command}\n{output}",
    "quality_shell": "shell syntax is not supported, put the command in a script: {command}",
    "quality_cannot_run": "cannot run: {command}: {error}",
    "product_reason": "no product test, the contract says: {reason}",
    "product_passed": "product test: passed: {commands}",
    "product_not_passed": "product test: not passed",
    "product_line_none": "product test: none, the contract says: {reason}",
    "product_not_reported": "product test: not reported",
    "product_not_named": "product test: none, the contract names no product test",
    "checks_pending": "checks not passed: {names}",
    "checks_ok": "all checks passed: {names}",
    "no_checks": "no checks reported",
    "threads_open": "{count} unresolved review threads",
    "threads_ok": "no unresolved review thread",
    "tier": "tier {tier}: review {review}, the {approver} merges ({who})",
    "no_tier": "no tier matches the changed files",
    "approvals_not_checked": "approvals are not checked in this version: the merge by the {approver} is the approval",
    "review_none": "review loop: no review yet",
    "review_round": "round {rounds} of {limit}",
    "review_round_no_limit": "round {rounds}, no limit in the contract",
    "review_no_line": "review loop: {where}, no severity line in the report",
    "review_open": "review loop: {where}, highest open severity {severity}: a finding at {threshold} or above keeps the loop open, the author answers",
    "review_limit": "review loop: {where}, highest open severity {severity}: the limit is reached, a person decides",
    "review_closed": "review loop: {where}, highest open severity {severity}: the loop is closed",
    "code_review_not_needed": "code review: not needed, no file outside {intents} and {plans} changed",
    "code_review_no_facts": "code review: the facts hold no code review, the collecting step names no reviewer of the code",
    "code_review_none": "code review: no review yet",
    "code_review_no_line": "code review: {where}, no severity line in the report",
    "code_review_open": "code review: {where}, highest open severity {severity}: a finding at {threshold} or above keeps the loop open, the author answers",
    "code_review_limit": "code review: {where}, highest open severity {severity}: the limit is reached, a person decides",
    "code_review_closed": "code review: {where}, highest open severity {severity}: the loop is closed",
    "code_review_stale": "{line}; the newest report names the commit {commit}, not the head commit {head}: a push after the last report is not reviewed yet",
    "code_review_shadow": "{line} (shadow period: {field} is not true, so the code review blocks nothing)",
    "merge_verdict": "merge: the verdict merges: the approver of the tier is {approver}, and the reviews by agents closed on the head commit {head}",
    "merge_person": "merge: a person merges: {reason}",
    "merge_not_ready": "the verdict is not ready",
    "merge_approver": "the approver of the tier is {approver}, not {agent}",
    "merge_shadow": "{field} is not true, so the code review is in its shadow period",
    "merge_no_head": "the facts name no head commit",
    "merge_intent": "a file under {intents} changed, and a person approves an intent",
    "merge_code_review": "the newest report of the code review is missing, is not closed, or names another commit than the head commit",
    "merge_plan_none": "a file under {plans} changed, and the facts hold no report of the intent reviewer",
    "merge_plan_no_line": "a file under {plans} changed, and the newest report of the intent reviewer has no severity line",
    "merge_plan_open": "a file under {plans} changed, and the newest report of the intent reviewer is open at {severity}, at {threshold} or above",
    "merge_plan_commit": "a file under {plans} changed, and the newest report of the intent reviewer names the commit {commit}, not the head commit {head}",
    "run": "run: {outcome}, {turns} turns, {duration}, cost {cost} (an estimate of Claude Code)",
    "run_many": "run: {outcome}, {count} runs of an agent, {turns} turns, {duration}, cost {cost} (an estimate of Claude Code)",
    "answer_not_factory": "no answer: the contract says that a person starts an answer ({field} is {value})",
    "answer_no_run": "no answer: no agent run built this change request",
    "answer_no_head": "no answer: the facts name no head commit",
    "answer_wait": "no answer yet: the newest report of {reviewer} is not for the head commit {head}",
    "answer_closed": "no answer: no reviewer has an open finding at {threshold} or above",
    "answer_limit": "no answer: {reviewer} is at round {rounds} of {limit}: a person decides",
    "answer_done": "no answer: an agent answered the reports for the head commit {head} already",
    "answer_start": "answer: round {rounds} of {limit}, open at {threshold} or above: {reviewers}",
    "answer_start_no_limit": "answer: round {rounds}, no limit in the contract, open at {threshold} or above: {reviewers}",
    "answer_no_limit": "no answer: the contract holds no limit of rounds, {field}, so only a person starts an answer",
    "merge_agent_drop": "an agent of a run dropped a finding, and a person reads the reason",
    "answer_not_open": "no answer: the change request is not open, its state is {state}",
    "answer_fork": "no answer: the change request is not known to come from a branch of this repo",
    "answer_no_branch": "no answer: the branch {branch} is not the branch of a run, {form}",
    "answer_no_issue": "no answer: the change request does not link the open issue {number} of its branch",
    "reviewer_intents": "the reviewer of intents",
    "reviewer_code": "the reviewer of the code",
    "run_none": "run: none, no agent run built this change request",
    "run_seconds": "{value:.0f} s",
    "run_dollars": "{value:.2f} USD",
    "plan_intents_only": "not needed, the change is the Plan phase (only files under {dir})",
    "plan_no_intent": "no linked issue names an intent (a line `Intent: {dir}<part>{suffix}` in the issue)",
    "plan_missing": "`{plan}` is missing. A plan at the old place, `{old}`, counts too.",
    "plan_ok": "{plan} exists",
    "plan_removed": "{intent} is removed by the change request, no plan needed",
    "boundary_closed": "{path}: a run without a person cannot change this path, a pattern of {field}. "
                       "A person makes this change, in its own change request.",
    "boundary_outside": "{path}: the path leaves the repo",
    "boundary_quoted": "{line}: git wrote this path in quotes, and the gate cannot read it. Write the list with "
                       "a NUL character between the paths: the option `-z` of git.",
    "boundary_ok": "no changed path is under a pattern of {field} ({count} paths)",
}


class GateFailure(Exception):
    """A gate found a fault in the change."""


@dataclass
class GateResult:
    gate: str
    passed: bool
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {JSON_KEY_GATE: self.gate, JSON_KEY_RESULT: OUT_GATE_PASS if self.passed else OUT_GATE_FAIL,
                JSON_KEY_REASONS: self.reasons}


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _is_issue(value: object) -> bool:
    return (isinstance(value, dict) and isinstance(value.get(ISSUE_NUMBER), int)
            and isinstance(value.get(ISSUE_STATE), str))


FACT_SHAPES = {
    FACT_CHANGE_REQUEST: lambda v: isinstance(v, int),
    FACT_LINKED_ISSUES: lambda v: isinstance(v, list) and all(_is_issue(i) for i in v),
    FACT_CHANGED_FILES: lambda v: isinstance(v, list) and all(isinstance(f, str) for f in v),
    FACT_REASON: lambda v: v is None or isinstance(v, str),
    FACT_UNRESOLVED_THREADS: lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0,
    FACT_CHECKS: lambda v: isinstance(v, dict) and all(isinstance(k, str) and isinstance(s, str) for k, s in v.items()),
}


def _is_false_failure(value: object) -> bool:
    return isinstance(value, dict) and isinstance(value.get(JSON_KEY_GATE), str) and isinstance(value.get("reason"), str)


def load_facts(path: Path) -> dict:
    text = cc.read_text(path)
    try:
        facts = json.loads(text)
    except json.JSONDecodeError as e:
        raise cc.CannotRun(msg("facts_not_json", path=path, error=e))
    if not isinstance(facts, dict):
        raise cc.CannotRun(msg("facts_not_object", path=path))
    for key, fits in FACT_SHAPES.items():
        if key not in facts:
            raise cc.CannotRun(msg("facts_missing_key", key=key, path=path))
        if not fits(facts[key]):
            raise cc.CannotRun(msg("facts_bad_value", key=key, path=path))
    optional = facts.get(FACT_FALSE_FAILURES, [])
    if not (isinstance(optional, list) and all(_is_false_failure(f) for f in optional)):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_FALSE_FAILURES, path=path))
    for key in (FACT_DROPPED_FINDINGS, FACT_FALSE_FINDINGS):
        value = facts.get(key, [])
        if not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
            raise cc.CannotRun(msg("facts_bad_value", key=key, path=path))
    rounds = facts.get(FACT_REVIEW_ROUNDS, 0)
    if not (isinstance(rounds, int) and not isinstance(rounds, bool) and rounds >= 0):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_REVIEW_ROUNDS, path=path))
    if facts.get(FACT_REVIEW_SEVERITY) not in (None, *SEVERITIES):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_REVIEW_SEVERITY, path=path))
    reports = facts.get(FACT_REVIEW_REPORTS, [])
    if not (isinstance(reports, list) and all(r in (None, *SEVERITIES) for r in reports)):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_REVIEW_REPORTS, path=path))
    intents = facts.get(FACT_INTENTS, [])
    if not (isinstance(intents, list) and all(_is_intent(i) for i in intents)):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_INTENTS, path=path))
    code_reports = facts.get(FACT_CODE_REVIEW_REPORTS, [])
    if not (isinstance(code_reports, list) and all(r in (None, *SEVERITIES) for r in code_reports)):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_CODE_REVIEW_REPORTS, path=path))
    for key in (FACT_CODE_REVIEW_COMMIT, FACT_HEAD_COMMIT, FACT_REVIEW_COMMIT):
        if not (facts.get(key) is None or isinstance(facts.get(key), str)):
            raise cc.CannotRun(msg("facts_bad_value", key=key, path=path))
    if FACT_RUN in facts and not _is_run(facts[FACT_RUN]):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_RUN, path=path))
    answered = facts.get(FACT_ANSWERED, [])
    if not (isinstance(answered, list) and all(isinstance(c, str) for c in answered)):
        raise cc.CannotRun(msg("facts_bad_value", key=FACT_ANSWERED, path=path))
    return facts


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_run(value: object) -> bool:
    """The fact `run`: a table with the commit as text and the three numbers, each a number or null, and
    optionally the number of the runs of an agent that the numbers sum."""
    return (isinstance(value, dict) and isinstance(value.get(RUN_COMMIT), str) and bool(value.get(RUN_COMMIT))
            and all(key in value and (value[key] is None or _is_number(value[key])) for key in RUN_NUMBERS)
            and (RUN_COUNT not in value or (_is_number(value[RUN_COUNT]) and value[RUN_COUNT] >= 1)))


def _is_intent(value: object) -> bool:
    return (isinstance(value, dict) and isinstance(value.get(INTENT_PATH), str)
            and isinstance(value.get(INTENT_PLAN), bool) and isinstance(value.get(INTENT_REMOVED, False), bool))


def plan_of(intent: str) -> str:
    """The plan of an intent: `plans/<part>.md` for `intents/<part>.md`, also for a part with folders in it."""
    part = intent[len(INTENTS_DIR):] if intent.startswith(INTENTS_DIR) else intent
    return PLANS_DIR + (part if part.endswith(INTENT_SUFFIX) else part + INTENT_SUFFIX)


def old_plan_of(intent: str) -> str:
    """The old place of the plan of an intent: `intents/<part>.plan.md` next to `intents/<part>.md`."""
    stem = intent[:-len(INTENT_SUFFIX)] if intent.endswith(INTENT_SUFFIX) else intent
    return stem + OLD_PLAN_SUFFIX


def effective(args) -> cc.Effective:
    e = cc.effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if e.failures:
        raise cc.CannotRun("; ".join(e.failures))
    return e


# ---------------------------------------------------------------------------
# The gates
# ---------------------------------------------------------------------------


def gate_link(facts: dict) -> GateResult:
    issues = facts[FACT_LINKED_ISSUES]
    if not issues:
        return GateResult(CMD_LINK, False, [msg("no_linked_issue")])
    open_issues = [i[ISSUE_NUMBER] for i in issues if i.get(ISSUE_STATE) == STATE_OPEN]
    if not open_issues:
        return GateResult(CMD_LINK, False, [msg("no_open_issue", issues=[i[ISSUE_NUMBER] for i in issues])])
    return GateResult(CMD_LINK, True, [msg("link_ok", issues=open_issues)])


def changed_paths(text: str) -> tuple[list[str], bool]:
    """The paths of a list, and whether it is a list of lines. A list with a NUL character holds each
    name as it is. A list of lines is read without the blanks around a line."""
    if NUL in text:
        return [path for path in text.split(NUL) if path], False
    return [line.strip() for line in text.splitlines() if line.strip()], True


def gate_boundary(changed: list[str], e: cc.Effective, lines: bool = True) -> GateResult:
    """The paths that a run changed, against boundary.no_write. A path is read without its dot segments.
    In a list of lines, a line in the quotes of git fails: its path cannot be read."""
    closed = e.values.get(cc.FIELD_NO_WRITE, []) or []
    reasons: list[str] = []
    for line in changed:
        path = posixpath.normpath(line)
        if lines and line.startswith(GIT_QUOTE):
            reasons.append(msg("boundary_quoted", line=line))
        elif line.startswith(cc.SEGMENT_SEPARATOR) or path == PARENT_SEGMENT or path.startswith(PARENT_SEGMENT + cc.SEGMENT_SEPARATOR):
            reasons.append(msg("boundary_outside", path=line))
        elif cc.matches(path, closed):
            reasons.append(msg("boundary_closed", path=path, field=cc.FIELD_NO_WRITE))
    if reasons:
        return GateResult(CMD_BOUNDARY, False, reasons)
    return GateResult(CMD_BOUNDARY, True, [msg("boundary_ok", field=cc.FIELD_NO_WRITE, count=len(changed))])


def gate_documents(facts: dict, e: cc.Effective) -> GateResult:
    code_paths = e.values.get(FIELD_CODE_PATHS, [])
    necessary = e.values.get(FIELD_NECESSARY, [])
    changed = facts[FACT_CHANGED_FILES]
    if not code_paths:
        return GateResult(CMD_DOCUMENTS, True, [msg("no_code_paths")])
    code_changes = [f for f in changed if cc.matches(f, code_paths)]
    if not code_changes:
        return GateResult(CMD_DOCUMENTS, True, [msg("no_code_change")])
    documents = [f for f in changed if f in necessary]
    if documents:
        return GateResult(CMD_DOCUMENTS, True, [msg("document_changed", documents=documents)])
    reason = facts[FACT_REASON]
    if isinstance(reason, str) and reason.strip():
        return GateResult(CMD_DOCUMENTS, True, [msg("reason_recorded", reason=reason.strip())])
    return GateResult(CMD_DOCUMENTS, False, [msg("no_document_no_reason", files=code_changes)])


def needs_a_shell(command: str) -> bool:
    """True when the command has an unquoted shell operator, a variable, or a substitution."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return True
    return any(all(ch in SHELL_OPERATOR_CHARS for ch in tok) or tok.startswith("$") or "`" in tok
               for tok in tokens if tok)


def gate_quality(e: cc.Effective, cwd: Path, field: str = FIELD_QUALITY, gate: str = CMD_QUALITY) -> GateResult:
    """The commands of one field of the contract run without a shell, and each exits with 0."""
    commands = e.values.get(field, [])
    if not commands:
        return GateResult(gate, False, [msg("quality_none")])
    reasons: list[str] = []
    passed = True
    for command in commands:
        if needs_a_shell(command):
            reasons.append(msg("quality_shell", command=command))
            passed = False
            continue
        try:
            result = subprocess.run(shlex.split(command), cwd=cwd, capture_output=True, text=True, check=False)
        except (FileNotFoundError, PermissionError) as error:
            reasons.append(msg("quality_cannot_run", command=command, error=error))
            passed = False
            continue
        if result.returncode == 0:
            reasons.append(msg("quality_ok", command=command))
        else:
            tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-OUTPUT_TAIL_LINES:])
            reasons.append(msg("quality_failed", command=command, code=result.returncode, output=tail))
            passed = False
    return GateResult(gate, passed, reasons)


def gate_product(e: cc.Effective, cwd: Path) -> GateResult:
    """The commands of checks.product run as the quality commands do. With no command, a reason for none
    passes and is printed; with neither, the gate fails with the message of the checker."""
    if not e.values.get(FIELD_PRODUCT):
        reason = cc.product_reason(e)
        if reason:
            return GateResult(CMD_PRODUCT, True, [msg("product_reason", reason=reason)])
        return GateResult(CMD_PRODUCT, False, [cc.msg("product_none", product=FIELD_PRODUCT, reason=FIELD_NO_PRODUCT_REASON)])
    return gate_quality(e, cwd, FIELD_PRODUCT, CMD_PRODUCT)


def product_line(facts: dict, e: cc.Effective) -> tuple[str, bool]:
    """One line on the product test, for the verdict, and whether it blocks. A check `product` that did not
    pass makes the verdict not ready through the rule for checks. The line itself blocks in one case: the
    contract names commands, and the facts hold no check `product`, so nothing ran the product test."""
    commands = e.values.get(FIELD_PRODUCT) or []
    state = facts[FACT_CHECKS].get(CHECK_PRODUCT)
    if commands:
        if state is None:
            return msg("product_not_reported"), True
        if state == CHECK_PASS:
            return msg("product_passed", commands=commands), False
        return msg("product_not_passed"), False
    reason = cc.product_reason(e)
    if reason:
        return msg("product_line_none", reason=reason), False
    return msg("product_not_named"), False


def tiers_in_order(e: cc.Effective) -> dict[str, dict]:
    """The tiers, in the declaration order of the repo contract, with the inherited values."""
    order: list[str] = []
    for path in e.repo_values:
        if path.startswith(TIERS_PREFIX):
            name = path.split(cc.PATH_SEPARATOR)[1]
            if name not in order:
                order.append(name)
    tiers: dict[str, dict] = {name: {} for name in order}
    for path, value in e.values.items():
        if path.startswith(TIERS_PREFIX):
            _, name, key = path.split(cc.PATH_SEPARATOR, 2)
            if name in tiers:
                tiers[name][key] = value
    return tiers


def tier_of(changed: list[str], e: cc.Effective) -> tuple[str | None, dict]:
    """The tier of the change: the first tier of the repo contract that matches any changed file."""
    for name, spec in tiers_in_order(e).items():
        if any(cc.matches(f, spec.get(TIER_PATHS, [])) for f in changed):
            return name, spec
    return None, {}


def current_round(reports: list[str | None], threshold: str) -> int:
    """The round of the current loop: the number of the reports after the last report, before the newest one,
    whose severity is below the threshold. A report without a severity line counts as open."""
    start = 0
    for i, severity in enumerate(reports[:-1]):
        if severity is not None and SEVERITIES.index(severity) < SEVERITIES.index(threshold):
            start = i + 1
    return len(reports) - start


def review_round(facts: dict, e: cc.Effective) -> int:
    """The round from the reports, or, in a facts file of an older collector, the count `review_rounds`."""
    if FACT_REVIEW_REPORTS not in facts:
        return facts.get(FACT_REVIEW_ROUNDS, 0)
    return current_round(facts[FACT_REVIEW_REPORTS], e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD))


def review_loop_state(facts: dict, e: cc.Effective) -> str:
    """One line on the author-reviewer loop. It blocks nothing in this version: shadow mode."""
    rounds = review_round(facts, e)
    severity = facts.get(FACT_REVIEW_SEVERITY)
    if not rounds:
        return msg("review_none")
    limit = e.values.get(FIELD_REVIEW_LOOP)
    where = msg("review_round", rounds=rounds, limit=limit) if limit is not None else msg("review_round_no_limit", rounds=rounds)
    if severity is None:
        return msg("review_no_line", where=where)
    threshold = e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)
    values = dict(where=where, severity=severity, threshold=threshold)
    if SEVERITIES.index(severity) < SEVERITIES.index(threshold):
        return msg("review_closed", **values)
    if limit is not None and rounds >= limit:
        return msg("review_limit", **values)
    return msg("review_open", **values)


def answer_state(facts: dict, e: cc.Effective, by_person: bool) -> tuple[bool, str, int]:
    """Whether an agent answers the findings of the reviewers on the change request of a run now, the reason,
    and the round of the answer. A reviewer takes part when the change request changes a file that it reviews.
    Each reviewer that takes part has its newest report on the head commit; else the answer waits. An answer
    starts when a report is open at the threshold or has no severity line, no open loop is at the limit of
    the contract, and no answer handled this head commit before. The factory starts an answer only when the
    contract says so, and only under a limit of rounds: without one nothing ends the loop. A person can start
    an answer in each of these cases, also a second one for the same commit."""
    start = e.values.get(FIELD_ANSWER_START, ANSWER_BY_PERSON)
    if not by_person and start != ANSWER_BY_FACTORY:
        return False, msg("answer_not_factory", field=FIELD_ANSWER_START, value=start), 0
    if facts.get(FACT_RUN) is None:
        return False, msg("answer_no_run"), 0
    head = facts.get(FACT_HEAD_COMMIT)
    if not head:
        return False, msg("answer_no_head"), 0
    threshold = e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)
    limit = e.values.get(FIELD_REVIEW_LOOP)
    changed = facts[FACT_CHANGED_FILES]
    reviewers = []
    if any(not is_code(f) for f in changed):
        reviewers.append((msg("reviewer_intents"), FACT_REVIEW_REPORTS, FACT_REVIEW_COMMIT))
    if any(is_code(f) for f in changed):
        reviewers.append((msg("reviewer_code"), FACT_CODE_REVIEW_REPORTS, FACT_CODE_REVIEW_COMMIT))
    if limit is None and not by_person:
        return False, msg("answer_no_limit", field=FIELD_REVIEW_LOOP), 0
    open_loops: list[tuple[str, int]] = []
    for name, reports_key, commit_key in reviewers:
        reports = facts.get(reports_key) or []
        if not reports or (facts.get(commit_key) or "").lower() != head.lower():
            return False, msg("answer_wait", reviewer=name, head=head), 0
        if reports[-1] is None or SEVERITIES.index(reports[-1]) >= SEVERITIES.index(threshold):
            open_loops.append((name, current_round(reports, threshold)))
    if not open_loops:
        return False, msg("answer_closed", threshold=threshold), 0
    for name, rounds in open_loops:
        if limit is not None and rounds >= limit:
            return False, msg("answer_limit", reviewer=name, rounds=rounds, limit=limit), 0
    if not by_person and head.lower() in [str(c).lower() for c in facts.get(FACT_ANSWERED) or []]:
        return False, msg("answer_done", head=head), 0
    rounds = max(r for _, r in open_loops)
    names = ", ".join(name for name, _ in open_loops)
    if limit is None:
        return True, msg("answer_start_no_limit", rounds=rounds, threshold=threshold, reviewers=names), rounds
    return True, msg("answer_start", rounds=rounds, limit=limit, threshold=threshold, reviewers=names), rounds


def is_code(path: str) -> bool:
    """A changed path that the reviewer of the code reviews: a path outside intents/ and plans/."""
    return not (path.startswith(INTENTS_DIR) or path.startswith(PLANS_DIR))


def code_review_round(facts: dict, e: cc.Effective) -> int:
    """The round of the current loop of the code review, from its reports."""
    return current_round(facts.get(FACT_CODE_REVIEW_REPORTS, []), e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD))


def code_review_state(facts: dict, e: cc.Effective) -> tuple[str, bool]:
    """One line on the review of the code, and whether it blocks. It blocks only when the contract sets
    review.code_blocks, and then in four cases: the facts hold no code review, no report exists, the newest
    report is open at the threshold or has no severity line, or the newest report names another commit than
    the head commit. The limit of the rounds changes the words of the line, not the readiness."""
    if not any(is_code(f) for f in facts[FACT_CHANGED_FILES]):
        return msg("code_review_not_needed", intents=INTENTS_DIR, plans=PLANS_DIR), False
    threshold = e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)
    if FACT_CODE_REVIEW_REPORTS not in facts:
        line, blocks = msg("code_review_no_facts"), True
    elif not facts[FACT_CODE_REVIEW_REPORTS]:
        line, blocks = msg("code_review_none"), True
    else:
        reports = facts[FACT_CODE_REVIEW_REPORTS]
        rounds, severity = code_review_round(facts, e), reports[-1]
        limit = e.values.get(FIELD_REVIEW_LOOP)
        where = msg("review_round", rounds=rounds, limit=limit) if limit is not None else msg("review_round_no_limit", rounds=rounds)
        values = dict(where=where, severity=severity, threshold=threshold)
        if severity is None:
            line, blocks = msg("code_review_no_line", where=where), True
        elif SEVERITIES.index(severity) < SEVERITIES.index(threshold):
            line, blocks = msg("code_review_closed", **values), False
        elif limit is not None and rounds >= limit:
            line, blocks = msg("code_review_limit", **values), True
        else:
            line, blocks = msg("code_review_open", **values), True
        commit, head = facts.get(FACT_CODE_REVIEW_COMMIT), facts.get(FACT_HEAD_COMMIT)
        if commit != head:
            line, blocks = msg("code_review_stale", line=line, commit=commit, head=head), True
    if not e.values.get(FIELD_CODE_BLOCKS):
        return msg("code_review_shadow", line=line, field=FIELD_CODE_BLOCKS), False
    return line, blocks


def merge_decision(facts: dict, e: cc.Effective, ready: bool, spec: dict) -> tuple[bool, str]:
    """Whether the verdict merges the change request, and the line that says so. It checks the conditions in
    their order and names the first one that does not hold. A missing fact means that a person merges: a
    missing commit agrees with no other commit, also with no other missing commit. The readiness stays as it is."""
    def person(message_id: str, **values: object) -> tuple[bool, str]:
        return False, msg("merge_person", reason=msg(message_id, **values))

    if not ready:
        return person("merge_not_ready")
    approver = spec.get(TIER_APPROVER)
    if approver != APPROVER_AGENT:
        return person("merge_approver", approver=approver, agent=APPROVER_AGENT)
    if e.values.get(FIELD_CODE_BLOCKS) is not True:
        return person("merge_shadow", field=FIELD_CODE_BLOCKS)
    head = facts.get(FACT_HEAD_COMMIT)
    if not head:
        return person("merge_no_head")
    if any(str(reason).lower().startswith(AGENT_DROP.strip().lower()) for reason in facts.get(FACT_DROPPED_FINDINGS) or []):
        return person("merge_agent_drop")
    threshold = e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)
    changed = facts[FACT_CHANGED_FILES]
    if any(f.startswith(INTENTS_DIR) for f in changed):
        return person("merge_intent", intents=INTENTS_DIR)
    if any(is_code(f) for f in changed):
        reports = facts.get(FACT_CODE_REVIEW_REPORTS) or []
        severity = reports[-1] if reports else None
        if (severity is None or SEVERITIES.index(severity) >= SEVERITIES.index(threshold)
                or facts.get(FACT_CODE_REVIEW_COMMIT) != head):
            return person("merge_code_review")
    if any(f.startswith(PLANS_DIR) for f in changed):
        folders = dict(plans=PLANS_DIR)
        reports = facts.get(FACT_REVIEW_REPORTS) or []
        if not reports:
            return person("merge_plan_none", **folders)
        severity = reports[-1]
        if severity is None:
            return person("merge_plan_no_line", **folders)
        if SEVERITIES.index(severity) >= SEVERITIES.index(threshold):
            return person("merge_plan_open", severity=severity, threshold=threshold, **folders)
        commit = facts.get(FACT_REVIEW_COMMIT)
        if commit != head:
            return person("merge_plan_commit", commit=commit, head=head, **folders)
    return True, msg("merge_verdict", approver=approver, head=head)


def run_outcome(facts: dict, e: cc.Effective, ready: bool) -> str | None:
    """The outcome of the agent run that built the change request, or None without the fact `run`. `manual`:
    the head commit is missing or is not the commit of the run, so a later push changed what the run built.
    `flawed`: the verdict is not ready, or the newest report of the intent review or of the code review is
    open at the threshold or has no severity line, also in the shadow period. Else `success`. Information only."""
    run = facts.get(FACT_RUN)
    if run is None:
        return None
    head = facts.get(FACT_HEAD_COMMIT)
    if not head or head.lower() != run[RUN_COMMIT].lower():
        return RUN_MANUAL
    threshold = e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)
    for key in (FACT_REVIEW_REPORTS, FACT_CODE_REVIEW_REPORTS):
        reports = facts.get(key) or []
        if reports and (reports[-1] is None or SEVERITIES.index(reports[-1]) >= SEVERITIES.index(threshold)):
            return RUN_FLAWED
    return RUN_SUCCESS if ready else RUN_FLAWED


def run_line(facts: dict, outcome: str | None) -> str:
    """The line of the verdict on the run, with `none` for a value that the block does not hold."""
    if outcome is None:
        return msg("run_none")
    run = facts[FACT_RUN]
    turns, duration, cost = (run.get(key) for key in RUN_NUMBERS)
    count = run.get(RUN_COUNT) or 1
    return msg("run_many" if count > 1 else "run", outcome=outcome, count=count,
               turns=RUN_NONE if turns is None else f"{turns:.0f}",
               duration=RUN_NONE if duration is None else msg("run_seconds", value=duration),
               cost=RUN_NONE if cost is None else msg("run_dollars", value=cost))


def run_record(facts: dict, outcome: str | None) -> dict | None:
    """The run in the evidence record: the outcome and the three numbers, or None."""
    if outcome is None:
        return None
    run = facts[FACT_RUN]
    return {RUN_OUTCOME: outcome, **{key: run.get(key) for key in RUN_NUMBERS},
            **({RUN_COUNT: run[RUN_COUNT]} if run.get(RUN_COUNT) else {})}


def gate_plan(facts: dict, e: cc.Effective) -> GateResult | None:
    """The plan of the work item exists before the code. None when the contract does not set the flag. A
    change of intents alone is the Plan phase and needs no plan. An intent that the change request removes or
    renames away needs no plan (#71); an intent that it does not touch still does, so a wrong path in an issue
    still fails. It checks the result, not the order of commits."""
    if not e.values.get(FIELD_PLAN_BEFORE_CODE):
        return None
    changed = facts[FACT_CHANGED_FILES]
    if changed and all(f.startswith(INTENTS_DIR) for f in changed):
        return GateResult(CMD_PLAN, True, [msg("plan_intents_only", dir=INTENTS_DIR)])
    intents = facts.get(FACT_INTENTS, [])
    if not intents:
        return GateResult(CMD_PLAN, False, [msg("plan_no_intent", dir=INTENTS_DIR, suffix=INTENT_SUFFIX)])
    removed = [i[INTENT_PATH] for i in intents if i.get(INTENT_REMOVED)]
    kept = [i for i in intents if not i.get(INTENT_REMOVED)]
    missing = [i[INTENT_PATH] for i in kept if not i[INTENT_PLAN]]
    present = [plan_of(i[INTENT_PATH]) for i in kept if i[INTENT_PLAN]]
    return GateResult(CMD_PLAN, not missing,
                      [msg("plan_missing", plan=plan_of(i), old=old_plan_of(i)) for i in missing]
                      + [msg("plan_ok", plan=p) for p in present]
                      + [msg("plan_removed", intent=i) for i in removed])


def gate_verdict(facts: dict, e: cc.Effective) -> tuple[bool, list[str], dict]:
    gates = [gate_link(facts), gate_documents(facts, e)]
    plan = gate_plan(facts, e)
    if plan is not None:
        gates.append(plan)
    reasons: list[str] = []
    passed = all(g.passed for g in gates)
    for g in gates:
        reasons += [f"{g.gate}: {r}" for r in g.reasons]

    checks: dict[str, str] = facts[FACT_CHECKS]
    not_passed = sorted(name for name, state in checks.items() if state != CHECK_PASS)
    if not checks:
        passed = False
        reasons.append(msg("no_checks"))
    elif not_passed:
        passed = False
        reasons.append(msg("checks_pending", names=not_passed))
    else:
        reasons.append(msg("checks_ok", names=sorted(checks)))
    product, product_blocks = product_line(facts, e)
    reasons.append(product)
    if product_blocks:
        passed = False

    threads = facts[FACT_UNRESOLVED_THREADS]
    if threads:
        passed = False
        reasons.append(msg("threads_open", count=threads))
    else:
        reasons.append(msg("threads_ok"))
    reasons.append(review_loop_state(facts, e))
    code_line, code_blocks = code_review_state(facts, e)
    reasons.append(code_line)
    if code_blocks:
        passed = False

    tier, spec = tier_of(facts[FACT_CHANGED_FILES], e)
    detail: dict = {JSON_KEY_TIER: tier, JSON_KEY_APPROVER: spec.get(TIER_APPROVER), JSON_KEY_MERGES: [],
                    RECORD_REVIEW_ROUND: review_round(facts, e), CODE_REVIEW_ROUND: code_review_round(facts, e)}
    if tier is None:
        passed = False
        reasons.append(msg("no_tier"))
    else:
        who = e.values.get(FIELD_ROLE.format(role=spec.get(TIER_APPROVER)), [])
        detail[JSON_KEY_MERGES] = who
        reasons.append(msg("tier", tier=tier, review=spec.get(TIER_REVIEW), approver=spec.get(TIER_APPROVER), who=who))
    merges, merge_line = merge_decision(facts, e, passed, spec)
    reasons.append(merge_line)
    detail[RECORD_MERGE_BY_VERDICT] = merges
    outcome = run_outcome(facts, e, passed)
    reasons.append(run_line(facts, outcome))
    detail[FACT_RUN] = run_record(facts, outcome)
    if tier is not None:
        reasons.append(msg("approvals_not_checked", approver=spec.get(TIER_APPROVER)))
    detail[JSON_KEY_GATES] = [g.as_dict() for g in gates]
    return passed, reasons, detail


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def report(result: GateResult, as_json: bool) -> int:
    if as_json:
        print(json.dumps(result.as_dict(), indent=2))
    else:
        for r in result.reasons:
            cc.emit(OUT_GATE_PASS if result.passed else OUT_GATE_FAIL, f"{result.gate}: {r}")
    return cc.PASS if result.passed else cc.FAIL


def cmd_link(args) -> int:
    return report(gate_link(load_facts(args.facts)), args.json)


def cmd_documents(args) -> int:
    return report(gate_documents(load_facts(args.facts), effective(args)), args.json)


def repo_only(args) -> cc.Effective:
    """The repo contract alone, without its organization source: for a run that has no access to it."""
    fields = cc.load_schema(args.schema)
    repo = cc.validate(cc.load_toml(args.contract), fields, str(args.contract))
    if repo.role != cc.ROLE_REPO:
        repo.errors.append(cc.msg("not_repo", name=args.contract))
    if repo.errors:
        raise cc.CannotRun("; ".join(repo.errors))
    return cc.Effective(dict(repo.values), fields, [], "", dict(repo.values))


def cmd_boundary(args) -> int:
    try:
        text = args.changed.read_text()
    except OSError as error:
        raise cc.CannotRun(cc.msg("no_file", path=args.changed)) from error
    changed, lines = changed_paths(text)
    return report(gate_boundary(changed, effective(args), lines), args.json)


def cmd_tier(args) -> int:
    """The tier of the changed paths and the depth of its review, one on each line, for the reviewer of the code."""
    try:
        text = args.changed.read_text()
    except OSError as error:
        raise cc.CannotRun(cc.msg("no_file", path=args.changed)) from error
    changed, _ = changed_paths(text)
    tier, spec = tier_of(changed, repo_only(args) if args.repo_only else effective(args))
    if tier is None:
        return report(GateResult(CMD_TIER, False, [msg("no_tier")]), args.json)
    if args.json:
        print(json.dumps({JSON_KEY_TIER: tier, TIER_REVIEW: spec.get(TIER_REVIEW)}, indent=2))
    else:
        print(tier)
        print(spec.get(TIER_REVIEW))
    return cc.PASS


def cmd_quality(args) -> int:
    e = repo_only(args) if args.repo_only else effective(args)
    return report(gate_quality(e, args.contract.resolve().parent), args.json)


def cmd_product(args) -> int:
    e = repo_only(args) if args.repo_only else effective(args)
    return report(gate_product(e, args.contract.resolve().parent), args.json)


def build_record(facts: dict, verdict: str, origin: str, reasons: list[str], detail: dict,
                 scripts_version: str, time: str) -> dict:
    """The evidence record of one change: the verdict and its facts, in the documented form."""
    return {
        RECORD_KEYS[0]: RECORD_FORM,
        RECORD_KEYS[1]: facts[FACT_CHANGE_REQUEST],
        RECORD_KEYS[2]: time,
        RECORD_KEYS[3]: scripts_version,
        JSON_KEY_VERDICT: verdict,
        JSON_KEY_SOURCE: origin,
        JSON_KEY_REASONS: reasons,
        **detail,
        FACT_CHECKS: facts[FACT_CHECKS],
        RECORD_KEYS[4]: facts.get(FACT_FALSE_FAILURES, []),
        RECORD_KEYS[5]: facts.get(FACT_DROPPED_FINDINGS, []),
        RECORD_KEYS[6]: facts.get(FACT_FALSE_FINDINGS, []),
        RECORD_KEYS[7]: facts.get(FACT_REVIEW_ROUNDS, 0),
        RECORD_KEYS[8]: facts.get(FACT_REVIEW_SEVERITY),
        RECORD_KEYS[9]: facts.get(FACT_INTENTS, []),
        RECORD_KEYS[10]: facts.get(FACT_REVIEW_REPORTS, []),
        RECORD_REVIEW_ROUND: detail.get(RECORD_REVIEW_ROUND, 0),
        FACT_CODE_REVIEW_REPORTS: facts.get(FACT_CODE_REVIEW_REPORTS, []),
        CODE_REVIEW_ROUND: detail.get(CODE_REVIEW_ROUND, 0),
        CODE_REVIEW_SEVERITY: (facts.get(FACT_CODE_REVIEW_REPORTS) or [None])[-1],
        RECORD_MERGE_BY_VERDICT: detail.get(RECORD_MERGE_BY_VERDICT) is True,
        FACT_RUN: detail.get(FACT_RUN),
    }


def cmd_verdict(args) -> int:
    e = effective(args)
    facts = load_facts(args.facts)
    passed, reasons, detail = gate_verdict(facts, e)
    verdict = VERDICT_READY if passed else VERDICT_NOT_READY
    record = build_record(facts, verdict, e.origin, reasons, detail, args.scripts_version,
                          datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    if args.record:
        args.record.write_text(json.dumps(record, indent=2))
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print(verdict)
        for r in reasons:
            print(f"  {r}")
    return cc.PASS if passed else cc.FAIL


def answer_of(facts: dict, e: cc.Effective, by_person: bool) -> tuple[bool, str, dict]:
    """The decision on an answer of an agent, for a change request as the facts describe it: whether it starts,
    the reason, and the values of the answer. Before the state of the review loops, the change request is
    open, comes from a branch of this repo, its branch is the branch of a run, and it links the open issue
    that the branch names."""
    state = facts.get(FACT_STATE)
    if state != STATE_OPEN:
        return False, msg("answer_not_open", state=state), {}
    if facts.get(FACT_FROM_FORK) is not False:
        return False, msg("answer_fork"), {}
    branch = facts.get(FACT_HEAD_BRANCH)
    match = RUN_BRANCH.match(branch) if isinstance(branch, str) else None
    if not match:
        return False, msg("answer_no_branch", branch=branch, form=RUN_BRANCH_FORM.format(number="<number>")), {}
    number = int(match.group(1))
    if not any(i.get(ISSUE_NUMBER) == number and str(i.get(ISSUE_STATE)).lower() == STATE_OPEN
               for i in facts[FACT_LINKED_ISSUES]):
        return False, msg("answer_no_issue", number=number), {}
    start, reason, rounds = answer_state(facts, e, by_person)
    values = {OUT_ISSUE: number, OUT_BRANCH: branch, OUT_COMMIT: facts.get(FACT_HEAD_COMMIT), OUT_ROUND: rounds,
              OUT_THRESHOLD: e.values.get(FIELD_REVIEW_THRESHOLD, DEFAULT_REVIEW_THRESHOLD)}
    return start, reason, values if start else {}


def cmd_answer(args) -> int:
    """Print the decision as lines `name=value`, for the outputs of a step: `start`, `reason`, and, when the
    answer starts, the issue, the branch, the head commit, the round, and the threshold. A decision ends with
    0 in both cases; only a command that could not run ends with another code."""
    start, reason, values = answer_of(load_facts(args.facts), effective(args), args.by == ANSWER_BY_PERSON)
    out = {OUT_START: "true" if start else "false", OUT_REASON: reason, **values}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for name, value in out.items():
            print(f"{name}={value}")
    return cc.PASS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="charter_gate", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(f"--{cc.ARG_SCHEMA}", type=Path, default=cc.DEFAULT_SCHEMA)
    sub = parser.add_subparsers(dest="command", required=True)
    specs = {
        CMD_LINK: (cmd_link, True, False),
        CMD_DOCUMENTS: (cmd_documents, True, True),
        CMD_QUALITY: (cmd_quality, False, True),
        CMD_PRODUCT: (cmd_product, False, True),
        CMD_BOUNDARY: (cmd_boundary, False, True),
        CMD_VERDICT: (cmd_verdict, True, True),
        CMD_TIER: (cmd_tier, False, True),
        CMD_ANSWER: (cmd_answer, True, True),
    }
    for name, (_, needs_facts, needs_contract) in specs.items():
        p = sub.add_parser(name)
        if needs_facts:
            p.add_argument(f"--{ARG_FACTS}", type=Path, required=True)
        if needs_contract:
            p.add_argument(f"--{cc.ARG_CONTRACT}", type=Path, required=True)
            p.add_argument(f"--{cc.ARG_SOURCE}", type=Path, default=None)
            p.add_argument(f"--{cc.ARG_CACHE_DIR.replace('_', '-')}", dest=cc.ARG_CACHE_DIR, type=Path,
                           default=Path(cc.os.environ.get(cc.ENV_CACHE_DIR, cc.DEFAULT_CACHE_DIR)))
        p.add_argument(f"--{cc.ARG_JSON}", action="store_true")
        if name == CMD_VERDICT:
            p.add_argument(f"--{ARG_RECORD}", type=Path, default=None, help="write the evidence record to this file")
            p.add_argument(f"--{ARG_SCRIPTS_VERSION.replace('_', '-')}", dest=ARG_SCRIPTS_VERSION, default="",
                           help="the version of the scripts that make the record, for example a commit")
        if name == CMD_ANSWER:
            p.add_argument(f"--{ARG_BY}", choices=(ANSWER_BY_FACTORY, ANSWER_BY_PERSON), default=ANSWER_BY_FACTORY,
                           help="who starts the answer; the factory starts one only when the contract says so")
        if name in (CMD_BOUNDARY, CMD_TIER):
            p.add_argument(f"--{ARG_CHANGED}", type=Path, required=True,
                           help="a file with the paths that the run changed: with NUL between them, or one on each line")
        if name in (CMD_QUALITY, CMD_PRODUCT, CMD_TIER):
            p.add_argument(f"--{ARG_REPO_ONLY.replace('_', '-')}", dest=ARG_REPO_ONLY, action="store_true",
                           help="read the repo contract alone, without its organization source")
    args = parser.parse_args(argv)
    try:
        return specs[args.command][0](args)
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
