The change request of a run holds the line that closes its issue one time

Closes #116

The text of the change request of a run held the line `Closes #<number>` two times: the publishing step wrote it, and the text of the agent started with it too.

- `charter-run text` writes the text of the change request, before the block of the run. It writes the closing line, then the text of the agent without a line that only links the issue of the run.
- The publishing step calls the command, in the template and in the workflow of this repo. The shell lines that wrote the text leave the step.
- A missing file, an empty file, a link, or the closing line alone gives the sentence that the workflow wrote before.
- Version 0.3.17.

The intent, the plan, and the code come together. Check 6 of the intent is manual: the next run at an adopter with this version.

No document change: the product does the same work, and `docs/contract.md` names the new command.
