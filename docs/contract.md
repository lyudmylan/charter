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
| `run.answer_start` | choice | `factory` or `person`: what starts the agent that answers the findings of the reviewers on the change request of a run. With `factory`, the workflow `run` starts an answer after the reports of the reviewers. With `person`, or without a value, a person starts each answer. The organization sets the value for its repos, and a repo can move it toward `person` |
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
| `checks.product` | set | The product test: the commands that start the product and test it from the outside, as a user or a caller meets it. The gate `product` runs them. Needs the version 0.3.15 of the core |
| `checks.no_product_reason` | text | Why the repo has no product test yet. A contract that declares code paths has a command in `checks.product` or this reason, not both. Needs the version 0.3.15 of the core |
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
python3 charter/scripts/charter_gate.py product   --contract charter.toml
python3 charter/scripts/charter_gate.py verdict   --facts facts.json --contract charter.toml [--json]
```

| Gate | Passes when |
|---|---|
| `link` | The change request links an open issue with a closing keyword of the code host followed by the number: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves` or `resolved`, in any case, with or without a colon, then `#N` (`Closes #N`); or `Part of #N`, which links the issue without closing it, the form of a change request of the Plan phase, the intent alone. A bare `#N` in the text is a mention, not a link. |
| `documents` | No file under `documents.code_paths` changed; or a document in `documents.necessary` changed; or the change request records a reason. |
| `quality` | Each command in `checks.quality` exits with 0. |
| `product` | Each command in `checks.product` exits with 0; or the contract names no command and a reason in `checks.no_product_reason`. |
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

## The product test

A review reads the change; it does not show that the product works. The product test does: its commands
start the product and test it from the outside, as a user or a caller meets it. The repo writes them, and
Charter writes no product test.

- **The contract.** A contract that declares code paths has a command in `checks.product` or a reason in
  `checks.no_product_reason`. With neither, `charter-check all` fails and says what to add. With both it
  fails too: a repo with a product test has no reason left. A contract without code paths is not asked.
- **The gate.** `charter-gate product --contract charter.toml [--repo-only]` runs the commands as the gate
  `quality` does: with no shell, and it fails when one fails. With a reason and no command it passes and
  prints the reason.
- **The job.** The workflow `tests` has a second job, `product`, with the same checkout, the same toolchain
  block, and the same fetch of Charter as the job `tests`. It runs the gate with `--repo-only`. It runs the
  code of the change request and holds no secret.
- **The verdict.** The verdict reads the check `product` beside the check `tests`, so a failed product test
  makes the change request not ready, and the evidence record holds its state. It prints one line:
  `product test: passed: <the commands>`, `product test: not passed`, `product test: not reported` when no
  check `product` reached the facts, `product test: none, the contract says: <the reason>`, or, for a
  contract with neither field, `product test: none, the contract names no product test`. The line
  `not reported` makes the change request not ready: the contract names commands, and nothing ran them.
  Each other line changes no readiness of its own.
- **The run.** The brief of a run tells the agent to run the commands of `checks.product` after the quality
  commands, in its sandbox. So a product test that a run can use needs no network and no secret. A product
  test that needs either runs in the job `product` only.

The product test of this repo is `python3 tests/product.py`. It makes a repo with the setup step in a
temporary folder, through the commands of `charter/bin`, and runs the contract checks, the quality gate,
the boundary gate, and a verdict on it.

## The boundary of a run

A run of an agent with no person present works inside the boundary of the contract. Two parts enforce it.

```
python3 charter/scripts/charter_check.py boundary charter.toml > settings.json
python3 charter/scripts/charter_gate.py boundary --contract charter.toml --changed changed.txt
```

`charter-check boundary` prints the settings of Claude Code for the run, as JSON. The workflow of the run
writes them at the start of each run and passes them on the command line; they are not a file of the repo.
They turn the sandbox of the shell on, let no command run outside it, and stop the run when the sandbox
cannot start. A command that runs inside the sandbox needs no approval, `autoAllowBashIfSandboxed`: its
limits are the limits of the sandbox. The shell has no network. The tokens of the model and of the code
host leave the environment of each shell command. A call that would need a question to a person is
refused. The settings give an empty text for the attribution of a commit and of a change request, so
Claude Code does not tell the agent to end its text with a line that names the tool. The file tools
stay inside the folder of the repo: the mode `acceptEdits` lets them change a file of that folder with no
question, a read or a write on a path outside it would need a question and is refused, and
`blockWritesOutsideWorkingDirectories` refuses such a write in every mode. A run passes no list of allowed
tools: such a list opens a tool for every path. No shell command reads the environment of another process.
Each pattern
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

