# Decision record

Decisions for Charter, with their reasons. What Charter is and why: see
[product.md](product.md).

- **Accepted**: decided by the product owner.
- **Proposed**: written down, not yet confirmed.
- **Open**: not decided.

A decision changes only through a reviewed change to this file.

## A. Direction

| ID | Decision | Reason | Date |
|---|---|---|---|
| A1 | Charter serves the engineering leader. It works for one leader with agents and for an organization of 20 to 50 people in several teams, with any technology stack. | Tools for one engineer do not answer the questions of the leader. | 2026-09-28 |
| A2 | Skills are light. The organization model is part of the core. | The first iteration had heavy skills, and the organization could not lock a rule. | 2026-09-28 |
| A3 | Claude Code first. The contract stays in open formats. | Full use of one runtime, without loss of portability for the rules. | 2026-09-28 |
| A4 | Built-in first, then install, then build. New parts come from practical work, one at a time. | No reinvention, and no cost without evidence of need. | 2026-09-28 |
| A5 | Charter is a public product. | Adoption by other organizations is a goal. | 2026-09-28 |
| A6 | Out of scope: how to build or evaluate an agent inside a product. | A different subject with a different user. | 2026-09-28 |
| A7 | Two plugins in one marketplace: `charter`, which depends on nothing, and `charter-practices`, which depends on `charter`. | An adopter with other practice skills can take the control layer alone. | 2026-09-28 |
| A8 | Charter follows its own contract. The Charter repository gets no special machinery. | First user and first test; protection against effort on the plugin itself. | 2026-09-29 |
| A9 | No method framework at the start. A team that uses one binds it in the lifecycle map. | Follows from A4 and C3. | 2026-09-29 |

## B. Model

| ID | Decision | Reason | Date |
|---|---|---|---|
| B1 | Four owners of rules: organization, team, repository, person. A person is free in the method, not in the gates. The contract says if personal skills are permitted. | An engineer needs an own way of work; the gate checks the result. | 2026-09-28 |
| B2 | Three types of actor: a person, a person with an agent, an agent alone. An agent is an actor, not an owner of rules. | The owner of a rule and the doer of the work are different questions. | 2026-09-28 |
| B3 | An agent that works alone holds a grant: identity, boundary, decision rights by risk tier, named human owner. | Accountability stays with a person. | 2026-09-28 |
| B4 | The contract names roles. One person can hold more than one role. There is no special mode for a team of one. | The size of the organization changes who holds a role, not the rules. | 2026-09-29 |
| B5 | The writer does not review its own work. An agent has its own identity. | Agents praise their own work. Most code hosts do not let an author approve the own change. | 2026-09-29 |
| B6 | A small organization can be simulated: agents hold team roles, and a reference organization proves that the contract and the overrides work. | The organization model must be tested before real teams exist. | 2026-09-28 |
| B7 | The contract holds a minimum table of roles and rights from the first iteration: what a leader, a team lead, an engineer, and an agent can do. Detail comes later. | The gates must know who can approve. | 2026-09-29 |

## C. Control

| ID | Decision | Reason | Date |
|---|---|---|---|
| C1 | A person always decides: direction and scope, a change to the contract, a production release. | Ownership and control stay with a person. | 2026-09-28 |
| C2 | Merge: risk tiers from the start. A person approves the high tier. | Approval of every merge is a bottleneck. Both official sources accept risk-based approval. | 2026-09-28 |
| C3 | A gate checks the result. It checks the process only where the organization locked a process rule. | The official sources differ on result against process; this is the choice. | 2026-09-28 |
| C4 | Three types of drift are controlled: the agent skips the process, the agent does more than the task, and erosion with time. | | 2026-09-28 |
| C5 | Three limits return control to a person: the loop for the acceptance checks, the loop between writer and reviewer, repeated refusals by the boundary. Each is a contract value; the default is 3. | Official guidance asks for stopping conditions and gives no fixed number. | 2026-09-29 |
| C6 | A stop switch: one setting stops all agents. | A simple way to stop. | 2026-09-29 |
| C7 | The contract files, the gate scripts, the approved acceptance checks, and the eval cases are protected. A change to them needs a person. Gates run from the main branch. | A change must not be able to change its own gate. | 2026-09-29 |
| C8 | Each contract section names its owner as a role. The code owners file of the code host is written from the roles. | Use the enforcement that the code host has. | 2026-09-29 |
| C9 | The evidence record holds, for each change: the gate verdicts, the dropped findings with reasons, false failures of a gate, eval results, and cost. | The leader audits by sample, not by approval of every step. | 2026-09-29 |
| C10 | Additions to C2: a shadow period for a new agent reviewer; a log of each approval with reasons; a risk-weighted sample for a person; automatic return of a tier to human approval after an escaped defect. | The first three come from official guidance. The fourth withdraws a grant after a failure. | 2026-09-29 |
| C11 | A reading that an agent drafts for a person (a manual check whose result is a judgment on evidence, such as the error analysis of an eval round) reaches the person after a review by an agent that is not the author, as a list of disagreements with the evidence on each side; the person decides the disagreements and confirms the rest in one word. | B5: agents praise their own work. C2: approval of every item by a person is the bottleneck. C10: the person decides on a sample, and the disagreements are that sample. | 2026-11-03 |
| C12 | The verdict merges a change request of a tier whose approver is `agent` when each of these holds: the verdict is ready; the approver of the tier is `agent`; `review.code_blocks` is true; no file under `intents/` changed, because a person approves an intent; for a change of code, the newest report of the code review is closed on the head commit; and, for a change of a file under `plans/`, the newest report of the intent reviewer is below the threshold and names the head commit. Else a person merges. Three settings of a person turn the merge on: the approver `agent` in a tier, the flag `review.code_blocks`, and the secret `CHARTER_MERGE_TOKEN`. | Autonomy is a grant by risk tier (B3, C10). Each condition is a fact that a script reads. The author never merges, because the verdict runs from the main branch. | 2026-11-20 |

