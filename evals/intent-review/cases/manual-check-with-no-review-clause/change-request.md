A reviewer in CI writes no file and reads no token

Closes #131

A reviewer in CI gets a closed list of tools, and its checkout keeps no credentials.

- `--permission-mode dontAsk` refuses each tool call that the list does not allow.
- The read tools name their folder: the folder of the change, and the folder of the Charter scripts, where the skill is.
- A second list refuses the ways in which the allowed commands write a file, change a comment, or send data.
- The checkout has `persist-credentials: false`.

The cause is a test on the code host with false tokens and a local server in the place of the model. With the flags of 0.3.19 the reviewer read each file of the machine, the credentials file of the checkout too, and wrote a file at any path. It did not read the token of the model. The record is a comment on #131.

The intent, the plan, and the code are in this one change request; the merge approves the three. The two reviewers of this change request run with the new flags: their reports here are check 6.

An adopter names 0.3.20 and copies the two reviewer workflows from the setup step.

No document change: the product document does not describe the tools of a reviewer; `docs/contract.md` and `docs/decisions.md` carry the change.
