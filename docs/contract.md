# The contract files

Charter uses three files. The schema belongs to Charter. The other two belong to the organization and
to the repo.

| File | Owner | Location | Content |
|---|---|---|---|
| `schema/contract.toml` | Charter | This repo | The fields, their kinds, and their directions |
| `organization.toml` | The organization | A source outside every repo, for example a private repo | The rules of the organization, and which of them are locked |
| `charter.toml` | The repo | The root of the repo | A reference to the source, and the rules of the repo |

A repo holds no copy of the organization file. The checker reads the source from a cache outside the
repo, or from a path that CI gives with `--source`. The cache is a git clone at
`~/.charter/cache/<host>/<owner>/<repo>`; the checker names the clone command when the cache is
missing. The environment variable `CHARTER_CACHE_DIR` moves the cache.

## Kinds and directions

A lower owner can make a rule stricter. It cannot weaken a locked rule. The kind of a field says what
"stricter" means.

| Kind | Type | Stricter |
|---|---|---|
| `flag` | true or false | true |
| `limit` | whole number | smaller |
| `count` | whole number | larger |
| `set` | list of text | a superset |
| `choice` | one value of an ordered list | a later value |
| `text` | text, or a list of text | no direction; a locked text stays equal |

A `set` field can carry `text_check = "exact"` or `"ignore_case"`. Then a text file must not contain
any of its patterns. The `instructions` and `text` commands read this from the schema.

## Fields

| Field | Kind | Meaning |
|---|---|---|
| `text.private_material_patterns` | set | Patterns of private material that must not appear in text |
| `text.session_link_patterns` | set | Patterns of a session link |
| `text.project_name_patterns` | set | Names of other projects, kept in the private source |
| `change.person_approves_contract` | flag | A person approves each change to a contract |
| `change.author_not_reviewer` | flag | The author of a change is not its reviewer |
| `change.ticket_per_change` | flag | Each change to a source file has a ticket |
| `limits.acceptance_loop` | limit | Runs of the acceptance checks before the agent stops |
| `limits.review_loop` | limit | Rounds between author and reviewer before a person decides |
| `limits.refusals` | limit | Refusals in sequence before the agent stops |
| `tiers.<tier>.paths` | set | Path patterns of the files in the tier |
| `tiers.<tier>.review` | choice | `light` or `deep` |
| `tiers.<tier>.approver` | choice | `agent`, `engineer`, `team_lead`, or `leader` |
| `tiers.<tier>.approvals` | count | Approvals that a merge needs |
| `documents.necessary` | set | Documents that the repo keeps current |
| `documents.code_paths` | set | Paths whose change needs a document change or a recorded reason |
| `documents.text_checked` | set | Files that must contain none of the text-checked patterns |
| `instructions.file` | text | The instruction file of the repo |
| `checks.quality` | set | Commands that must pass before a push. They run on the code of the change. |
| `tools.issue_tracker`, `tools.code_host`, `tools.ci` | text | The tools of the repo |
| `roles.leader`, `roles.team_lead`, `roles.engineer`, `roles.agent` | text | Who holds a role |
| `lifecycle.<phase>.work` | text | What does the work in a phase |
| `lifecycle.<phase>.builtin` | text | Built-in abilities of the runtime that the phase uses |

## Reserved tables

| Table | In which file | Content |
|---|---|---|
| `schema = 1` | both | The schema version |
| `[organization] name` | organization | The name of the organization |
| `[locks] fields` | organization | The locked fields. Each must have a value in the file. |
| `[repo] name` | repo | The name of the repo |
| `[source] address, file, version` | repo | The organization source and its version |

## The terms of the product document

| Term in `docs/product.md` | Where it is in the files |
|---|---|
| Contract | `charter.toml` and `organization.toml` |
| Gate | `checks.quality`, `documents.code_paths`, and the scripts that read them |
| Acceptance check | The issue in the tracker. Not a field: it belongs to one work item. |
| Risk tier | `tiers.<tier>.*` |
| Evidence record | The output of the checker, and later the record on the change request |
| Stop rules | `limits.*` |
| Owner of a rule | The file that holds it, and `[locks]` |
| Lifecycle map | `lifecycle.<phase>.*` |

## The gates

`scripts/charter_gate.py` checks one change. It reads the contract, and the facts of the change request
from one JSON file. A collecting step writes that file on the code host; the gates know no code host.

```
python3 scripts/charter_gate.py link      --facts facts.json
python3 scripts/charter_gate.py documents --facts facts.json --contract charter.toml
python3 scripts/charter_gate.py quality   --contract charter.toml
python3 scripts/charter_gate.py verdict   --facts facts.json --contract charter.toml [--json]
```

