#!/usr/bin/env python3
"""Charter contract checker. Python 3.11 or later, standard library only.

Commands:
  validate FILE                      Validate one file: an organization file or a repo contract.
  check CONTRACT                     Check a repo contract against its organization source.
  instructions FILE --contract C     Check an instruction file against the effective contract.
  text FILE --contract C             Check any text file against the pattern sets of the contract.
  source CONTRACT                    Print the address, the file, the version, and the cache path of the source.
  all CONTRACT                       Run check, then instructions on the declared instruction file, then text
                                     on each declared text-checked file. The files are relative to the contract.

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
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration. Every name, key, message, and pattern lives here, once.
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1

# Exit codes.
PASS, FAIL, CANNOT_RUN = 0, 1, 2

# Commands.
CMD_VALIDATE, CMD_CHECK, CMD_INSTRUCTIONS, CMD_TEXT, CMD_SOURCE, CMD_ALL = "validate", "check", "instructions", "text", "source", "all"

# Reserved tables and keys of a contract file.
TABLE_SCHEMA = "schema"
TABLE_ORGANIZATION = "organization"
TABLE_REPO = "repo"
TABLE_SOURCE = "source"
TABLE_LOCKS = "locks"
KEY_NAME = "name"
KEY_FIELDS = "fields"
SOURCE_KEYS = ("address", "file", "version")
RESERVED_TABLES = {TABLE_SCHEMA, TABLE_ORGANIZATION, TABLE_REPO, TABLE_SOURCE, TABLE_LOCKS}

# Roles of a file.
ROLE_ORGANIZATION, ROLE_REPO, ROLE_UNKNOWN = TABLE_ORGANIZATION, TABLE_REPO, "unknown"

# Attributes of a field in the schema.
ATTR_KIND = "kind"
ATTR_ORDER = "order"
ATTR_TEXT_CHECK = "text_check"          # a set of patterns that text must not contain
TEXT_CHECK_EXACT = "exact"
TEXT_CHECK_IGNORE_CASE = "ignore_case"
TEXT_CHECKS = {TEXT_CHECK_EXACT, TEXT_CHECK_IGNORE_CASE}

WILDCARD = "*"
PATH_SEPARATOR = "."

# The cache of organization sources.
ENV_CACHE_DIR = "CHARTER_CACHE_DIR"
DEFAULT_CACHE_DIR = Path.home() / ".charter" / "cache"
DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "schema" / "contract.toml"
GIT = "git"
GIT_OPTION_DIR = "-C"
GIT_SHOW = "show"

# Command line arguments and JSON keys.
ARG_FILE, ARG_CONTRACT, ARG_SOURCE, ARG_CACHE_DIR, ARG_JSON, ARG_SCHEMA = "file", "contract", "source", "cache_dir", "json", "schema"
JSON_KEY_EFFECTIVE, JSON_KEY_FAILURES = "effective", "failures"

# Fields that the "all" command reads.
FIELD_INSTRUCTIONS_FILE = "instructions.file"
FIELD_TEXT_CHECKED = "documents.text_checked"

# Identifiers in an instruction file: [a.b] or [a.b.c]. Only a mark whose first segment is a
# field group of the schema counts; other bracketed text, such as a file name, is ignored.
ID_PATTERN = re.compile(r"\[([a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+)\]")
FILE_SUFFIXES = (".toml", ".md", ".yml", ".yaml", ".json", ".py", ".txt")   # [charter.toml] is a file, not a rule

# Output prefixes.
OUT_PASS, OUT_FAIL, OUT_CANNOT_RUN, OUT_VALID, OUT_SOURCE = "pass", "fail", "cannot run", "valid", "source"

# Messages. Each one is used in one place.
MSG = {
    "no_file": "no file: {path}",
    "access_denied": "access denied: {path}",
    "not_toml": "not TOML: {name}, {error}",
    "schema_no_fields": "schema has no fields: {path}",
    "schema_bad_kind": "schema field {field} has an unknown kind",
    "schema_no_order": "schema field {field} is a choice without order",
    "schema_bad_text_check": "schema field {field} has an unknown text_check",
    "bad_schema_version": "{name}: schema must be {version}",
    "one_role": "{name}: the file must have exactly one of [{org}] or [{repo}]",
    "missing_name": "{name}: {table}.{key} is missing or not text",
    "org_has_source": "{name}: an organization file has no [{table}]",
    "missing_source": "{name}: [{table}] is missing",
    "missing_source_key": "{name}: {table}.{key} is missing or not text",
    "repo_has_locks": "{name}: a repo contract has no [{table}]",
    "bad_locks": "{name}: {table}.{key} must be a list of text",
    "unknown_field": "{name}: unknown field {field}",
    "bad_value": "{name}: field {field}: {problem}",
    "lock_unknown": "{name}: lock names an unknown field {field}",
    "lock_no_value": "{name}: locked field without value: {field}",
    "not_repo": "{name}: not a repo contract",
    "not_org": "{name}: not an organization file",
    "changes_lock": "changes locked rule {field}: organization {org!r}, repo {repo!r}",
    "source_not_found": "source not found: {address}. Populate the cache: {git} clone {address} {dir}",
    "bad_address": "the source address cannot be a cache path: {address}",
    "git_not_found": "{git} not found on this computer",
    "version_not_found": "version not found: {version} of {file} in {address}. {detail}",
    "source_origin": "{address} version {version}",
    "check_pass": "{contract} obeys its organization source",
    "no_ids": "{path}: no rule identifiers found, expected [a.b] marks",
    "unknown_id": "{path}: identifier [{id}] has no value in the contract or its source",
    "pattern_hit": "{path}:{line}: matches a pattern of {field}",
    "instructions_pass": "{path} agrees with the contract ({count} identifiers, source: {origin})",
    "text_pass": "{path} contains none of the patterns (source: {origin})",
    "all_pass": "all contract checks of {contract} passed",
    "redacted": "redacted: {count} patterns",
    "not_a_file": "not a file: {path}",
    "not_utf8": "not UTF-8 text: {path}",
    "schema_not_table": "schema field {field} is not a table",
}

# ---------------------------------------------------------------------------
# Kinds. Each kind has its type check and its comparison, in one place.
# ---------------------------------------------------------------------------


def _is_text_or_list(value: object) -> bool:
    return isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))


def _is_whole_number(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


@dataclass(frozen=True)
class Kind:
    name: str
    expected: str                                   # message when a value does not fit
    accepts: Callable[[object, dict], bool]         # (value, field spec) -> fits the kind
    stricter: Callable[[object, object, dict], bool]  # (org value, repo value, spec) -> equal or stricter
    needs_order: bool = False


KINDS: dict[str, Kind] = {
    k.name: k for k in (
        Kind("flag", "expected true or false",
             lambda v, s: isinstance(v, bool),
             lambda org, repo, s: repo is True or org is False),
        Kind("limit", "expected a whole number of 0 or more",
             lambda v, s: _is_whole_number(v),
             lambda org, repo, s: repo == org),      # a locked limit is a policy: exact, not a bound
        Kind("count", "expected a whole number of 0 or more",
             lambda v, s: _is_whole_number(v),
             lambda org, repo, s: repo >= org),
        Kind("set", "expected a list of text",
             lambda v, s: isinstance(v, list) and all(isinstance(i, str) for i in v),
             lambda org, repo, s: set(org).issubset(set(repo))),
        Kind("choice", "expected one of the values in order",
             lambda v, s: v in s[ATTR_ORDER],
             lambda org, repo, s: s[ATTR_ORDER].index(repo) >= s[ATTR_ORDER].index(org),
             needs_order=True),
        Kind("text", "expected text or a list of text",
             lambda v, s: _is_text_or_list(v),
             lambda org, repo, s: repo == org),
    )
}


class CannotRun(Exception):
    """The check could not run. The message names the cause."""


def msg(message_id: str, **values: object) -> str:
    return MSG[message_id].format(**values)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_toml(path: Path) -> dict:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise CannotRun(msg("no_file", path=path))
    except IsADirectoryError:
        raise CannotRun(msg("not_a_file", path=path))
    except PermissionError:
        raise CannotRun(msg("access_denied", path=path))
    except UnicodeDecodeError:
        raise CannotRun(msg("not_utf8", path=path))
    except tomllib.TOMLDecodeError as e:
        raise CannotRun(msg("not_toml", name=path, error=e))


def parse_toml_text(text: str, name: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise CannotRun(msg("not_toml", name=name, error=e))


def load_schema(path: Path) -> dict:
    data = load_toml(path)
    fields = data.get(KEY_FIELDS)
    if not isinstance(fields, dict) or not fields:
        raise CannotRun(msg("schema_no_fields", path=path))
    for name, spec in fields.items():
        if not isinstance(spec, dict):
            raise CannotRun(msg("schema_not_table", field=name))
        kind = KINDS.get(spec.get(ATTR_KIND))
        if kind is None:
            raise CannotRun(msg("schema_bad_kind", field=name))
        if kind.needs_order and not spec.get(ATTR_ORDER):
            raise CannotRun(msg("schema_no_order", field=name))
        if ATTR_TEXT_CHECK in spec and spec[ATTR_TEXT_CHECK] not in TEXT_CHECKS:
            raise CannotRun(msg("schema_bad_text_check", field=name))
    return fields


# ---------------------------------------------------------------------------
# Field paths
# ---------------------------------------------------------------------------


def flatten(table: dict, prefix: str = "") -> dict[str, object]:
    """Turn nested tables into {"a.b.c": value}."""
    out: dict[str, object] = {}
    for key, value in table.items():
        path = f"{prefix}{PATH_SEPARATOR}{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def match_field(path: str, fields: dict) -> str | None:
    """Return the schema pattern that matches a concrete field path, else None."""
    if path in fields:
        return path
    parts = path.split(PATH_SEPARATOR)
    for pattern in fields:
        pp = pattern.split(PATH_SEPARATOR)
        if len(pp) == len(parts) and all(a == b or a == WILDCARD for a, b in zip(pp, parts)):
            return pattern
    return None


def spec_of(path: str, fields: dict) -> dict:
    return fields[match_field(path, fields)]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class Validated:
    role: str
    values: dict[str, object]
    locks: list[str]
    errors: list[str]


def _text_table(data: dict, table: str, name: str, errors: list[str]) -> None:
    """The table must exist and have a text name."""
    if not isinstance(data[table].get(KEY_NAME), str):
        errors.append(msg("missing_name", name=name, table=table, key=KEY_NAME))


def validate(data: dict, fields: dict, name: str) -> Validated:
    errors: list[str] = []
    if data.get(TABLE_SCHEMA) != SCHEMA_VERSION:
        errors.append(msg("bad_schema_version", name=name, version=SCHEMA_VERSION))

    has_org = isinstance(data.get(TABLE_ORGANIZATION), dict)
    has_repo = isinstance(data.get(TABLE_REPO), dict)
    if has_org == has_repo:
        errors.append(msg("one_role", name=name, org=TABLE_ORGANIZATION, repo=TABLE_REPO))
        role = ROLE_UNKNOWN
    else:
        role = ROLE_ORGANIZATION if has_org else ROLE_REPO

    if role == ROLE_ORGANIZATION:
        _text_table(data, TABLE_ORGANIZATION, name, errors)
        if TABLE_SOURCE in data:
            errors.append(msg("org_has_source", name=name, table=TABLE_SOURCE))
    if role == ROLE_REPO:
        _text_table(data, TABLE_REPO, name, errors)
        source = data.get(TABLE_SOURCE)
        if not isinstance(source, dict):
            errors.append(msg("missing_source", name=name, table=TABLE_SOURCE))
        else:
            for key in SOURCE_KEYS:
                if not isinstance(source.get(key), str) or not source[key]:
                    errors.append(msg("missing_source_key", name=name, table=TABLE_SOURCE, key=key))
        if TABLE_LOCKS in data:
            errors.append(msg("repo_has_locks", name=name, table=TABLE_LOCKS))

    locks: list[str] = []
    if role == ROLE_ORGANIZATION and TABLE_LOCKS in data:
        raw = data[TABLE_LOCKS].get(KEY_FIELDS) if isinstance(data[TABLE_LOCKS], dict) else None
        if not isinstance(raw, list) or not all(isinstance(v, str) for v in raw):
            errors.append(msg("bad_locks", name=name, table=TABLE_LOCKS, key=KEY_FIELDS))
        else:
            locks = raw

    values: dict[str, object] = {}
    body = {k: v for k, v in data.items() if k not in RESERVED_TABLES}
    for path, value in flatten(body).items():
        pattern = match_field(path, fields)
        if pattern is None:
            errors.append(msg("unknown_field", name=name, field=path))
            continue
        spec = fields[pattern]
        kind = KINDS[spec[ATTR_KIND]]
        if not kind.accepts(value, spec):
            errors.append(msg("bad_value", name=name, field=path, problem=kind.expected))
            continue
        values[path] = value

    for lock in locks:
        if match_field(lock, fields) is None:
            errors.append(msg("lock_unknown", name=name, field=lock))
        elif lock not in values:
            errors.append(msg("lock_no_value", name=name, field=lock))
    return Validated(role, values, locks, errors)


# ---------------------------------------------------------------------------
# The organization source
# ---------------------------------------------------------------------------


def cache_path(address: str, cache_dir: Path) -> Path:
    """The clone of a source inside the cache: <cache>/<host>/<owner>/<repo>."""
    stripped = re.sub(r"^[a-z]+://", "", address).rstrip("/")
    stripped = re.sub(r"\.git$", "", stripped)
    parts = [p for p in stripped.split("/") if p]
    if not parts or any(p in ("..", ".") for p in parts):
        raise CannotRun(msg("bad_address", address=address))
    return cache_dir.joinpath(*parts)


def resolve_source(source: dict, explicit: Path | None, cache_dir: Path) -> tuple[dict, str]:
    """Return the organization data and a description of where it came from."""
    if explicit is not None:
        return load_toml(explicit), str(explicit)
    address, file, version = (source[k] for k in SOURCE_KEYS)
    repo_dir = cache_path(address, cache_dir)
    if not repo_dir.is_dir():
        raise CannotRun(msg("source_not_found", address=address, git=GIT, dir=repo_dir))
    try:
        result = subprocess.run(
            [GIT, GIT_OPTION_DIR, str(repo_dir), GIT_SHOW, f"{version}:{file}"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        raise CannotRun(msg("git_not_found", git=GIT))
    except PermissionError:
        raise CannotRun(msg("access_denied", path=repo_dir))
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
        raise CannotRun(msg("version_not_found", version=version, file=file, address=address, detail=detail))
    origin = msg("source_origin", address=address, version=version)
    return parse_toml_text(result.stdout, origin), origin


# ---------------------------------------------------------------------------
# The effective contract
# ---------------------------------------------------------------------------


@dataclass
class Effective:
    values: dict[str, object]       # the organization values, overridden by the repo values
    fields: dict
    failures: list[str]
    origin: str
    repo_values: dict[str, object] = None   # the repo values alone, in declaration order


def effective_contract(contract: Path, schema: Path, source: Path | None, cache_dir: Path) -> Effective:
    fields = load_schema(schema)
    repo_data = load_toml(contract)
    repo = validate(repo_data, fields, str(contract))
    if repo.role != ROLE_REPO:
        repo.errors.append(msg("not_repo", name=contract))
    if repo.errors:
        return Effective({}, fields, repo.errors, "", {})
    org_data, origin = resolve_source(repo_data[TABLE_SOURCE], source, cache_dir)
    org = validate(org_data, fields, origin)
    if org.role != ROLE_ORGANIZATION:
        org.errors.append(msg("not_org", name=origin))
    if org.errors:
        return Effective({}, fields, org.errors, origin, {})
    failures = [
        msg("changes_lock", field=path, org=org.values[path], repo=value)
        for path, value in repo.values.items()
        if path in org.locks and not KINDS[spec_of(path, fields)[ATTR_KIND]].stricter(org.values[path], value, spec_of(path, fields))
    ]
    return Effective({**org.values, **repo.values}, fields, failures, origin, dict(repo.values))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def emit(prefix: str, text: str) -> None:
    print(f"{prefix}: {text}")


def report_failures(failures: list[str]) -> int:
    for f in failures:
        emit(OUT_FAIL, f)
    return FAIL if failures else PASS


def cmd_validate(args) -> int:
    result = validate(load_toml(args.file), load_schema(args.schema), str(args.file))
    if report_failures(result.errors) == FAIL:
        return FAIL
    emit(OUT_VALID, f"{args.file} ({result.role})")
    return PASS


def redacted(e: Effective) -> dict[str, object]:
    """The effective values, with the text-checked sets replaced: they can be private."""
    out: dict[str, object] = {}
    for path, value in e.values.items():
        if ATTR_TEXT_CHECK in spec_of(path, e.fields) and isinstance(value, list):
            out[path] = msg("redacted", count=len(value))
        else:
            out[path] = value
    return out


def cmd_check(args) -> int:
    e = effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if args.json:
        print(json.dumps({OUT_SOURCE: e.origin, JSON_KEY_FAILURES: e.failures, JSON_KEY_EFFECTIVE: redacted(e)},
                         indent=2, sort_keys=True))
        return FAIL if e.failures else PASS
    if e.origin:
        emit(OUT_SOURCE, e.origin)
    if report_failures(e.failures) == FAIL:
        return FAIL
    emit(OUT_PASS, msg("check_pass", contract=args.contract))
    return PASS


def text_patterns(e: Effective) -> list[tuple[str, list[str], bool]]:
    """The pattern sets that text must not contain: (field, patterns, ignore case)."""
    out = []
    for path, value in e.values.items():
        spec = spec_of(path, e.fields)
        if ATTR_TEXT_CHECK in spec and isinstance(value, list):
            out.append((path, value, spec[ATTR_TEXT_CHECK] == TEXT_CHECK_IGNORE_CASE))
    return out


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CannotRun(msg("no_file", path=path))
    except IsADirectoryError:
        raise CannotRun(msg("not_a_file", path=path))
    except PermissionError:
        raise CannotRun(msg("access_denied", path=path))
    except UnicodeDecodeError:
        raise CannotRun(msg("not_utf8", path=path))


def pattern_hits(e: Effective, path: Path, text: str) -> list[str]:
    """Lines of the text that contain a pattern of a text-checked set."""
    problems: list[str] = []
    lines = text.splitlines()
    for field, patterns, ignore_case in text_patterns(e):
        for pattern in patterns:
            needle = pattern.lower() if ignore_case else pattern
            for number, line in enumerate(lines, start=1):
                haystack = line.lower() if ignore_case else line
                if needle and needle in haystack:
                    problems.append(msg("pattern_hit", path=path, line=number, field=field))
    return problems


def cmd_instructions(args) -> int:
    e = effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if report_failures(e.failures) == FAIL:
        return FAIL
    text = read_text(args.file)
    ids = identifiers(text, e)
    if report_failures(instructions_problems(e, args.file)) == FAIL:
        return FAIL
    emit(OUT_PASS, msg("instructions_pass", path=args.file, count=len(ids), origin=e.origin))
    return PASS


def cmd_text(args) -> int:
    e = effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if report_failures(e.failures) == FAIL:
        return FAIL
    if report_failures(pattern_hits(e, args.file, read_text(args.file))) == FAIL:
        return FAIL
    emit(OUT_PASS, msg("text_pass", path=args.file, origin=e.origin))
    return PASS


def identifiers(text: str, e: Effective) -> set[str]:
    """The rule identifiers of a text: a bracketed path whose first segment is a group of the schema.
    A bracketed file name is not an identifier."""
    groups = {pattern.split(PATH_SEPARATOR)[0] for pattern in e.fields}
    return {i for i in ID_PATTERN.findall(text)
            if i.split(PATH_SEPARATOR)[0] in groups and not i.endswith(FILE_SUFFIXES)}


def instructions_problems(e: Effective, path: Path) -> list[str]:
    """The faults of an instruction file: unknown identifiers, no identifiers, pattern hits."""
    text = read_text(path)
    problems: list[str] = []
    ids = identifiers(text, e)
    if not ids:
        problems.append(msg("no_ids", path=path))
    problems += [msg("unknown_id", path=path, id=i) for i in sorted(ids) if i not in e.values]
    return problems + pattern_hits(e, path, text)


def cmd_all(args) -> int:
    e = effective_contract(args.contract, args.schema, args.source, args.cache_dir)
    if e.origin:
        emit(OUT_SOURCE, e.origin)
    problems = list(e.failures)
    if not problems:
        root = args.contract.resolve().parent
        instructions = e.values.get(FIELD_INSTRUCTIONS_FILE)
        if instructions:
            problems += instructions_problems(e, root / instructions)
        for name in e.values.get(FIELD_TEXT_CHECKED, []) or []:
            path = root / name
            problems += pattern_hits(e, path, read_text(path))
    if report_failures(problems) == FAIL:
        return FAIL
    emit(OUT_PASS, msg("all_pass", contract=args.contract))
    return PASS


def cmd_source(args) -> int:
    """For a step that populates the cache: address, file, version, and the cache path, one per line."""
    fields = load_schema(args.schema)
    data = load_toml(args.contract)
    repo = validate(data, fields, str(args.contract))
    if repo.role != ROLE_REPO:
        repo.errors.append(msg("not_repo", name=args.contract))
    if report_failures(repo.errors) == FAIL:
        return FAIL
    source = data[TABLE_SOURCE]
    for key in SOURCE_KEYS:
        print(source[key])
    print(cache_path(source[SOURCE_KEYS[0]], args.cache_dir))
    return PASS


def main(argv: list[str] | None = None) -> int:
    default_cache = Path(os.environ.get(ENV_CACHE_DIR, DEFAULT_CACHE_DIR))
    parser = argparse.ArgumentParser(prog="charter_check", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(f"--{ARG_SCHEMA}", type=Path, default=DEFAULT_SCHEMA)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser(CMD_VALIDATE, help="validate one file")
    p.add_argument(ARG_FILE, type=Path)

    p = sub.add_parser(CMD_CHECK, help="check a repo contract against its organization source")
    p.add_argument(ARG_CONTRACT, type=Path)
    p.add_argument(f"--{ARG_SOURCE}", type=Path, default=None)
    p.add_argument(f"--{ARG_CACHE_DIR.replace('_', '-')}", dest=ARG_CACHE_DIR, type=Path, default=default_cache)
    p.add_argument(f"--{ARG_JSON}", action="store_true")

    for command, help_text in ((CMD_INSTRUCTIONS, "check an instruction file against the contract"),
                               (CMD_TEXT, "check any text file against the pattern sets of the contract")):
        p = sub.add_parser(command, help=help_text)
        p.add_argument(ARG_FILE, type=Path)
        p.add_argument(f"--{ARG_CONTRACT}", type=Path, required=True)
        p.add_argument(f"--{ARG_SOURCE}", type=Path, default=None)
        p.add_argument(f"--{ARG_CACHE_DIR.replace('_', '-')}", dest=ARG_CACHE_DIR, type=Path, default=default_cache)

    p = sub.add_parser(CMD_ALL, help="run all contract checks on the declared files")
    p.add_argument(ARG_CONTRACT, type=Path)
    p.add_argument(f"--{ARG_SOURCE}", type=Path, default=None)
    p.add_argument(f"--{ARG_CACHE_DIR.replace('_', '-')}", dest=ARG_CACHE_DIR, type=Path, default=default_cache)

    p = sub.add_parser(CMD_SOURCE, help="print the source of a repo contract and its cache path")
    p.add_argument(ARG_CONTRACT, type=Path)
    p.add_argument(f"--{ARG_CACHE_DIR.replace('_', '-')}", dest=ARG_CACHE_DIR, type=Path, default=default_cache)

    args = parser.parse_args(argv)
    commands = {CMD_VALIDATE: cmd_validate, CMD_CHECK: cmd_check, CMD_INSTRUCTIONS: cmd_instructions,
                CMD_TEXT: cmd_text, CMD_SOURCE: cmd_source, CMD_ALL: cmd_all}
    try:
        return commands[args.command](args)
    except CannotRun as e:
        emit(OUT_CANNOT_RUN, str(e))
        return CANNOT_RUN


if __name__ == "__main__":
    sys.exit(main())
