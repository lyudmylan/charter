Each started run waits for its turn: a new run cancels no run that waits

Closes #120

A person who started more than two runs got two: the first one worked, the last one waited, and the code host cancelled each run between them. A cancelled run of this kind holds no job, so its issue got no comment.

- The concurrency group of the run workflow holds `queue: max`, in the template and in the workflow of this repo. Up to 100 runs wait, in the order of their start. One run works at a time, as before.
- `docs/contract.md` says what waits and why the option is there.
- The version stays 0.3.17: no tag names it yet.

The intent, the plan, and the code come together. The evidence of check 3, two tests on the code host, is in a comment on #120.

No document change: the product does the same work, and `docs/contract.md` holds the changed sentence.
