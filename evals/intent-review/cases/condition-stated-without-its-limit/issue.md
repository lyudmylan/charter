#66 The verdict merges the change request of a tier whose approver is agent

## Goal
A tier whose approver is `agent` is merged by the verdict, not by a person. When the verdict of a change request is `ready` and the approver of its tier is `agent`, the verdict workflow merges the change request. The output of the verdict is the log of the approval with its reasons (decision C10). A person still merges every tier whose approver is a person role.

## In scope
- The verdict workflow template: the merge step, under the conditions above and no other.
- The token of the merge: a merge with the token of the workflow starts no workflow on the main branch, so the merge uses a token that the adopter sets (a GitHub App token or a fine-grained token). The setup documents the secret.
- The evidence record: the merge by the verdict is recorded with the tier, the approver, and the reasons of the verdict.
- Separation of duties: the author of the change never merges it; the verdict runs on the main branch and is not the author.
- `docs/contract.md`: the meaning of `approver = "agent"`.

## Out of scope
- An approving review on the code host, rulesets, and auto-merge: the path of a public repo, a later issue.
- The rules of the shadow period of a new agent reviewer, the sample for a person, and the return of a tier to human approval after an escaped defect (decision C10): recorded on the epic, a later issue.
- The tier of the plan file: #65.

Intent: `intents/verdict-merges.md`
