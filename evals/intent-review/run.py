#!/usr/bin/env python3
"""The test set of the intent reviewer. Intent: intent-reviewer-test-set.
Run it from the root of the repo, on a machine with Claude Code: python3 evals/intent-review/run.py

Each folder under `cases/` is one real change request: the repo before the change, the changed intents and
plans, the text of the issue, and the answer that is right. The command gives each case to the reviewer in
the form of the workflow `review-intents`: the prompt, the limit of turns, and the tool list come from the
template of that workflow, and the skill comes from this folder of the repo. A stand-in for the command of
the code host answers from the files of the case, so a run reads nothing on the code host. Code grades the
report: the line of the highest open severity against the threshold of the contract, and the subject of the
finding where the case names one. It ends with 1 when a case gave no report, and with 2 when it cannot run.

Each case is one run of the model, on the account of the person who starts the command.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CASES = HERE / "cases"
TEMPLATE = ROOT / "charter" / "templates" / "review-intents.yml"
MARKER = "<!-- charter-intent-review -->"
LEVELS = ["none", "low", "medium", "high", "blocker"]
BLOCKS, PASSES = "blocks", "passes"
RIGHT, FALSE_ALARM, MISS, OTHER_SUBJECT, NO_REPORT = "right", "false alarm", "miss", "other subject", "no report"
CHANGE_REQUEST = "1"
TIMEOUT_SECONDS = 1200
SEVERITY = r"(none|low|medium|high|blocker)"
# The model of the reviewer on the code host: the workflow names none, and the action takes this one for a
# token of a subscription. The logs of the reviewer runs show it.
MODEL = "sonnet"
# The stand-in for the command of the code host. It answers a read of an issue and of the change request
# from the files of the case, and it knows no other command. The file of the issues holds one part for each
# issue of the case, with the number at the start of its first line.
STAND_IN_GH = '''#!/usr/bin/env python3
import os, re, sys
case, args = os.environ["CHARTER_EVAL_CASE"], sys.argv[1:]
read = lambda name: open(os.path.join(case, name)).read() if os.path.exists(os.path.join(case, name)) else ""
if tuple(args[:2]) == ("issue", "list"):
    sys.exit(0)
if tuple(args[:2]) == ("pr", "view"):
    print(read("change-request.md") or "no text in this case")
    sys.exit(0)
if tuple(args[:2]) != ("issue", "view"):
    sys.exit("the stand-in of the test set knows only: gh issue view, gh issue list, gh pr view")
number = next((a.lstrip("#") for a in args[2:] if a.lstrip("#").isdigit()), "")
for part in read("issue.md").split("\\n-----\\n"):
    if re.match(rf"\\s*#{number}\\b", part):
        print(part.strip())
        sys.exit(0)
sys.exit(f"issue #{number} is not in this case: the test set holds only the issues of the change request")
'''


class CannotRun(Exception):
    pass


def git(folder: Path, *args: str, stdin: bytes | None = None) -> str:
    done = subprocess.run(["git", "-C", str(folder), *args], input=stdin, capture_output=True, check=False)
    if done.returncode:
        raise CannotRun(f"git {' '.join(args[:2])}: {done.stderr.decode().strip()}")
    return done.stdout.decode().strip()


def read_case(folder: Path) -> dict:
    """The fields of a case, checked. A case names commits of this repo, or it holds the folders `base` and `head`."""
    path = folder / "case.toml"
    if not path.is_file():
        raise CannotRun(f"{folder.name}: no case.toml")
    case = tomllib.loads(path.read_text())
    if case.get("expected") not in (BLOCKS, PASSES):
        raise CannotRun(f"{folder.name}: expected is `{BLOCKS}` or `{PASSES}`")
    if not str(case.get("source", "")).strip():
        raise CannotRun(f"{folder.name}: the field source says where the right answer comes from")
    commits = "base" in case and "head" in case
    folders = (folder / "base").is_dir() and (folder / "head").is_dir()
    if commits == folders:
        raise CannotRun(f"{folder.name}: a case names the commits base and head, or it holds the folders base and head")
    if not (folder / "issue.md").is_file():
        raise CannotRun(f"{folder.name}: no issue.md")
    earlier = "earlier" in case if commits else (folder / "earlier").is_dir()
    if earlier != (folder / "earlier-report.md").is_file():
        raise CannotRun(f"{folder.name}: an earlier round needs its state and the file earlier-report.md, both")
    for pattern in case.get("finding", []):
        re.compile(pattern)
    return {**case, "name": folder.name, "folder": folder, "commits": commits, "has_earlier": earlier}


def put_state(case: dict, stage: str, workspace: Path) -> None:
    """Make the files of the workspace those of one state of the case. The test set itself never goes in."""
    if case["commits"]:
        for entry in workspace.iterdir():
            if entry.name != ".git":
                shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
        done = subprocess.run(["git", "-C", str(ROOT), "archive", case[stage]], capture_output=True, check=False)
        if done.returncode:
            raise CannotRun(f"{case['name']}: the commit {case[stage]} is not in this clone: {done.stderr.decode().strip()}")
        subprocess.run(["tar", "-x", "-C", str(workspace)], input=done.stdout, check=True)
    else:
        shutil.copytree(case["folder"] / stage, workspace, dirs_exist_ok=True)
    shutil.rmtree(workspace / "evals", ignore_errors=True)


def commit(workspace: Path, message: str) -> str:
    git(workspace, "add", "-A")
    git(workspace, "-c", "user.name=test set", "-c", "user.email=none", "commit", "--quiet",
        "--allow-empty", "-m", message)
    return git(workspace, "rev-parse", "HEAD")


def build(case: dict, work: Path) -> dict:
    """The workspace of a case: a repo with the base on `origin/main` and the change on its branch."""
    workspace, temp = work / "workspace", work / "temp"
    workspace.mkdir(parents=True)
    git(workspace, "init", "--quiet", "--initial-branch", "main")
    put_state(case, "base", workspace)
    base = commit(workspace, "the main branch before the change")
    git(workspace, "update-ref", "refs/remotes/origin/main", base)
    git(workspace, "checkout", "--quiet", "-b", "change")
    earlier_report = ""
    if case["has_earlier"]:
        put_state(case, "earlier", workspace)
        earlier = commit(workspace, "the change, the earlier round")
        text = (case["folder"] / "earlier-report.md").read_text()
        earlier_report = re.sub(r"(?m)^Commit: .*$", f"Commit: {earlier}", text, count=1)
        if f"Commit: {earlier}" not in earlier_report:
            raise CannotRun(f"{case['name']}: earlier-report.md has no line Commit:")
    put_state(case, "head", workspace)
    head = commit(workspace, "the change")
    # The skill and the scripts, as the workflow fetches them. Not the whole repo: the answers are in it.
    (temp / "charter").mkdir(parents=True)
    for part in ("charter", "charter-practices"):
        shutil.copytree(ROOT / part, temp / "charter" / part, ignore=shutil.ignore_patterns("evals", "__pycache__"))
    (temp / "review").mkdir()
    (temp / "review" / "earlier-reports.md").write_text(earlier_report + "\n\n=====\n\n" if earlier_report else "")
    (temp / "bin").mkdir()
    (temp / "bin" / "gh").write_text(STAND_IN_GH)
    (temp / "bin" / "gh").chmod(0o755)
    return {"workspace": workspace, "temp": temp, "head": head}


def workflow_form(temp: Path, head: str) -> tuple:
    """The prompt and the flags of the reviewer, from the template of the workflow."""
    text = TEMPLATE.read_text()
    block = re.search(r"(?m)^( +)prompt: \|\n((?:\1  .*\n|\s*\n)+)", text)
    limit = re.search(r"--max-turns (\d+)", text)
    mode = re.search(r"--permission-mode (\S+)", text)
    if not (block and limit and mode):
        raise CannotRun("the template of the workflow has no prompt, no limit of turns, or no permission mode")
    values = {"github.event.pull_request.number": CHANGE_REQUEST, "runner.temp": str(temp),
              "github.base_ref": "main", "github.event.pull_request.head.sha": head, "github.repository": "owner/name"}
    fill = lambda value: re.sub(r"\$\{\{ ([\w.]+) \}\}", lambda m: values[m.group(1)], value)  # noqa: E731
    indent = len(block.group(1)) + 2
    prompt = fill("\n".join(line[indent:] for line in block.group(2).splitlines()).strip() + "\n")
    flags = ["--max-turns", limit.group(1), "--permission-mode", mode.group(1)]
    for name in ("allowedTools", "disallowedTools"):
        flags += [f"--{name}", fill(re.search(rf'--{name} "([^"]+)"', text).group(1))]
    return prompt, flags


def review(case: dict, built: dict, model: str) -> dict:
    """One run of the reviewer. The settings of the person who starts it stay out of the run."""
    prompt, flags = workflow_form(built["temp"], built["head"])
    command = [os.environ.get("CHARTER_EVAL_CLAUDE", "claude"), "-p", "--output-format", "json",
               "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence", *flags]
    command += ["--model", model]
    env = {**os.environ, "PATH": f"{built['temp'] / 'bin'}{os.pathsep}{os.environ['PATH']}",
           "CHARTER_EVAL_CASE": str(case["folder"])}
    try:
        done = subprocess.run(command, input=prompt, text=True, capture_output=True, cwd=built["workspace"], env=env,
                              timeout=TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        return {"answer": "", "error": f"no end in {TIMEOUT_SECONDS} seconds"}
    try:
        record = json.loads(done.stdout)
    except ValueError:
        return {"answer": "", "error": " ".join((done.stderr or done.stdout).split())[:300] or "no output"}
    last = [r for r in (record if isinstance(record, list) else [record]) if isinstance(r, dict) and r.get("type") == "result"]
    if not last:
        return {"answer": "", "error": "the run left no result"}
    return {"answer": last[-1].get("result") or "", "turns": last[-1].get("num_turns"),
            "cost": last[-1].get("total_cost_usd"), "denied": len(last[-1].get("permission_denials") or [])}


def report_of(answer: str) -> str:
    """The report in a final answer: from the marker line on, as the workflow posts it."""
    lines = answer.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(MARKER)), None)
    return "" if start is None else "\n".join(lines[start:])


def findings(report: str) -> list:
    """(severity, text) of each numbered finding of a report."""
    start = rf"(?:\*\*)?\d+\.\s*(?:\*\*)?\s*{SEVERITY}\b"
    found = list(re.finditer(rf"(?mi)^{start}", report))
    ends = [match.start() for match in found[1:]] + [len(report)]
    return [(match.group(1).lower(), report[match.start():end]) for match, end in zip(found, ends)]


def grade(case: dict, report: str, threshold: str) -> dict:
    """The result of a case, by code. A report with no severity line is no report."""
    lines = re.findall(rf"(?mi)^Highest open severity:\s*\**\s*{SEVERITY}\b", report)
    if not lines:
        return {"result": NO_REPORT, "severity": None}
    severity = lines[-1].lower()
    answer = BLOCKS if LEVELS.index(severity) >= LEVELS.index(threshold) else PASSES
    if answer != case["expected"]:
        return {"result": FALSE_ALARM if answer == BLOCKS else MISS, "severity": severity}
    patterns = case.get("finding", [])
    if answer == BLOCKS and patterns:
        open_ones = [text for level, text in findings(report) if LEVELS.index(level) >= LEVELS.index(threshold)]
        if not any(re.search(p, text, re.I | re.S) for p in patterns for text in open_ones):
            return {"result": OTHER_SUBJECT, "severity": severity}
    return {"result": RIGHT, "severity": severity}


def run_case(case: dict, model: str, threshold: str, keep: Path) -> dict:
    work = Path(tempfile.mkdtemp(prefix="charter-eval-"))
    try:
        got = review(case, build(case, work), model)
        report = report_of(got.pop("answer"))
        (keep / f"{case['name']}.md").write_text(report or f"no report: {got.get('error', 'the final answer holds no marker line')}\n")
        return {"case": case["name"], "expected": case["expected"], **grade(case, report, threshold), **got}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def summary(rows: list, threshold: str, model: str, version: str) -> str:
    count = lambda name: sum(1 for row in rows if row["result"] == name)  # noqa: E731
    cost = sum(row.get("cost") or 0 for row in rows)
    lines = ["# The test set of the intent reviewer: one run", "",
             f"Cases: {len(rows)}. Right: {count(RIGHT)}. The threshold of the contract: {threshold}.",
             f"False alarms: {count(FALSE_ALARM)}. Misses: {count(MISS)}. Another subject: {count(OTHER_SUBJECT)}. "
             f"No report: {count(NO_REPORT)}.",
             f"Model: {model}. Claude Code: {version}. Cost that the runs report: {cost:.2f} USD.",
             "", "A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.",
             "A miss: the right answer blocks, and the reviewer gave no such finding.",
             "Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.",
             "", "| Case | Right answer | Highest open severity | Result | Turns |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| `{row['case']}` | {row['expected']} | {row['severity'] or '-'} | {row['result']} | {row.get('turns') or '-'} |")
    return "\n".join(lines) + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the test set of the intent reviewer.")
    parser.add_argument("--case", action="append", help="the name of one case; more than one is possible")
    parser.add_argument("--model", default=MODEL, help=f"the model of the reviewer; without it `{MODEL}`, as on the code host")
    parser.add_argument("--jobs", type=int, default=2, help="the number of cases that run at one time")
    parser.add_argument("--cases", type=Path, default=CASES, help="the folder of the cases")
    parser.add_argument("--out", type=Path, help="the folder of the result; a new folder under results/ without it")
    args = parser.parse_args(argv)
    try:
        if not shutil.which(os.environ.get("CHARTER_EVAL_CLAUDE", "claude")):
            raise CannotRun("Claude Code is not on the path")
        folders = sorted(p for p in args.cases.iterdir() if p.is_dir()) if args.cases.is_dir() else []
        if args.case:
            missing = sorted(set(args.case) - {p.name for p in folders})
            if missing:
                raise CannotRun(f"no such case: {', '.join(missing)}")
            folders = [p for p in folders if p.name in args.case]
        if not folders:
            raise CannotRun(f"no case under {args.cases}")
        cases = [read_case(folder) for folder in folders]
        threshold = tomllib.loads((ROOT / "charter.toml").read_text()).get("review", {}).get("threshold", "medium")
        out = args.out or HERE / "results" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        (out / "reports").mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            rows = list(pool.map(lambda case: run_case(case, args.model, threshold, out / "reports"), cases))
    except CannotRun as error:
        print(f"cannot run: {error}")
        return 2
    version = subprocess.run([os.environ.get("CHARTER_EVAL_CLAUDE", "claude"), "--version"], capture_output=True,
                             text=True, check=False).stdout.strip()
    text = summary(rows, threshold, args.model, version)
    (out / "report.md").write_text(text)
    (out / "result.json").write_text(json.dumps({"threshold": threshold, "model": args.model, "claude": version,
                                                 "cases": rows}, indent=1) + "\n")
    print(text)
    print(f"The result is in {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 1 if any(row["result"] == NO_REPORT for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
