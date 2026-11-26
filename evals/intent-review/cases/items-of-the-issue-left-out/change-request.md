A ready issue starts an agent run, and the run ends as a change request

Closes #92

The intent, the plan, and the code of one work item, in one change request. It is built on #100 and #103 to #108 and holds their commits; merge those first. The check `verdict` is red until #104 is merged, and `review-code` until #106 is merged.

What it adds:
- A workflow `run`. A person puts the label `charter-run` on an issue whose intent is merged, or starts the workflow by hand. With no session of a person, an agent builds the work item, and scripts check and publish the result as a change request.
- One variable of the repo, `CHARTER_RUNS`, stops the start of every run. One run works at a time.
- The agent works in the sandbox, under the settings of the boundary, with one secret, the token of the model. It holds no token of the code host and commits nothing.
- After the agent, only scripts act: they put back a copy of `.git` that was made before the agent, commit what the agent left, check each changed path against the boundary, and only then publish with the secret `CHARTER_RUN_TOKEN`, which a person creates. No step after the agent runs a file that the agent wrote.
- The outcome is written on the issue in each case: the change request, or "blocked" with the reason, and the turns, the duration, and the cost.

Proof so far, and its limit:
- 258 tests pass, 20 of them new. Thirteen faults put into the code on purpose each made a test fail.
- Two tests with a real Claude Code on a Mac, in a copy of this repo, are on the issue #92. The second one found a fault of the first design: with a list of allowed tools on the command line, the agent read and wrote files outside its folder. The settings of the boundary now keep the file tools inside the folder, and the workflow passes no such list. The same test with the new settings refused each case.
- No run happened on a runner. This workflow starts from an issue, so the code host runs it only from the main branch, after the merge. The first run needs the two secrets and is the manual check 15; the check on Linux is the manual check 16.

What a person does after the merge, before the first run: create the secret `CHARTER_RUN_TOKEN` (a token that can push a branch and open a change request), and the label `charter-run`.

An Opus subagent wrote the code and the tests from the plan, and added four protections of its own, which the author session read and kept: the copy of `.git`, no token left in the address of a clone, no Python one-liner after the agent, and no read of the agent's files through a link. The author session wrote the intent and the plan, ran the two real tests, and changed the design after the second one.