## The run

The workflow `run` takes a ready issue and runs an agent on it, with no person present. It always runs
from the main branch. A person starts it: the label `charter-run` on an issue, or a start by hand with the
number of an issue. Only a person with write access can do either. The same workflow answers the findings
of the reviewers on the change request that a run built; the section below says what starts that. The variable `CHARTER_RUNS` of the repo
with the value `off` stops the start of every run; the cancel of the code host stops a run that works. One
run works at a time. The others wait in the order of their start, up to 100: the option `queue: max` of the
group. Without it the code host keeps one waiting run, and a new run cancels it.

```
charter-run ready   --issue issue.json --root .
charter-run brief   --issue issue.json --intent intents/<part>.md --out brief.md
charter-run result  --agent agent.json --root . --base <commit> --issue issue.json --git-dir <copy> --out <folder>
charter-run text    --number <number> --request change-request.md
charter-run outcome --state published|blocked --reason TEXT --agent agent.json [--url URL]
```

The steps, in this order:

1. The checkout of the main branch, with no credential left in the folder. The scripts of Charter and the
   contract of the main branch are copied outside the folder.
2. `ready`: the issue is open, it names exactly one intent with the line `Intent: intents/<part>.md`, and
   that intent is a file of the main branch. Else the run ends as blocked, with the reason on the issue.
3. The toolchain block of the repo, with the steps of the block of `tests`.
4. The sandbox of Linux and Claude Code, at the version that the workflow names. The machine is the image
   `ubuntu-24.04`, by its name: on Ubuntu 26.04 the sandbox of Claude Code starts no command.
5. The settings of `charter-check boundary`, from the contract of the main branch with its organization
   source. The clone of the source is removed before the agent starts: the shell of the agent can read most
   of the disk, and the source of an organization can be private.
6. `brief`: the fixed text, then the text of the issue under a line that marks it as data.
7. The agent: `claude -p` with the settings as text on the command line, with no list of allowed tools, a
   limit of turns, and a time limit of the step. Its one secret is the token of the model. It writes the plan, the code, and the tests, runs
   the quality commands in its sandbox, and commits nothing. The commands `charter-gate` and `charter-check` do
   not run there: the machine holds no organization source at that time. It writes the text of the change request to
   `.charter-run/change-request.md`, or the reason of a stop to `.charter-run/blocked.md`.
8. `result`: a copy of `.git`, made before the agent, replaces the `.git` of the folder, so no
   configuration and no hook of the agent runs. The folder `.charter-run/` moves out and is never committed.
   The script commits what the agent left and lists the changed paths with a NUL character between them.
   An agent that ended in an error or wrote a reason, or a branch with no change, ends the run as blocked.
9. `charter-gate boundary` on that list, with the contract of the main branch. The step fetches the
   organization source again, with its token.
10. The publishing, only when the two steps before passed: a script pushes the branch `run/<number>` with
    no hook and opens the change request, with `Closes #<number>` as its first line. `text` writes that
    line and then the text of the agent, without a line of it that only links the same issue and without a
    line that names a tool as the author. The block of the run says that an agent built the change. It uses the secret
    `CHARTER_RUN_TOKEN`, a token that a person creates, because a change request that the token of the
    workflow opens starts no workflow. Without the secret nothing is published.
11. `outcome`, in each case: one comment on the issue with the change request or the reason, and the turns,
    the duration, and the cost that Claude Code reports.

No step after the agent runs a file of the folder that the agent wrote in: the scripts come from the copy,
and the quality commands run in the workflow `tests` of the change request. The change request then goes
through `tests`, the reviewers, and `verdict` as any other, and the merge follows the tier.

### The answer to the findings of the reviewers

An agent answers the findings of the reviewers on the change request of a run, with no session of a person:
a correction, or a dropped finding with its reason. Its commit goes to the same change request, on the
branch `run/<number>`.

