#!/usr/bin/env python3
"""Set a repo up for Charter: one command writes the contract, the rules, the intents folder, the
plans folder, the workflows, and the two documents. Python 3.11 or later, standard library only.

Run it in the root of the repo, from the installed plugin (`charter-setup`, on the path of the shell
while the plugin is enabled) or from a clone of the Charter repo at the version:

  charter-setup --repo NAME --source ADDRESS --source-version TAG --leader LOGIN [options]

Each value comes from a flag; when a flag is missing and the terminal is interactive, the setup asks.
It writes no file when any file that it would write exists; it names the files. It writes
`docs/product.md` and `docs/architecture.md` only when they are missing. At the end it prints the steps
that a person does by hand.

Exit codes: 0 done, 1 refused (a file exists, a value is missing, or the toolchain file is refused), 2 the setup could not run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charter_check as cc  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration. Every name, path, and message lives here, once.
# ---------------------------------------------------------------------------

PLUGIN_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = PLUGIN_DIR / "templates"
MANIFEST = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
MANIFEST_VERSION = "version"
CHARTER_ADDRESS = "https://github.com/lyudmylan/charter"
TAG_FORM = "charter--v{version}"

CONTRACT_FILE = "charter.toml"
INSTRUCTIONS_FILE = "AGENTS.md"
PRODUCT_FILE = "docs/product.md"
README_FILE = "README.md"
CLAUDE_FILE = "CLAUDE.md"          # when it exists, Claude Code reads it and not AGENTS.md
INTENT_TEMPLATE = "intents/_template.md"
PLAN_TEMPLATE = "plans/_template.md"
WORKFLOWS = ".github/workflows"

# template name -> written path. The order is the order of writing.
WRITTEN = {
    "charter.toml": CONTRACT_FILE,
    "AGENTS.md": INSTRUCTIONS_FILE,
    "intent.md": INTENT_TEMPLATE,
    "plan.md": PLAN_TEMPLATE,
    "tests.yml": f"{WORKFLOWS}/tests.yml",
    "verdict.yml": f"{WORKFLOWS}/verdict.yml",
    "review-intents.yml": f"{WORKFLOWS}/review-intents.yml",
    "review-code.yml": f"{WORKFLOWS}/review-code.yml",
    "run.yml": f"{WORKFLOWS}/run.yml",
}
# template name -> written path, only when the file is missing.
WRITTEN_IF_MISSING = {
    "architecture.md": "docs/architecture.md",
    "product.md": PRODUCT_FILE,
}
# The block of the toolchain in `tests.yml`: the steps of the repo that install its tools. The jobs `tests` and
# `product` of `tests.yml` and the workflow `run` have the same block, with the same steps.
TOOLCHAIN_TEMPLATE = "tests.yml"
TOOLCHAIN_TEMPLATES = (TOOLCHAIN_TEMPLATE, "run.yml")
TOOLCHAIN_VALUE = "toolchain"
TOOLCHAIN_START = "# charter:toolchain:start"
TOOLCHAIN_END = "# charter:toolchain:end"
STEP_INDENT = "      "
HIGH_TIER_PATHS = [CONTRACT_FILE, INSTRUCTIONS_FILE, "intents/**", f"{cc.MILESTONES_DIR}/**", ".github/**"]
# The product test in the contract: the commands of the flag, or the reason for none.
PRODUCT_LINE = "product = [{commands}]"
NO_PRODUCT_LINE = "no_product_reason = {reason}"
NO_PRODUCT_REASON = "no product to start yet"

DEFAULTS = {
    "source_file": "organization.toml",
    "tracker": "github-issues",
    "host": "github",
    "ci": "github-actions",
    "agent": "claude-code",
}
# flag -> the question for the interactive mode
ASKED = {
    "repo": "The name of the repo",
    "source": "The address of the organization source (a git URL)",
    "source_version": "The version of the organization source (a tag)",
    "leader": "Who holds the role of the leader (a login)",
}


class PercentTemplate(Template):
    """`%{name}` in a template, because the workflows use `${{ }}` themselves."""
    delimiter = "%"


MSG = {
    "exists": "refused: the file exists: {path}",
    "missing": "refused: no value for --{flag}; give it as a flag, or run the setup in a terminal",
    "written": "written: {path}",
    "kept": "kept: {path}",
    "toolchain_missing": "refused: the toolchain file is missing: {path}",
    "toolchain_marker": "refused: the toolchain file holds a marker line: {path}: {line}",
    "manifest": "the version of Charter cannot be read: {path}",
    "template": "the template is missing: {path}",
    "steps_title": "\nSteps that a person does by hand:",
    "step": "  {number}. {step}",
    "step_secret": "Set the secret CHARTER_ORG_TOKEN on the repo: a fine-grained token with read access to the organization source only. For the intent reviewer and the reviewer of the code, set CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`.",
    "step_merge": "Optional, for a repo that gives a tier the approver `agent`: set the secret CHARTER_MERGE_TOKEN, a fine-grained token with write access to the contents and the pull requests of this repo only. The verdict merges such a tier with it; a merge with the token of the workflow starts no workflow on the main branch.",
    "step_run": "For the workflow `run`: create the label charter-run, which starts a run on an issue. Set the secret CHARTER_RUN_TOKEN, a fine-grained token with write access to the contents and the pull requests of this repo only; the run publishes its change request with it, because a change request that the token of the workflow opens starts no workflow. The variable CHARTER_RUNS of the repo with the value off stops the start of every run. An agent answers the findings of the reviewers on the change request of a run; a person starts each answer, until the contract says run.answer_start = \"factory\".",
    "step_ruleset": "Protect the main branch with a ruleset: a change request is required, and the check \"verdict\" is required.",
    "step_cache": "On each computer, put the organization source in the cache of the checker: git clone {address} {cache}",
    "step_quality": "Put the test command of this repo in checks.quality of {contract}; the gate fails without one.",
    "step_product": "Write the product test of this repo: the commands that start the product and test it from the outside. Put them in checks.product of {contract}, and remove checks.no_product_reason. A run of an agent runs them in its sandbox, so they need no network and no secret.",
    "step_claude": "{claude} exists, so Claude Code does not read {instructions}. Add the line `@{instructions}` to {claude}.",
    "step_intents": "Write the first intent from {template}, and open the change request that adds it.",
}


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------


def toml_text(value: str) -> str:
    """A TOML basic string: quoted and escaped, so that a quote or a backslash in a value cannot break the file."""
    return json.dumps(value)


def toml_list(items: list[str]) -> str:
    return ", ".join(toml_text(item) for item in items)


def charter_version(manifest: Path = MANIFEST) -> str:
    try:
        return json.loads(manifest.read_text())[MANIFEST_VERSION]
    except (OSError, ValueError, KeyError):
        raise cc.CannotRun(msg("manifest", path=manifest))


def values_of(args: argparse.Namespace, target: Path, version: str) -> dict[str, str]:
    """The placeholders of the templates, from the arguments."""
    text_checked = [PRODUCT_FILE] + ([README_FILE] if (target / README_FILE).exists() else [])
    return {
        "repo": toml_text(args.repo),
        "source_address": toml_text(args.source),
        "source_file": toml_text(args.source_file),
        "source_version": toml_text(args.source_version),
        "charter_version": toml_text(version),
        "charter_address": CHARTER_ADDRESS,
        "tracker": toml_text(args.tracker),
        "host": toml_text(args.host),
        "ci": toml_text(args.ci),
        "leader": toml_list([args.leader]),
        "team_lead": toml_list([args.team_lead or args.leader]),
        "engineer": toml_list(args.engineer or [args.leader]),
        "agent": toml_list([args.agent]),
        "high_paths": toml_list(HIGH_TIER_PATHS + list(args.high_path)),
        "code_paths": toml_list(list(args.code_path)),
        "text_checked": toml_list(text_checked),
        "quality": toml_list(list(args.quality)),
        "product": (PRODUCT_LINE.format(commands=toml_list(list(args.product))) if args.product
                    else NO_PRODUCT_LINE.format(reason=toml_text(NO_PRODUCT_REASON))),
    }


def toolchain_block(path: Path | None) -> tuple[str, str | None]:
    """The steps of the toolchain file with the indent of a step, and the refusal or None. An empty line
    stays empty. No file gives no step. The text of the file is data: it is not substituted."""
    if path is None:
        return "", None
    if not path.is_file():
        return "", msg("toolchain_missing", path=path)
    lines = path.read_text().splitlines()
    for line in lines:
        if line.strip() in (TOOLCHAIN_START, TOOLCHAIN_END):
            return "", msg("toolchain_marker", path=path, line=line.strip())
    return "".join(f"{STEP_INDENT}{line}\n" if line else "\n" for line in lines), None


def toolchain_of(text: str) -> str:
    """The steps between the two marker lines of a written workflow, without the indent of a step, as the
    toolchain file gave them. No block or an empty block gives an empty text."""
    lines = text.splitlines()
    try:
        start = lines.index(STEP_INDENT + TOOLCHAIN_START)
        end = lines.index(STEP_INDENT + TOOLCHAIN_END, start + 1)
    except ValueError:
        return ""
    return "".join(f"{line.removeprefix(STEP_INDENT)}\n" for line in lines[start + 1:end])


def render(name: str, values: dict[str, str]) -> str:
    path = TEMPLATES / name
    if not path.is_file():
        raise cc.CannotRun(msg("template", path=path))
    return PercentTemplate(path.read_text()).substitute(values)


# ---------------------------------------------------------------------------
# The setup
# ---------------------------------------------------------------------------


def existing(target: Path) -> list[str]:
    return [written for written in WRITTEN.values() if (target / written).exists()]


def manual_steps(target: Path, args: argparse.Namespace, cache_dir: Path) -> list[str]:
    """The steps that a person does by hand, numbered in sequence; a step that does not apply is left out."""
    steps = [msg("step_secret"), msg("step_merge"), msg("step_run"), msg("step_ruleset"),
             msg("step_cache", address=args.source, cache=cc.cache_path(args.source, cache_dir))]
    if not args.quality:
        steps.append(msg("step_quality", contract=CONTRACT_FILE))
    if not args.product:
        steps.append(msg("step_product", contract=CONTRACT_FILE))
    if (target / CLAUDE_FILE).exists():
        steps.append(msg("step_claude", claude=CLAUDE_FILE, instructions=INSTRUCTIONS_FILE))
    steps.append(msg("step_intents", template=INTENT_TEMPLATE))
    return [msg("steps_title")] + [msg("step", number=n, step=step) for n, step in enumerate(steps, start=1)]


def setup(args: argparse.Namespace, target: Path, cache_dir: Path, out) -> int:
    found = existing(target)
    if found:
        for path in found:
            print(msg("exists", path=path), file=out)
        return cc.FAIL
    toolchain, refusal = toolchain_block(args.toolchain)
    if refusal:
        print(refusal, file=out)
        return cc.FAIL
    values = values_of(args, target, charter_version())
    rendered = {written: render(name, {**values, TOOLCHAIN_VALUE: toolchain} if name in TOOLCHAIN_TEMPLATES else values)
                for name, written in WRITTEN.items()}
    rendered_if_missing = {written: render(name, values) for name, written in WRITTEN_IF_MISSING.items()}
    for written, text in rendered.items():
        path = target / written
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(msg("written", path=written), file=out)
    for written, text in rendered_if_missing.items():
        path = target / written
        if path.exists():
            print(msg("kept", path=written), file=out)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(msg("written", path=written), file=out)
    for line in manual_steps(target, args, cache_dir):
        print(line, file=out)
    return cc.PASS


def ask_missing(args: argparse.Namespace, interactive: bool) -> str | None:
    """Fill the required values from the terminal; return the first flag that stays empty."""
    for flag, question in ASKED.items():
        if getattr(args, flag):
            continue
        if interactive:
            try:
                setattr(args, flag, input(f"{question}: ").strip())
            except EOFError:        # the end of the input is an empty answer, not a crash
                pass
        if not getattr(args, flag):
            return flag
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="charter_setup", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", help=ASKED["repo"])
    parser.add_argument("--source", help=ASKED["source"])
    parser.add_argument("--source-version", dest="source_version", help=ASKED["source_version"])
    parser.add_argument("--source-file", dest="source_file", default=DEFAULTS["source_file"])
    parser.add_argument("--leader", help=ASKED["leader"])
    parser.add_argument("--team-lead", dest="team_lead", help="default: the leader")
    parser.add_argument("--engineer", action="append", default=[], help="repeatable; default: the leader")
    parser.add_argument("--agent", default=DEFAULTS["agent"])
    parser.add_argument("--tracker", default=DEFAULTS["tracker"])
    parser.add_argument("--host", default=DEFAULTS["host"])
    parser.add_argument("--ci", default=DEFAULTS["ci"])
    parser.add_argument("--code-path", dest="code_path", action="append", default=[],
                        help="a path pattern whose change needs a document change; repeatable")
    parser.add_argument("--high-path", dest="high_path", action="append", default=[],
                        help="a path pattern added to the high risk tier; repeatable")
    parser.add_argument("--quality", action="append", default=[], help="a command that must pass before a push; repeatable")
    parser.add_argument("--product", action="append", default=[],
                        help="a command that starts the product and tests it from the outside; repeatable")
    parser.add_argument("--toolchain", type=Path, metavar="FILE",
                        help="the steps that install the tools of the repo, for the block of the tests workflow")
    parser.add_argument("--target", type=Path, default=Path("."), help="the root of the repo; default: here")
    parser.add_argument(f"--{cc.ARG_CACHE_DIR.replace('_', '-')}", dest=cc.ARG_CACHE_DIR, type=Path,
                        default=Path(cc.os.environ.get(cc.ENV_CACHE_DIR, cc.DEFAULT_CACHE_DIR)))
    args = parser.parse_args(argv)
    try:
        missing = ask_missing(args, sys.stdin.isatty())
        if missing:
            print(msg("missing", flag=missing.replace("_", "-")))
            return cc.FAIL
        return setup(args, args.target, getattr(args, cc.ARG_CACHE_DIR), sys.stdout)
    except cc.CannotRun as e:
        cc.emit(cc.OUT_CANNOT_RUN, str(e))
        return cc.CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
