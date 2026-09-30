# The contract files

Charter uses three files. The schema belongs to Charter. The other two belong to the organization and
to the repo.

| File | Owner | Location | Content |
|---|---|---|---|
| `schema/contract.toml` | Charter | This repo | The fields, their kinds, and their directions |
| `organization.toml` | The organization | A source outside every repo, for example a private repo | The rules of the organization, and which of them are locked |
| `charter.toml` | The repo | The root of the repo | A reference to the source, and the rules of the repo |

A repo holds no copy of the organization file. The checker reads the source from a cache outside the
repo (`~/.charter/cache/<host>/<owner>/<repo>`, a git clone), or from a path that CI gives.

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
| `checks.quality` | set | Commands that must pass before a push |
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

## The checker

```
python3 scripts/charter_check.py validate FILE
python3 scripts/charter_check.py check charter.toml [--source PATH] [--json]
python3 scripts/charter_check.py instructions AGENTS.md --contract charter.toml
```

Exit codes: 0 pass, 1 fail, 2 the check could not run. With exit code 2 the message names the cause:
no file, not TOML, source not found, access denied, version not found.
