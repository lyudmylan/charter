#!/usr/bin/env python3
"""Charter gates. Python 3.11 or later, standard library only. No model call.

A gate checks one change of a repo. The facts of the change request come from one JSON file
that a collecting step writes on the code host. The gates know no code host.

Commands:
  link      --facts F --contract C     The change request references an open issue.
  documents --facts F --contract C     A change under a code path changes a necessary document,
                                       or the change request records a reason.
  quality   --contract C               The quality checks of the contract run and pass.
  verdict   --facts F --contract C     One verdict: ready or not ready, with the reasons.

Options:
  --schema PATH, --source PATH, --cache-dir DIR   As in charter_check.
  --json                                          Print the result as one JSON object.

Exit codes: 0 pass, 1 fail, 2 the check could not run. The message names the cause.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
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
ARG_FACTS = "facts"

# Keys of the facts file.
FACT_CHANGE_REQUEST = "change_request"
FACT_LINKED_ISSUES = "linked_issues"        # [{"number": 22, "state": "open"}]
FACT_CHANGED_FILES = "changed_files"        # ["docs/product.md"]
FACT_REASON = "reason_for_no_document_change"   # text or null
FACT_UNRESOLVED_THREADS = "unresolved_review_threads"   # whole number
FACT_APPROVALS = "approvals"                # ["login"]
FACT_CHECKS = "checks"                      # {"tests": "pass"}
FACT_KEYS = (FACT_CHANGE_REQUEST, FACT_LINKED_ISSUES, FACT_CHANGED_FILES, FACT_REASON,
             FACT_UNRESOLVED_THREADS, FACT_APPROVALS, FACT_CHECKS)
ISSUE_NUMBER, ISSUE_STATE = "number", "state"
STATE_OPEN = "open"
CHECK_PASS = "pass"

# Fields of the contract that the gates read.
FIELD_CODE_PATHS = "documents.code_paths"
FIELD_NECESSARY = "documents.necessary"
FIELD_QUALITY = "checks.quality"
FIELD_ROLE = "roles.{role}"
TIERS_PREFIX = "tiers."
TIER_PATHS, TIER_APPROVER, TIER_REVIEW = "paths", "approver", "review"

# Output.
VERDICT_READY, VERDICT_NOT_READY = "ready", "not ready"
OUT_GATE_PASS, OUT_GATE_FAIL = cc.OUT_PASS, cc.OUT_FAIL
JSON_KEY_GATE, JSON_KEY_RESULT, JSON_KEY_REASONS, JSON_KEY_VERDICT = "gate", "result", "reasons", "verdict"
JSON_KEY_TIER, JSON_KEY_APPROVER, JSON_KEY_MERGES, JSON_KEY_GATES, JSON_KEY_SOURCE = "tier", "approver", "merges", "gates", cc.OUT_SOURCE

MSG = {
    "facts_not_json": "not JSON: {path}, {error}",
    "facts_missing_key": "the facts file has no key {key}: {path}",
    "no_linked_issue": "the change request references no issue",
    "no_open_issue": "the change request references no open issue: {issues}",
    "link_ok": "the change request references the open issue {issues}",
    "no_code_change": "no file under a code path changed",
    "document_changed": "a necessary document changed: {documents}",
    "reason_recorded": "no document changed; the recorded reason: {reason}",
    "no_document_no_reason": "a file under a code path changed ({files}), but no necessary document changed and no reason is recorded",
    "quality_none": "the contract declares no quality checks",
    "quality_ok": "passed: {command}",
    "quality_failed": "failed with exit code {code}: {command}",
    "quality_cannot_run": "cannot run: {command}: {error}",
    "checks_pending": "checks not passed: {names}",
    "checks_ok": "all checks passed: {names}",
    "no_checks": "no checks reported",
    "threads_open": "{count} unresolved review threads",
    "threads_ok": "no unresolved review thread",
    "tier": "tier {tier}: review {review}, the {approver} merges ({who})",
    "no_tier": "no tier matches the changed files",
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


def load_facts(path: Path) -> dict:
    text = cc.read_text(path)
    try:
        facts = json.loads(text)
    except json.JSONDecodeError as e:
        raise cc.CannotRun(msg("facts_not_json", path=path, error=e))
    for key in FACT_KEYS:
        if key not in facts:
            raise cc.CannotRun(msg("facts_missing_key", key=key, path=path))
    return facts


def effective(args) -> cc.Effective:
    e = cc.effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if e.failures:
        raise cc.CannotRun("; ".join(e.failures))
    return e


def matches(file: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(file, p) for p in patterns)


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


def gate_documents(facts: dict, e: cc.Effective) -> GateResult:
    code_paths = e.values.get(FIELD_CODE_PATHS, [])
    necessary = e.values.get(FIELD_NECESSARY, [])
    changed = facts[FACT_CHANGED_FILES]
    code_changes = [f for f in changed if matches(f, code_paths)]
    if not code_changes:
        return GateResult(CMD_DOCUMENTS, True, [msg("no_code_change")])
    documents = [f for f in changed if f in necessary]
    if documents:
        return GateResult(CMD_DOCUMENTS, True, [msg("document_changed", documents=documents)])
    reason = facts[FACT_REASON]
    if isinstance(reason, str) and reason.strip():
        return GateResult(CMD_DOCUMENTS, True, [msg("reason_recorded", reason=reason.strip())])
    return GateResult(CMD_DOCUMENTS, False, [msg("no_document_no_reason", files=code_changes)])


def gate_quality(e: cc.Effective, cwd: Path) -> GateResult:
    commands = e.values.get(FIELD_QUALITY, [])
    if not commands:
        return GateResult(CMD_QUALITY, False, [msg("quality_none")])
    reasons: list[str] = []
    passed = True
    for command in commands:
        try:
            result = subprocess.run(shlex.split(command), cwd=cwd, capture_output=True, text=True, check=False)
        except (FileNotFoundError, PermissionError) as error:
            reasons.append(msg("quality_cannot_run", command=command, error=error))
            passed = False
            continue
        if result.returncode == 0:
            reasons.append(msg("quality_ok", command=command))
        else:
            reasons.append(msg("quality_failed", command=command, code=result.returncode))
            passed = False
    return GateResult(CMD_QUALITY, passed, reasons)


def tier_of(changed: list[str], e: cc.Effective) -> tuple[str | None, dict]:
    """The tier of the change: the first declared tier that matches any changed file."""
    tiers: dict[str, dict] = {}
    for path, value in e.values.items():
        if path.startswith(TIERS_PREFIX):
            _, name, key = path.split(cc.PATH_SEPARATOR, 2)
            tiers.setdefault(name, {})[key] = value
    for name, spec in tiers.items():                       # declaration order: TOML keeps it
        if any(matches(f, spec.get(TIER_PATHS, [])) for f in changed):
            return name, spec
    return None, {}


def gate_verdict(facts: dict, e: cc.Effective) -> tuple[bool, list[str], dict]:
    gates = [gate_link(facts), gate_documents(facts, e)]
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

    threads = facts[FACT_UNRESOLVED_THREADS]
    if threads:
        passed = False
        reasons.append(msg("threads_open", count=threads))
    else:
        reasons.append(msg("threads_ok"))

    tier, spec = tier_of(facts[FACT_CHANGED_FILES], e)
    detail: dict = {JSON_KEY_TIER: tier, JSON_KEY_APPROVER: spec.get(TIER_APPROVER), JSON_KEY_MERGES: []}
    if tier is None:
        passed = False
        reasons.append(msg("no_tier"))
    else:
        who = e.values.get(FIELD_ROLE.format(role=spec.get(TIER_APPROVER)), [])
        detail[JSON_KEY_MERGES] = who
        reasons.append(msg("tier", tier=tier, review=spec.get(TIER_REVIEW), approver=spec.get(TIER_APPROVER), who=who))
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


def cmd_quality(args) -> int:
    return report(gate_quality(effective(args), args.contract.resolve().parent), args.json)


def cmd_verdict(args) -> int:
    e = effective(args)
    passed, reasons, detail = gate_verdict(load_facts(args.facts), e)
    verdict = VERDICT_READY if passed else VERDICT_NOT_READY
    if args.json:
        print(json.dumps({JSON_KEY_VERDICT: verdict, JSON_KEY_SOURCE: e.origin, JSON_KEY_REASONS: reasons, **detail}, indent=2))
    else:
        print(verdict)
        for r in reasons:
            print(f"  {r}")
    return cc.PASS if passed else cc.FAIL


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="charter_gate", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(f"--{cc.ARG_SCHEMA}", type=Path, default=cc.DEFAULT_SCHEMA)
    sub = parser.add_subparsers(dest="command", required=True)
    specs = {
        CMD_LINK: (cmd_link, True, False),
        CMD_DOCUMENTS: (cmd_documents, True, True),
        CMD_QUALITY: (cmd_quality, False, True),
        CMD_VERDICT: (cmd_verdict, True, True),
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
    args = parser.parse_args(argv)
    try:
        return specs[args.command][0](args)
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
