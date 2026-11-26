<!-- charter-intent-review -->
Commit: 987e8594947a48db3567b2581c237131dc4c1dab

| Intent | Verdict | Finding |
|---|---|---|
| `intents/one-closing-line.md` | approve with a change | The scope says "a list marker", but the command removes only `-`, `*`, or `+`, so it keeps `1. Closes #<number>`. Check 1 also leaves out the full stop that the scope names. |

Not checked: the decisions of epic #82. `gh issue view 82` failed because that issue is not available in this case. Issue #116 was read. It leaves the choice of fix to the intent.

**1. medium**, `intents/one-closing-line.md`, In scope. The statement is broader than what `charter_run.py` does. `LIST_MARKER` is `^[-*+]\s+`, so a numbered item such as `1. Closes #7` stays in the published text. The test named in check 1 tries only `-` and `*`.
- Sentence: "A list marker before the link, marks of emphasis around it, and a full stop after it do not change this."
- Proposed: "A bullet (`-`, `*`, or `+`) before the link, marks of emphasis around it, and a full stop after it do not change this."
- In check 1, change "with a list marker" to "with a bullet". If numbered items should also be removed, keep the scope sentence and have check 1 name them, so that the script and test must cover them.

**2. low**, `intents/one-closing-line.md`, check 1. The scope says a full stop after the link changes nothing, but check 1 does not mention it. The named test does include this case.
- Sentence: "in each form of a link, also with a list marker or with marks of emphasis."
- Proposed: "in each form of a link, also with a bullet, with marks of emphasis, or with a full stop after it."

**3. low**, `intents/one-closing-line.md`, In scope. "Link" means both a reference to an issue and a link in the file system.
- Sentences: "The file of the agent can be missing, empty, a link, or the closing line alone." and "A link is not followed: the agent wrote the file."
- Proposed: "The file of the agent can be missing, empty, a symbolic link, or the closing line alone." and "A symbolic link is not followed: the agent wrote the file."

Highest open severity: medium