The start is a rule of the contract, `run.answer_start`. With `factory`, the workflow `run` starts after
each run of a reviewer workflow on a branch `run/**`, and its job `decide` says whether an answer starts.
With `person`, or without a value, a person starts each answer: a start of the workflow by hand with the
number of the change request. A repo that moves to this version gets no new use of a subscription without
that written choice. The variable `CHARTER_RUNS` with the value `off` stops each answer too.

```
charter-gate answer --facts facts.json --contract charter.toml [--by factory|person]
```

The command reads the facts of the change request and the contract of the main branch, and prints
`start=true` or `start=false` with the reason. An answer starts when each line below holds:

- The change request is open, its branch is `run/<number>` in this repo and not in a fork, its text holds
  the block of a run, and it links the open issue of that number.
- Each reviewer that takes part has its newest report on the head commit. The reviewer of intents takes
  part when the change request changes a file under `intents/` or `plans/`, and the reviewer of the code
  when it changes another file. Else the answer waits for the report.
- A report is open: its highest open severity is at `review.threshold` or above, or it has no severity
  line. The shadow period of the reviewer of the code changes nothing here: its findings get an answer.
- No open loop is at `limits.review_loop`. At the limit a person decides. With the limit 3, an agent
  answers a change request two times at most in one loop. Without a limit in the contract nothing ends the
  loop, so the factory starts no answer; a person can start one.
- No answer handled this head commit before. A person can start a second answer for the same commit.

The job `decide` starts no agent. After a report of a reviewer, "no answer" ends it with success, and the
job `run` does not start. For a start by a person, "no answer" fails it, so that the person sees the reason.

The job `run` then works as for an issue, with these differences:

1. The step that reads the issue fetches the branch of the run and stops when the branch moved after the
   decision. It opens no file of the branch. The steps of the toolchain run on the files of the main
   branch, and the settings come from the contract of the main branch.
2. The brief of an answer: the fixed text, then the newest report of each reviewer and the text of the
   issue, under a line that marks them as data. The agent corrects a finding at the threshold or above, or
   drops it with the reason. A finding that needs a change of a closed path, the intent among them, is for a
   person. It marks no finding as false. It writes one line for each finding to `.charter-run/answers.md`.
3. The step of the agent opens the branch of the run. `result --answer-round <n>` commits with the message
   `Answer the findings of review round <n> (#<number>)`. No changed path is a result too: the agent can
   drop each finding. The gate checks the paths that this answer changed.
4. The publishing: a script pushes the commit to the branch, with no force, and changes the text of the
   change request. `body` keeps the text and adds each line `Dropped finding:` of the answers that the text
   does not hold yet; no other line of the agent reaches the text. The script writes the words
   `by the agent of a run:` right after `Dropped finding:`. The reviewers read the line as each dropped
   finding, so the finding is closed for them; the words tell a person that no person dropped it, and the
   verdict merges no change request that holds such a line. One more block of a run follows. An answer
   that changed no path and dropped no finding publishes nothing.
5. The outcome goes on the change request, not on the issue: `answered` or `blocked`, the line
   `Answered commit:` with the head commit whose reports the agent answered, the three numbers, and the
   lines of the answers. The facts collector reads that line back into the fact `answered_commits`.

```
charter-run brief  --issue issue.json --intent intents/<part>.md --reports comments.json --threshold <severity> --out brief.md
charter-run body --body body.md --answers answers.md [--changed <file>]
charter-run outcome --state answered|blocked --agent agent.json --url URL --answered <commit> --answers answers.md
```

The push starts the reviewers again, and their reports start the next decision. The loop ends when no
report is open at the threshold, or at the limit of the contract, or when the stop switch is off. A script
counts the rounds from the reports of the reviewers; the agent does not.

## The record of a run

The evidence record of a change request that a run built says how the run ended and what it cost. After the
push, the publishing step reads the commit that it pushed, with no hook, and adds the block of the run at
the end of the text of the change request:

```
charter-run record --agent agent.json --commit <commit>
```

```
<!-- charter-run -->
Run: commit=<the commit that the run published> turns=<n> duration_seconds=<n> cost_usd=<n>
```

A value that Claude Code did not report is `none`. The facts collector reads the blocks of the text into the
fact `run`: the marker line, then the line `Run:` right after it, with the four values in any order. The
first block is the run that built the change request, and each answer of an agent adds one. The commit is
the one of the last block. Each number is the sum of the blocks that hold it, and with more than one block
`agent_runs` is their number. A last block with a missing or unknown name, a value that is no number, or a
commit that is no identifier gives no run, and the collection goes on. A change request without the block
has no fact `run`.