| Gate | Passes when |
|---|---|
| `link` | The change request references an open issue. |
| `documents` | No file under `documents.code_paths` changed; or a document in `documents.necessary` changed; or the change request records a reason. |
| `quality` | Each command in `checks.quality` exits with 0. |
| `verdict` | `link` and `documents` pass, all reported checks passed, no review thread is unresolved, and a tier matches the changed files. The first line of the output is `ready` or `not ready`; the reasons follow. The verdict names the tier and who merges. |

The facts file:

```json
{
  "change_request": 23,
  "linked_issues": [{"number": 22, "state": "open"}],
  "changed_files": ["docs/product.md"],
  "reason_for_no_document_change": null,
  "unresolved_review_threads": 0,
  "approvals": ["login"],
  "checks": {"tests": "pass"}
}
```

A change request records a reason for a missing document change with one line in its text:
`No document change: <reason>`. The collecting step copies it into the facts file.

Three rules of the gates:

- **Path patterns.** `*` and `?` stay inside one path segment. `**` crosses segments. `src/*` matches
  `src/x.py` and not `src/a/b.py`; `scripts/**` matches both. The first tier of the repo contract that
  matches a changed file is the tier of the change.
- **Quality commands** run without a shell. A command with an unquoted operator such as `&&` or `|`,
  a variable, or a substitution is refused with a message: put it in a script. The output of a failed
  command is shown.
- **Approvals** are not checked in this version. The merge by the approver of the tier is the approval,
  and the verdict says so. The field `approvals` of the facts file is optional.

## On the code host

Two workflows run on each change request of this repo. They and the collecting script
`scripts/charter_facts_github.py` are the only parts that are specific to GitHub.

| Workflow | Trust | What it does |
|---|---|---|
| `tests` | Runs the code of the change request. It gets no secret. | Runs the quality checks of the contract with `--repo-only`. |
| `verdict` | Runs from the main branch, with the scripts of the main branch. It never runs the code of the change request. | Reads the files of the change request as data, fetches the organization source from the address in main, runs the contract checks on those files, collects the facts, runs the verdict, and publishes the check "verdict" on the change request. |

The ruleset on `main` demands the check "verdict". The workflow `verdict` starts when `tests`
completes, and it can also start by hand for one change request. When a reviewer resolves the last
review thread, run it by hand, or push a commit: a resolved thread starts no run.

The secret `CHARTER_ORG_TOKEN` is a fine-grained token with read access to the organization source
only. Only the workflow `verdict` holds it. The address of the source comes from the contract in main,
so a change request cannot send the token elsewhere. A change request that changes the source is a
contract change: a person reviews it, and the new source applies after the merge.

## The evidence record

Each run of the verdict writes the evidence record of the change: the JSON form of the verdict, with
the fields below. On GitHub, one comment on the change request carries it, updated on each run and
marked with `<!-- charter-record -->`. The check "verdict" keeps the short text.

| Field | Content |
|---|---|
| `record_form` | The version of this form: 1 |
| `change_request` | The number of the change request |
| `time` | When the record was made, UTC |
| `scripts_version` | The commit of the scripts that made the record |
| `verdict`, `reasons` | `ready` or `not ready`, and the reasons |
| `source` | The organization source and its version |
| `tier`, `approver`, `merges` | The tier of the change, the role that merges, and who holds it |
| `gates` | Each gate with its result and its reasons |
| `checks` | The state of each check |
| `false_failures` | What a person recorded with a line `False failure: <gate>: <reason>` in the change request |
| `dropped_findings` | Empty until the agent reviewer comes |

`charter_facts_github.py records --repo owner/name --last N` prints the records of the last merged
change requests, one line each, for a sample review.

## The checker

```
python3 scripts/charter_check.py validate FILE
python3 scripts/charter_check.py check charter.toml [--source PATH] [--json]
python3 scripts/charter_check.py instructions AGENTS.md --contract charter.toml
python3 scripts/charter_check.py text README.md --contract charter.toml
python3 scripts/charter_check.py source charter.toml
python3 scripts/charter_check.py all charter.toml
```

`all` runs `check`, then `instructions` on `instructions.file`, then `text` on each file in
`documents.text_checked`, relative to the contract. It is the one command for the contract checks.

Exit codes: 0 pass, 1 fail, 2 the check could not run. With exit code 2 the message names the cause:
no file, not a file, not UTF-8 text, not TOML, source not found, access denied, version not found.

`check --json` prints one JSON object: the source, the failures, and the effective contract. The
pattern sets with a `text_check` are redacted in that output, because they can be private.
