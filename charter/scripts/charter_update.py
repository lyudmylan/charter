#!/usr/bin/env python3
"""charter-update: moves a repo that is set up to the version of this Charter, in its working folder.

    charter-update [--target DIR] [--check] [--old-templates DIR]

A file that holds no content of the repo, such as a workflow or a template of an intent, gets the text of
this version; the block of the toolchain of the repo stays. The command compares each such file with the
text of the version that the contract names: a file that the repo changed by hand is written too, and its
lines are printed, so that no change is lost without notice. A file that holds content of the repo is not
changed: in the contract only the version line moves, and the command names each field and each rule that
this version adds. The result is a change of the working folder like any other: a person or an agent
opens the change request.

Exit codes: 0 done, or nothing to change; 1 refused; 2 cannot run.
"""

import argparse
import difflib
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charter_check as cc  # noqa: E402
import charter_setup as cs  # noqa: E402

CONTENT_TEMPLATES = ("charter.toml", "AGENTS.md")     # the contract and the rules file hold content of the repo
# template name -> written path, for each file that the command writes.
GENERATED = {name: path for name, path in cs.WRITTEN.items() if name not in CONTENT_TEMPLATES}
TAG = "charter--v{version}"
TEMPLATES_IN_REPO = Path("charter") / "templates"
VERSION_LINE = re.compile(r'(?ms)(^\[charter\][^\[]*?^version\s*=\s*)"[^"]*"')
RULE_ID = re.compile(r"\[([a-z_]+(?:\.[a-z_]+)+)\]")
PLACEHOLDER = re.compile(r"%\{([a-z_]+)\}")
DUMMY = '"a value of the repo"'
GIT_TIMEOUT_SECONDS = 120

MSG = {
    "no_contract": "no contract in this folder: {path}. Run the command in the root of a repo that is set up.",
    "no_version": "the contract names no version of Charter: {path}",
    "bad_version": "the version of Charter is not a row of numbers with points: {version}",
    "newer": "refused: the contract names Charter {old}, and this Charter is {new}. Update the plugin first.",
    "version_line": "refused: the version line of the table [charter] cannot be changed in {path}",
    "version": "version: {old} -> {new} in {path}",
    "same_version": "version: {new}, the contract names it already",
    "same": "same: {path}",
    "updated": "updated: {path}",
    "written": "written: {path}",
    "by_hand": "updated, and this repo changed it by hand: {path}. The lines of the repo, against Charter {old}:",
    "not_compared": "updated, not compared with Charter {old}: {path}. Read its difference before the change request.",
    "no_old": "the templates of Charter {old} are not here: {reason}. No file is compared with the old version.",
    "field": "new field: {key}. The contract template of this version sets it to {value}. The contract of this repo is not changed.",
    "rule": "new rule: [{key}]. The rules file of this version says: {line}",
    "rule_absent": "The rules file of this repo, {path}, cites none of the new rules: add them by hand.",
    "nothing": "nothing to change: the repo is at Charter {new}",
    "check": "check only: no file was written",
    "next": "Next: run `charter-check all {contract}`, then open a change request. The workflows are in the high risk tier.",
}


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


NUMBERS = re.compile(r"[0-9]+(\.[0-9]+)*")


def number(version: str) -> tuple:
    """The version as numbers, for the comparison. Another form, such as a version before a release, cannot run."""
    if not isinstance(version, str) or not NUMBERS.fullmatch(version):
        raise cc.CannotRun(msg("bad_version", version=version))
    return tuple(int(part) for part in version.split("."))


def with_version(text: str, new: str) -> str | None:
    """The contract text with the new version in the table [charter], or None when the line cannot be found."""
    changed = VERSION_LINE.sub(lambda m: f'{m.group(1)}"{new}"', text, count=1)
    try:
        return changed if tomllib.loads(changed)["charter"]["version"] == new else None
    except (tomllib.TOMLDecodeError, KeyError, TypeError):
        return None


def old_templates(version: str, address: str, folder: Path) -> tuple[Path | None, str]:
    """The templates of the named version, fetched at its tag into `folder`; or None and the reason."""
    try:
        result = subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--branch", TAG.format(version=version),
                                 address, str(folder)], capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    if result.returncode != 0 or not (folder / TEMPLATES_IN_REPO).is_dir():
        return None, (result.stderr.strip().splitlines() or ["no templates at the tag"])[-1]
    return folder / TEMPLATES_IN_REPO, ""


def text_of(templates: Path, name: str, toolchain: str) -> str | None:
    """The text of a generated file from the templates of one version, with the block of the repo."""
    path = templates / name
    if not path.is_file():
        return None
    block = "".join(f"{cs.STEP_INDENT}{line}\n" if line else "\n" for line in toolchain.splitlines())
    return cs.PercentTemplate(path.read_text()).safe_substitute(charter_address=cs.CHARTER_ADDRESS, toolchain=block)


def fields_of(templates: Path) -> dict:
    """The fields of the contract template, as `table.key` -> value. A placeholder stands for a value of the repo."""
    path = templates / "charter.toml"
    if not path.is_file():
        return {}
    lines = [f"placeholder_{m.group(1)} = {DUMMY}" if (m := PLACEHOLDER.fullmatch(line.strip())) else
             PLACEHOLDER.sub(DUMMY, line) for line in path.read_text().splitlines()]
    try:
        data = tomllib.loads("\n".join(lines))
    except tomllib.TOMLDecodeError:
        return {}
    found: dict = {}

    def walk(table: dict, prefix: str) -> None:
        for key, value in table.items():
            if isinstance(value, dict):
                walk(value, f"{prefix}{key}.")
            elif not key.startswith("placeholder_"):
                found[f"{prefix}{key}"] = value
    walk(data, "")
    return found