The verdict decides the outcome, one of three:

| Outcome | When |
|---|---|
| `success` | The head commit is the commit of the run, the verdict is ready, and no reviewer has an open finding at the threshold |
| `flawed` | The head commit is the commit of the run, and the verdict is not ready, or the newest report of the intent reviewer or of the reviewer of the code is open at the threshold or has no severity line, also in the shadow period of that reviewer |
| `manual` | The head commit is not the commit of the run, or the facts name no head commit: a later push changed what the run built |

A run that opened no change request is `blocked`; that outcome stays on the issue. The verdict prints one
line after the line `merge: ...`: `run: <outcome>, <turns> turns, <duration>, cost <cost> (an estimate of
Claude Code)`, or `run: none, no agent run built this change request`. With more than one block the line
names their number, `<n> runs of an agent`, before the turns. The cost is the estimate that
Claude Code prints, not a bill. The block is text of the change request, so a person can write one: the
record says what the text says, and the outcome decides nothing. It changes no readiness and no merge.
Needs the version 0.3.14 of the core.

## On the code host

Two workflows run on each change request of this repo. They and the collecting script
`charter/scripts/charter_facts_github.py` are the only parts that are specific to GitHub.

| Workflow | Trust | What it does |
|---|---|---|
| `tests` | Runs the code of the change request. It gets no secret. | Runs the quality checks of the contract with `--repo-only`, and in a second job, `product`, the gate `product` with `--repo-only`. |
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
- the text of the change request holds no finding that an agent of a run dropped: a person reads the reason;
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
| `run` | The agent run that built the change request: `outcome` (`success`, `flawed`, or `manual`), `turns`, `duration_seconds`, and `cost_usd`, each number `null` when Claude Code did not report it. `null` when no run built the change request. See "The record of a run" |

`charter_facts_github.py records --repo owner/name --last N` prints the records of the last merged
change requests, one line each, for a sample review.

## The setup step

`charter-setup` sets a repo up in one command. The plugin `charter` ships it in `bin/`, with
`charter-check`, `charter-gate`, `charter-facts-github`, and `charter-run`; Claude Code puts that folder on the path of
the shell while the plugin is enabled (the plugin documentation, "Executables"; claude.ai and Cowork do
not install a plugin with a `bin/` folder, so that way of distribution is not open to Charter). From a
clone of the Charter repo, the same scripts are `charter/scripts/charter_*.py`.

```
charter-setup --repo NAME --source ADDRESS --source-version TAG --leader LOGIN \
              [--quality CMD]... [--product CMD]... [--code-path PATTERN]... [--high-path PATTERN]... [--toolchain FILE]
```

It writes `charter.toml`, `AGENTS.md`, `intents/_template.md`, `plans/_template.md`, and the five workflows from
`charter/templates/`; `docs/product.md` and `docs/architecture.md` only when they are missing. It writes
nothing when one of its files exists, and names the file. At the end it prints the steps that a person
does by hand: the secrets, the ruleset, the cache command, and the first intent. The flag `--product`
puts its commands in `checks.product`; without it the contract gets the reason "no product to start yet",
and the steps by hand name the product test. For the workflow `run`
they name the label `charter-run`, the variable `CHARTER_RUNS`, and the secret `CHARTER_RUN_TOKEN`; the
setup step creates nothing on the code host.

The written workflows fetch Charter at the tag `charter--v<charter.version>` outside the checkout, and
run the scripts from there: `tests` with the version of the change request, `verdict` with the version in
the main branch, so that a change request cannot pick the scripts that judge it.

The `tests` workflow has a block for the toolchain of the repo: the steps that install its tools, after
the checkout and before the quality step, between the line `# charter:toolchain:start` and the line
`# charter:toolchain:end`. The flag `--toolchain FILE` fills the block. The file holds steps as they stand
in a workflow, with no indent before the first `- `; the setup step gives them the indent of a step and
does not substitute their text. A file that holds a marker line is refused, and so is a missing file.
Without the flag the block is empty. The steps run in the `tests` workflow, which holds no secret. Its job
`product` has the same block with the same steps, and so has the workflow `run`, before the agent starts.
An update of the repo keeps the block.

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