## D. Lifecycle

| ID | Decision | Reason | Date |
|---|---|---|---|
| D1 | A repository declares its tracker, code host, and CI in the contract. | Independence of tools. | 2026-09-28 |
| D2 | The lifecycle map binds each phase to what does the work. | A team can replace a skill; the gate stays. | 2026-09-28 |
| D3 | Tracker skill (light): plan from one product document and write decisions back; milestone, epic, work item; look for existing items first. | No ready-made skill creates the tracker structure. | 2026-09-28 |
| D4 | A work item states: goal, in scope, out of scope, acceptance checks. | The test is planned at the planning phase. | 2026-09-28 |
| D5 | A person approves the acceptance checks before the code starts. The agent works until they pass, up to a limit. The agent cannot change an approved check alone. | Agreement on "done" before code; a check that the agent can run closes the loop. | 2026-09-28 |
| D6 | The link from a change to its work item is a gate. | | 2026-09-28 |
| D7 | Review uses the built-in code review and security review. Charter has no review skill. The repository instructions add two lines: broken contracts between parts, and documents made stale by the change. | The built-in review covers the rest. | 2026-09-28 |
| D8 | The risk tier sets the depth of the review. | It is a decision right, so it belongs in the contract. | 2026-09-28 |
| D9 | Findings: one that affects correctness or an acceptance check is corrected. One that is out of scope or a preference is recorded, not corrected. Disagreement, or a reached limit, goes to a person. | To correct every finding causes over-engineering. | 2026-09-28 |
| D10 | Quality checks run before the push. The contract names them. | | 2026-09-29 |
| D11 | Documents gate, two parts: a script (named code paths changed, so the related document changes, or a reason is recorded) and the review. | A script cannot fully know if a document is stale. | 2026-09-29 |
| D12 | The change request needs no skill; the runtime does it. No change goes directly to the main branch. | The model knows this work. | 2026-09-29 |
| D13 | One merge-readiness script gives one verdict after all other checks: required checks passed; no open finding on correctness; the approval of the risk tier is there; the work item is linked; the documents gate passed. | Green CI alone is not sufficient. | 2026-09-29 |
| D14 | No merge around a failed check. An override needs a person with that right, and is recorded. | | 2026-09-29 |
| D15 | A setup step creates the contract and the first documents in a repository. Later. | The contract format must exist first. | 2026-09-28 |
| D16 | The lifecycle map names each built-in ability of the runtime that Charter uses. | Nothing is used in silence; an upgrade of the runtime shows what to check. | 2026-09-29 |
| D17 | The repository instructions are written from the contract and carry lines from all owners. They are advice; the gates enforce. | The file is the location where the agent reads the rules, not the owner of the rules. | 2026-09-29 |
| D18 | The plan of the intent `intents/<part>.md` is the file `plans/<part>.md`. | The path patterns of a tier have no exclusion, so a file under `intents/` cannot leave the high tier; a folder of its own needs no special rule. The plan is the words of the author, and it is no rule: the intent holds the acceptance checks and stays in the high tier. | 2026-11-20 |
| D19 | Charter enforces that a product tests itself as a whole: a contract with code names its product test in `checks.product`, or the reason for none in `checks.no_product_reason`, and each change request carries the result of the job `product`. Charter writes no product test. | A repo passes each gate with unit tests alone, and a review reads the change but does not show that the product works. Official: a run of the app catches what tests and typechecks miss, and an agent that can check its own work does better (Anthropic, Claude Code best practices); the app starts for each change (OpenAI, Harness engineering). Community: scenarios kept outside the repo, so that the author agent does not see them (StrongDM); they stay out of scope, a decision of the leader later. | 2026-11-20 |

