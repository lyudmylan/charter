# The contract files

Charter uses three files. The schema belongs to Charter. The other two belong to the organization and
to the repo.

| File | Owner | Location | Content |
|---|---|---|---|
| `charter/schema/contract.toml` | Charter | This repo | The fields, their kinds, and their directions |
| `organization.toml` | The organization | A source outside every repo, for example a private repo | The rules of the organization, and which of them are locked |
| `charter.toml` | The repo | The root of the repo | A reference to the source, and the rules of the repo |

A repo holds no copy of the organization file. The checker reads the source from a cache outside the
repo, or from a path that CI gives with `--source`. The cache is a git clone at
`~/.charter/cache/<host>/<owner>/<repo>`; the checker names the clone command when the cache is
missing. The environment variable `CHARTER_CACHE_DIR` moves the cache.

## Kinds and directions

A lower owner can make a rule stricter. It cannot weaken a locked rule. The kind of a field says what
"stricter" means. Two kinds have no direction: a locked limit and a locked text stay equal.

| Kind | Type | Stricter |
|---|---|---|
| `flag` | true or false | true |
| `limit` | whole number | no direction; a locked limit stays equal: the number is a policy of its owner |
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
| `review.threshold` | choice | `blocker`, `high`, `medium`, or `low`: the lowest severity of a finding that keeps the review loop open. Without a value: `medium` |
| `review.code_blocks` | flag | An open finding of the reviewer of the code makes the change request not ready. Without it, or with `false`: the shadow period, the verdict prints the state of the code review and blocks nothing. Needs the version 0.3.10 of the core |
| `build.plan_before_code` | flag | Each work item has its plan, `plans/<part>.md`, before the code; the verdict checks that it exists |
| `tiers.<tier>.paths` | set | Path patterns of the files in the tier |
| `tiers.<tier>.review` | choice | `light` or `deep` |
| `tiers.<tier>.approver` | choice | `agent`, `engineer`, `team_lead`, or `leader`: the role that merges a change of the tier. With `agent`, the verdict merges, under the conditions of the section "The merge by the verdict". Needs the version 0.3.11 of the core for `agent` |
| `tiers.<tier>.approvals` | count | Approvals that a merge needs |
| `documents.necessary` | set | Documents that the repo keeps current |
| `documents.code_paths` | set | Paths whose change needs a document change or a recorded reason |
| `documents.text_checked` | set | Files that must contain none of the text-checked patterns |
| `documents.absent` | set | Path patterns that the repo must not hold: the contract checks fail when a file is under one of them. The setup step writes the folders of decision files. Needs the version 0.3.5 of the core |
| `instructions.file` | text | The instruction file of the repo |
| `boundary.no_write` | set | Path patterns that a run of an agent without a person never changes, adds, or deletes. The plan of a work item passes. Needs the version 0.3.6 of the core |
| `boundary.no_read` | set | Path patterns that a run without a person never reads. Needs the version 0.3.6 of the core |
| `checks.quality` | set | Commands that must pass before a push. They run on the code of the change. |
| `charter.version` | text | The version of the core plugin of Charter that the repo uses; the workflows fetch Charter at the tag `charter--v<version>` |
| `tools.issue_tracker`, `tools.code_host`, `tools.ci` | text | The tools of the repo |
| `roles.leader`, `roles.team_lead`, `roles.engineer`, `roles.agent` | text | Who holds a role |
| `lifecycle.<phase>.work` | text | What does the work in a phase |
| `lifecycle.<phase>.builtin` | text | Built-in abilities of the runtime that the phase uses. The template `charter/templates/charter.toml` is the one list of them, for the six phases |

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
| Stop rules | `limits.*`, and `review.threshold` for the review loop |
| Owner of a rule | The file that holds it, and `[locks]` |
| Lifecycle map | `lifecycle.<phase>.*` |

## The gates

`charter/scripts/charter_gate.py` checks one change. It reads the contract, and the facts of the change request
from one JSON file. A collecting step writes that file on the code host; the gates know no code host.

```
python3 charter/scripts/charter_gate.py link      --facts facts.json
python3 charter/scripts/charter_gate.py documents --facts facts.json --contract charter.toml
python3 charter/scripts/charter_gate.py quality   --contract charter.toml
python3 charter/scripts/charter_gate.py verdict   --facts facts.json --contract charter.toml [--json]
```

