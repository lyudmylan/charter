#!/usr/bin/env python3
"""Charter contract checker. Python 3.11 or later, standard library only.

Commands:
  validate FILE                      Validate one file: an organization file or a repo contract.
  check CONTRACT                     Check a repo contract against its organization source.
  instructions FILE --contract C     Check an instruction file against the effective contract.

Options:
  --schema PATH      The schema. Default: schema/contract.toml next to this script.
  --source PATH      The organization file. Default: resolved from the cache.
  --cache-dir DIR    The cache of organization sources. Default: ~/.charter/cache
  --json             Print the effective contract as JSON (check only).

Exit codes: 0 pass, 1 fail, 2 the check could not run. The message names the cause.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PASS, FAIL, CANNOT_RUN = 0, 1, 2

RESERVED = {"schema", "organization", "repo", "source", "locks"}
KINDS = {"flag", "limit", "count", "set", "choice", "text"}
ID_PATTERN = re.compile(r"\[([a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+)\]")


class CannotRun(Exception):
    """The check could not run. The message names the cause."""


# --- Loading ---------------------------------------------------------------


def load_toml(path: Path) -> dict:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise CannotRun(f"no file: {path}")
    except PermissionError:
        raise CannotRun(f"access denied: {path}")
    except tomllib.TOMLDecodeError as e:
        raise CannotRun(f"not TOML: {path}, {e}")


def parse_toml_text(text: str, name: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise CannotRun(f"not TOML: {name}, {e}")


def load_schema(path: Path) -> dict:
    data = load_toml(path)
    fields = data.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise CannotRun(f"schema has no fields: {path}")
    for name, spec in fields.items():
        if spec.get("kind") not in KINDS:
            raise CannotRun(f"schema field {name} has an unknown kind")
        if spec["kind"] == "choice" and not spec.get("order"):
            raise CannotRun(f"schema field {name} is a choice without order")
    return fields


# --- Flattening and matching ----------------------------------------------


def flatten(table: dict, prefix: str = "") -> dict[str, object]:
    """Turn nested tables into {"a.b.c": value}. Lists of tables are not used."""
    out: dict[str, object] = {}
    for key, value in table.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def match_field(path: str, fields: dict) -> str | None:
    """Return the schema pattern that matches a concrete field path."""
    if path in fields:
        return path
    parts = path.split(".")
    for pattern in fields:
        pp = pattern.split(".")
        if len(pp) == len(parts) and all(a == b or a == "*" for a, b in zip(pp, parts)):
            return pattern
    return None


# --- Validation -------------------------------------------------------------


def check_value(kind: str, value: object, spec: dict) -> str | None:
    """Return a message when the value does not fit the kind, else None."""
    if kind == "flag":
        if not isinstance(value, bool):
            return "expected true or false"
    elif kind in ("limit", "count"):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return "expected a whole number of 0 or more"
    elif kind == "set":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return "expected a list of text"
    elif kind == "choice":
        if value not in spec["order"]:
            return f"expected one of {spec['order']}"
    elif kind == "text":
        if not (isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))):
            return "expected text or a list of text"
    return None


def validate(data: dict, fields: dict, name: str) -> tuple[str, dict[str, object], list[str], list[str]]:
    """Validate one file. Returns (role, values, locks, errors)."""
    errors: list[str] = []
    if data.get("schema") != 1:
        errors.append(f"{name}: schema must be 1")
    has_org = isinstance(data.get("organization"), dict)
    has_repo = isinstance(data.get("repo"), dict)
    if has_org == has_repo:
        errors.append(f"{name}: the file must have exactly one of [organization] or [repo]")
        role = "unknown"
    else:
        role = "organization" if has_org else "repo"

    if role == "organization":
        if not isinstance(data["organization"].get("name"), str):
            errors.append(f"{name}: organization.name is missing or not text")
        if "source" in data:
            errors.append(f"{name}: an organization file has no [source]")
    if role == "repo":
        if not isinstance(data["repo"].get("name"), str):
            errors.append(f"{name}: repo.name is missing or not text")
        source = data.get("source")
        if not isinstance(source, dict):
            errors.append(f"{name}: [source] is missing")
        else:
            for key in ("address", "file", "version"):
                if not isinstance(source.get(key), str) or not source[key]:
                    errors.append(f"{name}: source.{key} is missing or not text")
        if "locks" in data:
            errors.append(f"{name}: a repo contract has no [locks]")

    locks: list[str] = []
    if role == "organization" and "locks" in data:
        lock_table = data["locks"]
        raw = lock_table.get("fields") if isinstance(lock_table, dict) else None
        if not isinstance(raw, list) or not all(isinstance(v, str) for v in raw):
            errors.append(f"{name}: locks.fields must be a list of text")
        else:
            locks = raw

    values: dict[str, object] = {}
    body = {k: v for k, v in data.items() if k not in RESERVED}
    for path, value in flatten(body).items():
        pattern = match_field(path, fields)
        if pattern is None:
            errors.append(f"{name}: unknown field {path}")
            continue
        spec = fields[pattern]
        problem = check_value(spec["kind"], value, spec)
        if problem:
            errors.append(f"{name}: field {path}: {problem}")
            continue
        values[path] = value

    for lock in locks:
        if match_field(lock, fields) is None:
            errors.append(f"{name}: lock names an unknown field {lock}")
        elif lock not in values:
            errors.append(f"{name}: locked field without value: {lock}")
    return role, values, locks, errors


# --- Comparison -------------------------------------------------------------


def equal_or_stricter(kind: str, org: object, repo: object, spec: dict) -> bool:
    if kind == "flag":
        return repo is True or org is False
    if kind == "limit":
        return repo <= org
    if kind == "count":
        return repo >= org
    if kind == "set":
        return set(org).issubset(set(repo))
    if kind == "choice":
        return spec["order"].index(repo) >= spec["order"].index(org)
    return repo == org


# --- Source resolution ------------------------------------------------------


def cache_path(address: str, cache_dir: Path) -> Path:
    stripped = re.sub(r"^[a-z]+://", "", address).rstrip("/")
    stripped = re.sub(r"\.git$", "", stripped)
    return cache_dir / Path(stripped)


def resolve_source(source: dict, explicit: Path | None, cache_dir: Path) -> tuple[dict, str]:
    """Return (organization data, description of where it came from)."""
    if explicit is not None:
        return load_toml(explicit), str(explicit)
    address, file, version = source["address"], source["file"], source["version"]
    repo_dir = cache_path(address, cache_dir)
    if not repo_dir.is_dir():
        raise CannotRun(
            f"source not found: {address}. Populate the cache: git clone {address} {repo_dir}"
        )
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "show", f"{version}:{file}"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        raise CannotRun("git not found on this computer")
    except PermissionError:
        raise CannotRun(f"access denied: {repo_dir}")
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
        raise CannotRun(f"version not found: {version} of {file} in {address}. {detail}")
    return parse_toml_text(result.stdout, f"{address}@{version}:{file}"), f"{address} version {version}"


# --- Commands ---------------------------------------------------------------


def cmd_validate(args) -> int:
    fields = load_schema(args.schema)
    data = load_toml(args.file)
    role, _, _, errors = validate(data, fields, str(args.file))
    for e in errors:
        print(f"fail: {e}")
    if errors:
        return FAIL
    print(f"valid: {args.file} ({role})")
    return PASS


def effective_contract(args) -> tuple[dict, list[str], str]:
    """Load, validate, and merge. Returns (effective values, failures, source description)."""
    fields = load_schema(args.schema)
    repo_data = load_toml(args.contract)
    role, repo_values, _, errors = validate(repo_data, fields, str(args.contract))
    if role != "repo":
        errors.append(f"{args.contract}: not a repo contract")
    if errors:
        return {}, errors, ""
    org_data, origin = resolve_source(repo_data["source"], args.source, args.cache_dir)
    org_role, org_values, locks, org_errors = validate(org_data, fields, origin)
    if org_role != "organization":
        org_errors.append(f"{origin}: not an organization file")
    if org_errors:
        return {}, org_errors, origin
    failures: list[str] = []
    for path, repo_value in repo_values.items():
        if path in locks:
            spec = fields[match_field(path, fields)]
            if not equal_or_stricter(spec["kind"], org_values[path], repo_value, spec):
                failures.append(
                    f"weakens locked rule {path}: organization {org_values[path]!r}, repo {repo_value!r}"
                )
    effective = dict(org_values)
    effective.update(repo_values)
    effective["_fields"] = fields  # for the instructions command
    return effective, failures, origin


def cmd_check(args) -> int:
    effective, failures, origin = effective_contract(args)
    if origin:
        print(f"source: {origin}")
    for f in failures:
        print(f"fail: {f}")
    if failures:
        return FAIL
    effective.pop("_fields", None)
    if args.json:
        print(json.dumps({"source": origin, "effective": effective}, indent=2, sort_keys=True))
    print(f"pass: {args.contract} obeys its organization source")
    return PASS


def cmd_instructions(args) -> int:
    effective, failures, origin = effective_contract(args)
    if failures:
        for f in failures:
            print(f"fail: {f}")
        return FAIL
    effective.pop("_fields", None)
    try:
        text = args.file.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CannotRun(f"no file: {args.file}")
    except PermissionError:
        raise CannotRun(f"access denied: {args.file}")
    problems: list[str] = []
    ids = set(ID_PATTERN.findall(text))
    if not ids:
        problems.append(f"{args.file}: no rule identifiers found, expected [a.b] marks")
    for rule_id in sorted(ids):
        if rule_id not in effective:
            problems.append(f"{args.file}: identifier [{rule_id}] has no value in the contract or its source")
    lines = text.splitlines()
    for field, case_insensitive in (
        ("text.private_material_patterns", False),
        ("text.session_link_patterns", False),
        ("text.project_name_patterns", True),
    ):
        for pattern in effective.get(field, []) or []:
            for number, line in enumerate(lines, start=1):
                haystack = line.lower() if case_insensitive else line
                needle = pattern.lower() if case_insensitive else pattern
                if needle and needle in haystack:
                    problems.append(f"{args.file}:{number}: matches a pattern of {field}")
    for p in problems:
        print(f"fail: {p}")
    if problems:
        return FAIL
    print(f"pass: {args.file} agrees with the contract ({len(ids)} identifiers, source: {origin})")
    return PASS


def main(argv: list[str] | None = None) -> int:
    default_schema = Path(__file__).resolve().parent.parent / "schema" / "contract.toml"
    default_cache = Path(os.environ.get("CHARTER_CACHE_DIR", Path.home() / ".charter" / "cache"))

    parser = argparse.ArgumentParser(prog="charter_check", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--schema", type=Path, default=default_schema)
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="validate one file")
    p_validate.add_argument("file", type=Path)

    p_check = sub.add_parser("check", help="check a repo contract against its organization source")
    p_check.add_argument("contract", type=Path)
    p_check.add_argument("--source", type=Path, default=None)
    p_check.add_argument("--cache-dir", type=Path, default=default_cache)
    p_check.add_argument("--json", action="store_true")

    p_instr = sub.add_parser("instructions", help="check an instruction file against the contract")
    p_instr.add_argument("file", type=Path)
    p_instr.add_argument("--contract", type=Path, required=True)
    p_instr.add_argument("--source", type=Path, default=None)
    p_instr.add_argument("--cache-dir", type=Path, default=default_cache)

    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "check":
            return cmd_check(args)
        return cmd_instructions(args)
    except CannotRun as e:
        print(f"cannot run: {e}")
        return CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
