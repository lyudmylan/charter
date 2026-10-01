# Intent: the intent reviewer, an agent that reviews the intents of a change request, in shadow mode

Work item: #45. Status: done. Approval: a person merges the change request that adds this file.

## Goal

An agent that is not the author reviews each change request that touches the intents, against the
product document and the decisions, and posts one table of findings. In shadow mode: it comments, and a
person still merges.

## In scope

- The checklist as a skill, `charter-practices/skills/intent-review/SKILL.md`, under 40 lines: what to
  check (a goal that is a result; a bounded scope; acceptance checks that are automatic by default and
  prove the goal; nothing beyond the minimum; consistency with `docs/product.md` and the decisions of the
  epics; one place for each fact), and how to report (one table with one row per intent, then at most
  five findings, each with the exact sentence and the proposed text). A finding that affects the
  correctness of the plan is marked; a preference is marked as a preference.
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

## Manual checks

4. On one change request that changes an intent, the reviewer posts one table, and updates it on the next
   push. who: the leader. Not automatic: the run needs the token of the plan on GitHub.
   The run of 2026-10-01 on change request #48: one table with five findings, three of them on the
   correctness of the plan; all five applied.
5. The cost of one review is known after the first run. who: the leader. Not automatic: the number comes
   from the run on GitHub. The run of 2026-10-01: 9 turns, 59 seconds, 0.18 USD at list price, on the plan.