| Gate | Passes when |
|---|---|
| `link` | The change request links an open issue with a closing keyword of the code host followed by the number: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves` or `resolved`, in any case, with or without a colon, then `#N` (`Closes #N`); or `Part of #N`, which links the issue without closing it, the form of a change request of the Plan phase, the intent alone. A bare `#N` in the text is a mention, not a link. |
| `documents` | No file under `documents.code_paths` changed; or a document in `documents.necessary` changed; or the change request records a reason. |
| `quality` | Each command in `checks.quality` exits with 0. |
| `verdict` | `link` and `documents` pass, all reported checks passed, no review thread is unresolved, a tier matches the changed files, and, when the contract sets `build.plan_before_code`, the plan of each intent that a linked issue names exists at the head commit (a change of intents alone needs no plan; an intent that the change request removes or renames away needs no plan). The first line of the output is `ready` or `not ready`; the reasons follow. The verdict names the tier and who merges, and prints one line `merge: ...`: the verdict merges, or a person merges and why. |

The facts file:

```json
{
  "change_request": 23,
  "linked_issues": [{"number": 22, "state": "open"}],
  "changed_files": ["docs/product.md"],
  "reason_for_no_document_change": null,
  "unresolved_review_threads": 0,
  "approvals": ["login"],
  "checks": {"tests": "pass"},
  "review_reports": ["medium", "low"],
  "review_rounds": 2,
  "review_highest_severity": "low",
  "intents": [{"path": "intents/app.md", "plan": true, "removed": false}]
}
```

A change request records a reason for a missing document change with one line in its text:
`No document change: <reason>`. The collecting step copies it into the facts file. The three review
fields are optional: the collecting step writes them when it is given the reviewer workflow. The verdict
counts the round from `review_reports`; a facts file without it, from an older collector, gives the round
in `review_rounds`. The field
`intents` lists the intents that the linked issues name with a line `Intent: intents/<part>.md`, and
whether the plan `plans/<part>.md` of each exists at the head commit. A plan at the old place,
`intents/<part>.plan.md`, counts too. The linked issues are those that the text of the change request
closes with a keyword or names with `Part of #N`; an issue that the text only mentions is not linked, so
the verdict does not ask for its plan.

The plan lives in `plans/`, outside `intents/` (decision D18): a change request with code and its plan
takes the tier of its code, because the high tier holds `intents/**` and not `plans/**`. A repo moves each
plan with `git mv intents/<part>.plan.md plans/<part>.md`. A plan at the old place stays in the high tier.

Three rules of the gates:

- **Path patterns.** `*` and `?` stay inside one path segment. `**` crosses segments. `src/*` matches
  `src/x.py` and not `src/a/b.py`; `scripts/**` matches both. The first tier of the repo contract that
  matches a changed file is the tier of the change.
- **Quality commands** run without a shell. A command with an unquoted operator such as `&&` or `|`,
  a variable, or a substitution is refused with a message: put it in a script. The output of a failed
  command is shown.
- **Approvals** are not checked in this version. The merge by the approver of the tier is the approval,
  and the verdict says so. The field `approvals` of the facts file is optional.

## The boundary of a run

A run of an agent with no person present works inside the boundary of the contract. Two parts enforce it.

```
python3 charter/scripts/charter_check.py boundary charter.toml > settings.json
python3 charter/scripts/charter_gate.py boundary --contract charter.toml --changed changed.txt
```

`charter-check boundary` prints the settings of Claude Code for the run, as JSON. The workflow of the run
writes them at the start of each run and passes them on the command line; they are not a file of the repo.
They turn the sandbox of the shell on, let no command run outside it, and stop the run when the sandbox
cannot start. The shell has no network. The tokens of the model and of the code host leave the
environment of each shell command. A call that would need a question to a person is refused. Each pattern
of `boundary.no_write` is a deny rule for the edit tools and a write denial of the sandbox; each pattern
of `boundary.no_read` is a deny rule for the read tool and a read denial of the sandbox. Each path is
absolute, from the folder of the contract, so the settings are for one checkout.

