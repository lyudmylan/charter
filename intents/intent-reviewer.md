# Intent: the intent reviewer, an agent that reviews the intents of a change request, in shadow mode

Work items: #45, and #70 for the run that ends with a report. Status: done. Approval: a person merges the change request that adds this file.

## Goal

An agent that is not the author reviews each change request that touches the intents, against the
product document and the decisions, and posts one table of findings. In shadow mode: it comments, and a
person still merges.

## In scope

- The checklist as a skill, `charter-practices/skills/intent-review/SKILL.md`, under 40 lines. The skill
  holds the checklist and the form of the report; this intent does not repeat them.
- The workflow `.github/workflows/review-intents.yml`: on a change request that changes `intents/**`,
  it runs the official Claude Code action of Anthropic with the token of the owner's subscription, made
  with `claude setup-token` and stored as the secret `CLAUDE_CODE_OAUTH_TOKEN`. The prompt tells the
  agent to follow the skill, to read the product document and the epics of the milestone, and to post one
  comment on the change request, marked, and updated on each run. The tools are read-only, plus the
  commands that read issues and post the comment. A limit on the turns.
- The author answers each finding in the change request: a correction, or a line
  `Dropped finding: <reason>`. The leader records a wrong finding with a line `False finding: <reason>`.
  The collector copies the dropped findings and the false findings into the record, each in its own field.
  The shadow period ends when the leader decides, from these lines, that the reviewer agrees with them;
  that is epic #13.
- Security: the workflow runs on `pull_request`, so a change request from a fork gets no secret and no
  review. The text of an intent can carry an instruction to the agent; the agent can only read and comment.
- A run ends with a report, or it fails. A step before the reviewer notes when the report comment was
  last updated; a step after it fails the run when the report comment was neither posted nor updated, and
  prints the denied commands of the run from the execution file of the action, so that the log names the
  cause. A failed run is no round: the collector counts only the successful runs; the author side reruns
  a failed run once (the skill `review-loop`). The prompt names the reading tools, says that a denied
  command is no reason to stop, and names the one command that posts the report and the one that updates
  it. The reason: a run that ended with success and no report counted as a round. The cause: the permission
  rules refuse `gh pr comment --body "<report>"` when the report carries escaped backticks, so the report
  goes in through standard input, between two marker lines.

## Out of scope

Approval or blocking by the reviewer. A review of code; the built-in review does that.

## Acceptance checks

## Automatic checks

1. The workflow restricts its trigger to `intents/**` and its tools to reading and the comment commands.
   test: `tests/test_workflows.py::ReviewIntents.test_paths_and_tools`
2. The skill is under 40 lines, and its description says when to use it and when not.
   test: `tests/test_skills.py::IntentReviewSkill.test_size_and_description`
3. The lines `Dropped finding:` and `False finding:` are read from the text of the change request into the record.
   test: `tests/test_charter_facts_github.py::Text.test_finding_lines`
4. A run whose report comment was neither posted nor updated fails with the line "the reviewer posted no
   report"; a run with a new or updated report passes; the denied commands of the run are in the log.
   The two steps have the same text in the template and in the workflow of this repo.
   test: `tests/test_workflows.py::ReviewIntents.test_a_run_without_a_report_fails`
   test: `tests/test_workflows.py::ReviewIntents.test_the_denied_commands_are_printed`
5. The prompt names the reading tools, the one command that posts the report and the one that updates it,
   and says that a denied command is no reason to stop.
   test: `tests/test_workflows.py::ReviewIntents.test_the_prompt_names_the_tools_and_the_posting_command`

## Manual checks

6. On one change request that changes an intent, the reviewer posts one table, and updates it on the next
   push. who: the leader. Not automatic: the run needs the token of the plan on GitHub.
   The run of 2026-10-01 on change request #48: one table with five findings, three of them on the
   correctness of the plan; all five applied.
7. The cost of one review is known after the first run. who: the leader. Not automatic: the number comes
   from the run on GitHub. The run of 2026-10-01: 9 turns, 59 seconds, 0.18 USD at list price, on the plan.