## E. Agent boundary

| ID | Decision | Reason | Date |
|---|---|---|---|
| E1 | The boundary is a section of the contract. The organization sets the minimum and locks it. | | 2026-09-29 |
| E2 | Three layers, in this order: sandbox, permission rules, a script that reads the command. | A rule on command text is not a security boundary; the sandbox does not depend on the text. | 2026-09-29 |
| E3 | The sandbox is mandatory for an agent that works alone, and optional for a person with an agent. | The person is the second control when present. The products of the two vendors have different defaults. | 2026-09-29 |
| E4 | Boundary tests run as a gate: decision tests (input, expected decision, with forms that try to go around a rule) and a conformance check (the repository settings contain the minimum of the organization). For a run without a person, E8 replaces the conformance check. | A rule without a test fails silently. | 2026-09-29 |
| E5 | Rules that must never fail live in the sandbox and the deny rules, not only in a script. | A script that stops or exceeds its time limit lets the action continue. | 2026-09-29 |
| E6 | In a run without a person, an action that needs a question is refused. | | 2026-09-29 |
| E7 | A run without a person holds no credential of the code host. A step that is a script pushes the branch and opens the change request, after the gate `boundary` passed. | "A run never pushes to the main branch and never merges" then needs no rule on the text of a command (E2): the agent has nothing to do it with. | 2026-11-20 |
| E8 | The settings of a run are written from the contract at the start of each run, by `charter-check boundary`. They are not a file of the repo. The workflow of the run checks that the run used them. | A file can differ from the contract, and a change request can change it. Claude Code gives settings from the command line the precedence over the files of a repo, and a sandbox that is set there ignores a file of the repo that loosens it (the pages on settings and on the sandbox). | 2026-11-20 |
| E9 | For `boundary.no_write` there are two layers. The sandbox and the deny rules stop the agent (E5). The gate `boundary` reads the result, whatever wrote it, and runs between the run and the push; a gate that fails or does not run publishes nothing. | The gate is the layer for a writer that the sandbox and the permission rules do not cover: in Claude Code the sandbox covers the shell, and the permission rules cover the file tools. On Linux the sandbox closes no file that does not exist yet. | 2026-11-20 |
| E10 | A run can write the plan of a work item, `intents/<part>.plan.md`, also under a pattern of `boundary.no_write`. Replaced by D18: the plan lives in `plans/`, outside the closed patterns. | The run is the author of the plan. The approved intent holds the acceptance checks, and it stays closed to the run. | 2026-11-20 |
| E11 | A person starts each run of an agent on an issue: the label `charter-run` on a ready issue, or a start of the workflow `run` by hand with the number of the issue. | Only a person with write access can do either on the code host, so each run has a person who asked for it. | 2026-11-20 |
| E12 | One variable of the repo, `CHARTER_RUNS`, stops the start of every run with the value `off`. The cancel of the code host stops a run that works. | One switch that a person sets without a change request, in one place (#12). | 2026-11-20 |
| E13 | A token of a person, the secret `CHARTER_RUN_TOKEN`, publishes the result of a run, in the publishing step only. No step after the agent runs a file that the agent wrote. | A change request that the token of the workflow opens starts no workflow on the code host. A later step holds a token, so a file of the agent must not run beside it. | 2026-11-20 |
| E14 | A reviewer in CI has a closed list of tools: `--permission-mode dontAsk`, read tools that name their folder, five shell commands that read, and a checkout that keeps no credentials. It has no command that writes to the code host: its report is its final answer, and a step of the workflow posts it. A test with a local server in the place of the model repeats the cases. | A reviewer reads text that it did not write, and it runs next to two tokens. With the bare tools `Read`, `Glob`, and `Grep` it read each file of the machine, the credentials file of git too, and `git diff --output` wrote a file at any path. A command such as `gh pr comment --body-file <path>` or `gh api --input <path>` reads a file by itself, outside the read rules, and a pattern cannot refuse each form of its flags; so the reviewer has no such command. The limit: the test runs the program that the action runs, not the action. | 2026-11-25 |

## F. Skills, evals, model upgrades

| ID | Decision | Reason | Date |
|---|---|---|---|
| F1 | A skill is added only for knowledge that the model cannot have, or after practical work shows a failure. | Official guidance: add only context that the model does not have. | 2026-09-29 |
| F2 | The core is tested with usual tests. Each skill has three eval cases, run with the built-in eval tool: pinned model, cost ceiling, graders without a model where possible. | A script is deterministic; a model is not. | 2026-09-29 |
| F3 | Evals run when a skill changes and when a model upgrade is planned. | Cost. | 2026-09-29 |
| F4 | A model upgrade is a planned procedure and a contract change: run the full suite with and without each skill; then keep, shorten, or correct; remove one item at a time. Rules and gates stay. | Each part of a harness holds an assumption about the model, and assumptions become stale. | 2026-09-29 |
| F5 | When a gate fails, examine the gate first, then the case, then the work. Record each false failure. | A new gate fails falsely more frequently than truly. | 2026-09-29 |

## G. Documents

| ID | Decision | Reason | Date |
|---|---|---|---|
| G1 | Documents serve people and agents. Living documents are kept current: the product document, the README, the architecture map, this record. | The code cannot tell the reason for a decision. | 2026-09-29 |
| G2 | Plans, specs of one change, and review findings are not updated after the merge. No document describes how the code operates in detail. | A stored document costs nothing until it is read, but a stale one misleads. | 2026-09-29 |
| G3 | The contract lists the necessary documents. Default: one architecture map. | Teams and systems differ. | 2026-09-29 |
| G4 | Diagram skill (light), ten rules: draw at a level that changes rarely; show the mechanism, not names; prefer a sentence when it is faster; one claim, with title and caption; label every arrow; short labels; one color with a meaning; draw boundaries explicitly; planned parts dashed; diagrams stay as text. | | 2026-09-29 |
| G5 | Two drawing tools for now: Mermaid for diagrams that change with the code, SVG for a small number of important diagrams. | Practice will show if SVG alone is sufficient. | 2026-09-29 |
| G6 | A choice of the architecture and its reason live in the architecture map, next to the part, in one or two sentences. A choice that must always hold becomes a check. The history is in git. No separate file holds one decision; this record of the process decisions is one file and is not affected. | With one file for each decision a fact has two homes. A rule that only a document holds does not hold: the rule of 2026-10-01 lived in an epic, and an agent wrote eight decision files while both contract checks passed. Official: the design spec holds the decisions of a work item (Anthropic, the AI-native SDLC playbook); "When documentation falls short, we promote the rule into code" (OpenAI, Harness engineering). Community: one file for each decision (Nygard, 2011); neither official source asks for it. | 2026-11-18 |

## H. Sources and cost

| ID | Decision | Reason | Date |
|---|---|---|---|
| H1 | Official guidance from Anthropic and OpenAI first. Community sources fill gaps. Where the official sources differ, the record states the difference and the choice. | | 2026-09-28 |
| H2 | Cost is measured. The cost of each change goes into the evidence record. | Token use is a real cost of an organization. | 2026-09-29 |
| H3 | Decisions live in the repository, not in session logs. | Review, history, and access for people and agents. | 2026-09-29 |

## P. Proposed

None at this time.

## O. Open

| ID | Question |
|---|---|
| O1 | The scope of the first iteration |
| O2 | The real risk tiers |
| O3 | The format of the contract file, and its checker |
| O4 | The design of the evidence record, with the cost of each change |
| O5 | Agents in team roles: the design must limit cost |
| O6 | The sandbox rule on a platform that has no sandbox |
| O7 | The rows of the table of roles and rights |

## V. To verify before build

| ID | Item |
|---|---|
| V1 | The built-in code review reads the repository instructions |
| V2 | What a script can see of the refusals of each boundary layer |
| V3 | How a Mermaid theme shows on the code hosts |
| V4 | Statements from OpenAI were read through summaries, not on the primary pages |

## Sources read on the primary page

- Anthropic, "Building effective agents", 2024-12-19
- Anthropic, "Effective context engineering for AI agents", 2025-09-29
- Anthropic, "Harness design for long-running application development", 2026-03-24
- Anthropic, postmortem on Claude Code quality, 2026-04-23
- Anthropic, "How Anthropic secures its AI-native software development lifecycle", 2026-07-21
- Anthropic, skill authoring best practices
- Claude Code documentation: best practices, extension overview, costs, skills, memory, permissions, sandboxing, plugin dependencies, plugins for organizations, plugin evals
- `anthropics/claude-code-action`, example `agent-approval-check`