One limit comes from Claude Code. On Linux the write lists of the sandbox honour a wildcard only as a
trailing `/**`, so another pattern enters the sandbox as the files that match it at that time. A new file
is then not closed by the sandbox. The gate catches it. A pattern has no exception: `intents/**` is one
folder entry in both layers, and the plan of a work item, `plans/<part>.md`, is under no pattern.

`charter-gate boundary` reads the paths that a run changed: each added, changed, or deleted path, and
both names of a rename. The list has one of two forms. With a NUL character between the paths, as git
writes them with `-z`, each name is read as it is; the workflow of a run writes this form. Else the list
has one path on each line, and a line in the quotes of git fails, because git quotes a path with a
special character and the gate cannot read it. It fails when a path is under a pattern of `boundary.no_write`,
and it names the path. A path with dot segments is read as the path it points to, and a path that leaves
the repo fails. The plan of a work item, `plans/<part>.md`, passes, and each file under `intents/` fails.
The gate runs between the run and the push: a failure publishes nothing.

## On the code host

Two workflows run on each change request of this repo. They and the collecting script
`charter/scripts/charter_facts_github.py` are the only parts that are specific to GitHub.

| Workflow | Trust | What it does |
|---|---|---|
| `tests` | Runs the code of the change request. It gets no secret. | Runs the quality checks of the contract with `--repo-only`. |
| `verdict` | Runs from the main branch, with the scripts of the main branch. It never runs the code of the change request. | Reads the files of the change request as data, fetches the organization source from the address in main, runs the contract checks on those files with the schema of the change request (a data file, so that a change request can add a field and use it), collects the facts, runs the verdict, and publishes the check "verdict" on the change request, also when the verdict could not run: the check then says so, and the log of the job holds the cause. |

The ruleset on `main` demands the check "verdict". The workflow `verdict` starts when `tests`,
`review-intents`, or `review-code` completes, so that the record carries the last round of the review, and it can also
start by hand for one change request. When a reviewer resolves the last
review thread, run it by hand, or push a commit: a resolved thread starts no run.

The secret `CHARTER_ORG_TOKEN` is a fine-grained token with read access to the organization source
only. Only the workflow `verdict` holds it. The address of the source comes from the contract in main,
so a change request cannot send the token elsewhere. A change request that changes the source is a
contract change: a person reviews it, and the new source applies after the merge.

## The intent reviewer

The workflow `.github/workflows/review-intents.yml` runs on each change request that changes `intents/**` or `plans/**`.
An agent that is not the author follows the skill `charter-practices/skills/intent-review/SKILL.md` and
posts one comment: a table with one row per intent, and the findings. Shadow mode: it approves nothing and
blocks nothing; a person merges. It runs with a token of the owner's subscription, the secret
`CLAUDE_CODE_OAUTH_TOKEN`, and with read-only tools plus the comment commands. A change request from a
fork gets no secret and no review.

A reading that an agent drafts for a person, such as the error analysis of an eval round, is reviewed
before the person reads it (decision C11): the skill `charter-practices/skills/evidence-review/SKILL.md`
runs two passes by fresh agents in the session of the author, and puts the disagreements, with the
evidence on each side, in the text of the change request under `## Disagreements`.

### The review loop

Each finding carries a severity: `blocker`, `high`, `medium`, or `low`; the report ends with the line
`Highest open severity: <level>`. The author answers each finding at `review.threshold` or above: a
correction, or a line `Dropped finding: <reason>` in the change request, which closes the finding for the
next round. The skill `charter-practices/skills/review-loop/SKILL.md` is the author side of the loop, for
the agent in the session of the author.

The loop ends when the highest open severity is below the threshold, or when the rounds reach
`limits.review_loop`; then a person decides, with the merge. A round is a report of the reviewer in the
current loop. A loop starts with the first report, and again with the first report after one whose highest
open severity is below the threshold; a report without a severity line counts as open. Each report stays
on the change request as its own comment: the reviewer posts a new comment at each run and changes no
earlier one. Each report names the head commit that it covers, in a line `Commit: <identifier>`. A run
that ends without a new report that names the head commit fails, is no round, and prints the denied
commands of the agent in its log. The collecting step reads the severity line of each report, and the verdict
prints `review loop: round <n> of <limit>, highest open severity <level>: ...`. In shadow mode, this line
changes no verdict.

## The reviewer of the code

