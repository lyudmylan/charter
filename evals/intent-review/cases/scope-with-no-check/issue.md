#95 An agent that is not the author reviews the code of a change request

## Goal
An agent that is not the author reviews the code of each change request, under the rules of the review loop: each finding has a severity, a finding at the threshold keeps the loop open, and the rounds have a limit. A tier whose approver is `agent` merges only after this review.

Today an agent reviews the intents only, and the person who merges reads the code. #66 lets the verdict merge a change of a tier whose approver is `agent`. Without a reviewer, such a change reaches the main branch after no review but the checks, and the contract says that the author of a change is not its reviewer.

## In scope
- A reviewer workflow for a change request that changes a file outside `intents/`. It reads the diff, the intent, the plan, and the results of the checks. It posts one report in the form of the intent reviewer: the findings with a severity each, and the highest open severity in the last line.
- The checklist, as a skill of `charter-practices`: the change against the acceptance checks of the intent and against its plan, a test that does not test its check, a broken contract between parts of the system, and a document that the change made stale.
- Built-in first: Claude Code has the commands `/code-review` and `/security-review`. The intent decides what the reviewer takes from them.
- The depth follows `tiers.<tier>.review`, light or deep.
- The reviewer runs no code of the change request: its job holds a secret. The tests run in the workflow `tests`, and the reviewer reads their result.
- The verdict: an open finding at the threshold makes the change request not ready, the rounds count against `limits.review_loop`, and the evidence record holds the findings and each dropped one with its reason.
- The shadow period of decision C10: the reviewer reports first, and a person still merges. The intent puts the rule for the end of the period to the leader.
- Eval cases for the skill, as the other skills have.

## Out of scope
- A reviewer for the product document and the architecture map: #98.
- The identity of the reviewer on the code host, more than what the workflow gives.
- The sample that a person reads after the shadow period, and the return of a tier to the approval of a person after a defect that escaped: later issues of #13.

## Sources
- Official: "Harness engineering" of OpenAI (agents review each change). The AI-native SDLC playbook of Anthropic keeps a person at each gate; the risk tiers of the contract decide between the two.

Intent: `intents/code-reviewer.md`
