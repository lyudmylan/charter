#92 A ready issue starts an agent run, and the run ends as a change request

## Goal
One work item with an approved intent becomes a change request with no session of a person. The run starts from the issue, works inside the boundary, and ends as a change request with the plan, the code, and the tests. The merge follows the risk tier of the change (#66); until that exists, a person merges.

Today a person starts each agent session by hand and stays in it. This issue is the first step of #82: one work item, one run at a time, built from what the code host and Claude Code give. This repo already runs Claude Code in a workflow for the reviewer of intents.

## In scope
- What makes a work item ready: the intent is merged, and a person marks the issue. The intent decides the mark.
- The tracker skill says what a work item for a run looks like: its size (one change request that one run can finish), automatic checks only, no network and no secret during the work, a change of a closed file as its own work item, and the order of the first work items of a new product. An adopter in 2026-11 had to ask for each of these.
- The run: a workflow of the CI that starts Claude Code on the issue, in its own workspace, under the boundary of the contract, #91.
- The plan. Today the agent stops and a person accepts the plan in the conversation. A run has no conversation. The risk tier of the change decides who accepts the plan (leader, 2026-11-20): in a tier whose approver is `agent`, an agent that is not the author; in a tier of a person, that person. The intent gives the form of each.
- The list of the changed paths for the gate is written with a NUL character between the paths (`-z` of git), so that no path is quoted (#101).
- The order of the steps: the gate `charter-gate boundary` runs on the result of the run, and the step that publishes runs only after it passed. A test of the workflow template checks the order, and a failed gate publishes nothing (#91).
- The end of the run: a change request that closes the issue. The workflows `tests` and `verdict` run on it as on any change request.
- A run that cannot finish says so on the issue, with the reason.
- The findings of a reviewer on the change request of a run. In the first version a person decides: a correction by hand, or a new run. A run that answers the findings is the next step of #82.
- One setting of the repo stops the start of every run (the stop switch of #12), and each run has a time limit and a limit of turns.
- The run has the toolchain of the repo, from the declared place of #88.
- The stop rules of the contract hold in the run: the limits of the acceptance loop, the review loop, and the refusals.
- The workflow as a template, written by the setup step. A person creates its secret.
- The workflow checks that the run used the settings that `charter-check boundary` printed from the contract. This replaces the conformance check of decision E4 for a run (#91).
- The manual check 16 of the boundary intent, `intents/boundary-of-a-run.md` (#91), is done in the first run of this work item: the sandbox starts, the edit tool refuses a write to the contract, a shell command reaches no host, a read of `.env` is refused, a shell command sees no token, and a call that needs a question is refused.
- The manual check of this work item: one work item of an adopter goes from the approved intent to a merged change, and no session of a person drove the run.

## Out of scope
- More than one run at a time, retries, and a run whose issue changed while it worked.
- The identity of the agent that is the author: #13.
- A merge without a person: #65, #66.
- An agent that reviews the code: #95.
- The outcome and the cost of the run in the evidence record: #93.

## Sources
- Official: the Symphony specification of OpenAI (work from the issue tracker, one isolated workspace for each issue). The AI-native SDLC playbook of Anthropic (a person approves at each gate).
- Community: the report of Vercel on its factory (one agent for each task, a person merges every change).

Intent: `intents/run-from-an-issue.md`