The workflow `.github/workflows/review-code.yml` runs on each change request that changes a file outside
`intents/` and `plans/`; a change of those two folders alone needs no review of the code. An agent that is
not the author follows the skill `charter-practices/skills/change-review/SKILL.md`: it reads the diff, the
intent and the plan of the linked issue, and the results of the checks, and posts a new comment at each
run. The report begins with `<!-- charter-code-review -->`, holds the line `Commit: <identifier>`, and ends
with `Highest open severity: <level>`. The reviewer reads files and runs no code of the change request; the
workflow `tests` runs the tests. It has the same secrets, the same tools, the same last step, and the same
rules of the loop as the intent reviewer: the lines `Dropped finding: <reason>` and `False finding: <reason>`
close its findings too. A change request from a fork gets no secret and no review.

The depth of the review follows `tiers.<tier>.review` of the tier of the change, read from the contract of
the base branch: `light`, the changed lines and their tests; `deep`, also the code that calls them and the
security of the change. The workflow reads it with
`charter-gate tier --contract charter.toml --changed FILE [--repo-only]`, which prints the name of the tier
and the depth, one on each line, and fails when no tier matches.

The collecting step, given `--code-review-workflow review-code.yml`, writes `code_review_reports`, the
severity line of each report of the code review, oldest first, apart from the reports of the intent
review; `code_review_commit`, the line `Commit:` of the newest one; and `head_commit`, the commit that the
facts describe. The verdict counts the round as for the intents and prints one line,
`code review: round <n> of <limit>, highest open severity <level>: ...`.

The flag `review.code_blocks` ends the shadow period; the leader sets it with a change of the contract.
Without it, or with `false`, the line blocks nothing. With `true`, the change request is not ready in four
cases: the facts hold no code review; no report exists; the newest report is open at `review.threshold` or
above, or has no severity line; the newest report names another commit than the head commit, so a push
after the last report is not reviewed yet. At the limit of the rounds the verdict stays not ready and says
that a person decides.

Claude Code has a review of its own: the plugin `code-review` of the official marketplace and the command
`/security-review`. They report faults of correctness as inline comments, and know no intent, no plan, and
no severity line that the verdict reads. A repo can run them beside the reviewer of Charter.

## The merge by the verdict

The approver of a tier merges its change requests. With `leader`, `team_lead`, or `engineer`, a person
merges. With `agent`, the verdict merges, when each of these holds; else it names the first one that does
not hold, and a person merges:

- the verdict is ready;
- the approver of the tier of the change is `agent`;
- `review.code_blocks` is true, so the reviewer of the code is past its shadow period;
- no file under `intents/` changed: a person approves an intent, whatever tier the contract gives to that folder;
- when the change holds a file outside `intents/` and `plans/`: the newest report of the reviewer of the
  code is closed on the head commit;
- when the change holds a file under `plans/`: the newest report of the intent reviewer is below
  `review.threshold` and names the head commit. In such a tier, this review is the acceptance of the plan.

A missing fact means that a person merges. The collecting step writes `review_commit`, the line `Commit:` of
the newest report of the intent reviewer. The verdict prints one line, `merge: the verdict merges: ...` or
`merge: a person merges: <the reason>`, and the evidence record holds the decision under `merge_by_verdict`.
The decision changes no readiness.

The workflow `verdict` has one step after the step that publishes the check "verdict": "Merge, for a tier
whose approver is agent". It runs only when the verdict is ready, and merges only when the record says that
the verdict merges. It merges with `gh pr merge --match-head-commit` and the commit that the verdict read,
so a push after the verdict is not merged. A refusal of the code host fails the run, and a person merges.

The merge uses the secret `CHARTER_MERGE_TOKEN`, a token that a person creates, with write access to the
contents and the pull requests of the repo. A merge with the token of the workflow starts no workflow on the
main branch. Without the secret the step merges nothing and says that a person merges. So three settings of
a person turn the merge on: the approver `agent` in a tier, the flag `review.code_blocks`, and the secret.
The contract that the setup step writes sets none of them. Needs the version 0.3.11 of the core.

## The evidence record

Each run of the verdict writes the evidence record of the change: the JSON form of the verdict, with
the fields below. On GitHub, one comment on the change request carries it, updated on each run and
marked with `<!-- charter-record -->` and written by the account of the workflow; a comment by anyone
else does not count. The check "verdict" keeps the short text.