def rules_of(text: str) -> dict:
    """The rule identifiers that a rules file cites, each with the first line that cites it."""
    found: dict = {}
    for line in text.splitlines():
        for key in RULE_ID.findall(line):
            found.setdefault(key, line.strip())
    return found


def generated(target: Path, new: Path, old: Path | None, old_version: str, write: bool, out) -> bool:
    """Writes each generated file of this version. Returns True when a file changed."""
    changed = False
    tests = target / GENERATED[cs.TOOLCHAIN_TEMPLATE]
    shared = cs.toolchain_of(tests.read_text()) if tests.is_file() else ""
    for name, written in GENERATED.items():
        path = target / written
        here = path.read_text() if path.is_file() else None
        block = cs.toolchain_of(here) if here is not None and name in cs.TOOLCHAIN_TEMPLATES else shared
        text = text_of(new, name, block if name in cs.TOOLCHAIN_TEMPLATES else "")
        if text is None:
            raise cc.CannotRun(cs.msg("template", path=new / name))
        if here == text:
            print(msg("same", path=written), file=out)
            continue
        changed = True
        if here is None:
            print(msg("written", path=written), file=out)
        else:
            before = text_of(old, name, block if name in cs.TOOLCHAIN_TEMPLATES else "") if old else None
            if old is None or before is None:
                print(msg("not_compared", path=written, old=old_version), file=out)
            elif before == here:
                print(msg("updated", path=written), file=out)
            else:
                print(msg("by_hand", path=written, old=old_version), file=out)
                for line in difflib.unified_diff(before.splitlines(), here.splitlines(), f"Charter {old_version}",
                                                 "this repo", lineterm="", n=1):
                    print(f"  {line}", file=out)
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    return changed


def additions(target: Path, new: Path, old: Path | None, contract: dict, out) -> None:
    """Names each field and each rule that this version adds and the repo does not hold. It changes no file."""
    if old is None:
        return
    before, now = fields_of(old), fields_of(new)

    def held(key: str) -> bool:
        table = contract
        for part in key.split("."):
            if not isinstance(table, dict) or part not in table:
                return False
            table = table[part]
        return True
    for key, value in now.items():
        if key not in before and not held(key):
            print(msg("field", key=key, value=value if value != DUMMY.strip('"') else "a value of the repo"), file=out)
    old_rules = rules_of((old / "AGENTS.md").read_text()) if (old / "AGENTS.md").is_file() else {}
    new_rules = rules_of((new / "AGENTS.md").read_text()) if (new / "AGENTS.md").is_file() else {}
    instructions = target / str(contract.get("instructions", {}).get("file", cs.INSTRUCTIONS_FILE))
    cited = rules_of(instructions.read_text()) if instructions.is_file() else {}
    added = [(key, line) for key, line in new_rules.items() if key not in old_rules and key not in cited]
    for key, line in added:
        print(msg("rule", key=key, line=line), file=out)
    if added:
        print(msg("rule_absent", path=instructions.relative_to(target)), file=out)


def update(target: Path, new: Path, version: str, old_dir: Path | None, address: str, write: bool, out) -> int:
    path = target / cs.CONTRACT_FILE
    if not path.is_file():
        raise cc.CannotRun(msg("no_contract", path=path))
    text = path.read_text()
    try:
        contract = tomllib.loads(text)
        old_version = contract["charter"]["version"]
    except (tomllib.TOMLDecodeError, KeyError, TypeError):
        raise cc.CannotRun(msg("no_version", path=path))
    if number(old_version) > number(version):
        print(msg("newer", old=old_version, new=version), file=out)
        return cc.FAIL
    # Each refusal comes before the first write: a refused update changes no file.
    moved = None if old_version == version else with_version(text, version)
    if old_version != version and moved is None:
        print(msg("version_line", path=cs.CONTRACT_FILE), file=out)
        return cc.FAIL
    with tempfile.TemporaryDirectory() as folder:
        old, reason = (old_dir, "") if old_dir else old_templates(old_version, address, Path(folder) / "old")
        if old is not None and not old.is_dir():
            old, reason = None, f"no folder: {old}"
        if old is None:
            print(msg("no_old", old=old_version, reason=reason), file=out)
        changed = generated(target, new, old, old_version, write, out)
        additions(target, new, old, contract, out)
    if old_version == version:
        print(msg("same_version", new=version), file=out)
    else:
        if write:
            path.write_text(moved)
        print(msg("version", old=old_version, new=version, path=cs.CONTRACT_FILE), file=out)
        changed = True
    if not changed:
        print(msg("nothing", new=version), file=out)
        return cc.PASS
    print(msg("next", contract=cs.CONTRACT_FILE) if write else msg("check"), file=out)
    return cc.PASS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="charter-update", description=__doc__.split("\n\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", type=Path, default=Path("."), help="the root of the repo; default: here")
    parser.add_argument("--check", action="store_true", help="print what the update changes, and write no file")
    parser.add_argument("--old-templates", dest="old_templates", type=Path, metavar="DIR",
                        help="the folder charter/templates of the version that the contract names; default: fetched at its tag")
    parser.add_argument("--charter-address", dest="address", default=cs.CHARTER_ADDRESS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        return update(args.target, cs.TEMPLATES, cs.charter_version(), args.old_templates, args.address,
                      not args.check, sys.stdout)
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
