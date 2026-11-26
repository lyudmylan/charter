<!-- charter-intent-review -->
Commit: 42af2428d944a0fc14323498da7a7aea54e55eec

| Intent | Verdict | Finding |
|---|---|---|
| `intents/one-closing-line.md` | approve with a change | The scope says that a list marker before the link changes nothing, but `text` handles only `-`, `*` and `+`. A numbered line such as `1. Closes #7` stays in the published text. |

I could not read the epic #82 (`gh issue view 82` failed), so I did not check the intent against the epic's decisions.

**1. medium: `intents/one-closing-line.md`, In scope**

The rule for list markers is wider than what the script does. `LIST_MARKER` in `charter/scripts/charter_run.py` is `^[-*+]\s+`. Stripping `*_. ` from the ends does not remove a leading `1`, so `1. Closes #7` does not count as a line that only links the issue. The published text would then hold the link a second time. The cases for check 1 in `tests/test_run.py` use only `-` and `*` as list markers, so they do not show this gap.

Sentence to change: "A list marker before the link, marks of emphasis around it, and a full stop after it do not change this."

Proposed text, if only bullets are meant: "A bullet (`-`, `*`, or `+`) before the link, marks of emphasis around it, and a full stop after it do not change this. A line with a number of a list before the link stays." In check 1, write "also with a bullet" in place of "also with a list marker".

If numbered lists are meant too, keep the sentence, and change the script and add a numbered case to the test of check 1.

**2. low: `intents/one-closing-line.md`, check 1**

The check promises "each form of a link". The cases of the named test use only `Closes`, `fixes:`, `Fixes`, `Resolves` and `Part of`. They leave out forms such as `close`, `closed`, `fix`, `fixed`, `resolve` and `resolved`. The script takes its pattern from the facts collector, but the test does not try each form.

Sentence to change: "The command prints the closing line one time for a text of the agent that holds a link to the issue of the run, in each form of a link, also with a list marker or with marks of emphasis."

Proposed text: keep the sentence and add a case to the test for each keyword. Otherwise, write "in the forms `Closes`, `Fixes`, `Resolves`, and `Part of`, with or without a colon" in place of "in each form of a link".

Highest open severity: medium