| Field | Content |
|---|---|
| `record_form` | The version of this form: 1 |
| `change_request` | The number of the change request |
| `time` | When the record was made, UTC |
| `scripts_version` | The commit of the scripts that made the record |
| `verdict`, `reasons` | `ready` or `not ready`, and the reasons |
| `source` | The organization source and its version |
| `tier`, `approver`, `merges` | The tier of the change, the role that merges, and who holds it |
| `merge_by_verdict` | `true` when the verdict merges the change request, else `false`: a person merges. The line `merge: ...` among the reasons gives the cause |
| `gates` | Each gate with its result and its reasons |
| `checks` | The state of each check |
| `false_failures` | What a person recorded with a line `False failure: <gate>: <reason>` in the change request |
| `dropped_findings` | The findings of the intent reviewer that the author dropped, from lines `Dropped finding: <reason>` |
| `false_findings` | The findings of the intent reviewer that the leader marked as false, from lines `False finding: <reason>` |
| `review_rounds`, `review_highest_severity` | The number of the reports of the intent reviewer (0 before the first), and the severity line of the newest report (`null` before the first, or when the report has no such line) |
| `review_round` | The round of the current review loop: the reports since the loop started (0 before the first report) |
| `review_reports` | The severity line of each report of the intent reviewer, oldest first (`null` for a report without the line) |
| `code_review_reports`, `code_review_round`, `code_review_highest_severity` | The same for the reviewer of the code: the severity line of each report, the round of the current loop, and the severity line of the newest report |
| `intents` | The intents that the linked issues name, each with whether its plan exists and whether the change request removes or renames it away |

`charter_facts_github.py records --repo owner/name --last N` prints the records of the last merged
change requests, one line each, for a sample review.

## The setup step

`charter-setup` sets a repo up in one command. The plugin `charter` ships it in `bin/`, with
`charter-check`, `charter-gate`, and `charter-facts-github`; Claude Code puts that folder on the path of
the shell while the plugin is enabled (the plugin documentation, "Executables"; claude.ai and Cowork do
not install a plugin with a `bin/` folder, so that way of distribution is not open to Charter). From a
clone of the Charter repo, the same scripts are `charter/scripts/charter_*.py`.

```
charter-setup --repo NAME --source ADDRESS --source-version TAG --leader LOGIN \
              [--quality CMD]... [--code-path PATTERN]... [--high-path PATTERN]...
```

It writes `charter.toml`, `AGENTS.md`, `intents/_template.md`, `plans/_template.md`, and the four workflows from
`charter/templates/`; `docs/product.md` and `docs/architecture.md` only when they are missing. It writes
nothing when one of its files exists, and names the file. At the end it prints the steps that a person
does by hand: the secrets, the ruleset, the cache command, and the first intent.

The written workflows fetch Charter at the tag `charter--v<charter.version>` outside the checkout, and
run the scripts from there: `tests` with the version of the change request, `verdict` with the version in
the main branch, so that a change request cannot pick the scripts that judge it.

## The checker

```
python3 charter/scripts/charter_check.py validate FILE
python3 charter/scripts/charter_check.py check charter.toml [--source PATH] [--json]
python3 charter/scripts/charter_check.py instructions AGENTS.md --contract charter.toml
python3 charter/scripts/charter_check.py text README.md --contract charter.toml
python3 charter/scripts/charter_check.py source charter.toml
python3 charter/scripts/charter_check.py all charter.toml
python3 charter/scripts/charter_check.py boundary charter.toml [--source PATH]
```

`all` runs `check`, then `instructions` on `instructions.file`, then `text` on each file in
`documents.text_checked`, relative to the contract. Then it looks in the folder of the contract for a file
under a pattern of `documents.absent`, and each one is a failure that says where its content goes. It is
the one command for the contract checks.

Exit codes: 0 pass, 1 fail, 2 the check could not run. With exit code 2 the message names the cause:
no file, not a file, not UTF-8 text, not TOML, source not found, access denied, version not found.

`check --json` prints one JSON object: the source, the failures, and the effective contract. The
pattern sets with a `text_check` are redacted in that output, because they can be private.
