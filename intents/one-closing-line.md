# Intent: the change request of a run holds the line that closes its issue one time

Work item: #116. Approval: a person merges the change request that adds this file.

## Goal

The text of the change request that a run publishes holds the line `Closes #<number>` one time, as its
first line.

## In scope

- The defect. The first run that ended with a change request, at an adopter on 2026-11-22, published a
  text with the line two times. The publishing step wrote it as the first line. The agent reads in
  `AGENTS.md` that a change request closes its issue, so its text started with the same line.
- A command `text` of `charter_run.py` writes the text of the change request, before the block of the
  run: the line `Closes #<number>`, an empty line, and then what the agent wrote. It leaves out a line of
  the agent that only links the issue of the run: a closing keyword of the code host or `Part of`, then
  the number, in the forms that the facts collector reads as a link. A list marker before the link, marks
  of emphasis around it, and a full stop after it do not change this. A line that links another issue
  stays. A line that holds more than the link stays too, a second number or other words: the script
  removes no words of the agent.
- The file of the agent can be missing, empty, a link, or the closing line alone. The text then holds one
  sentence in its place, the sentence that the workflow wrote before this change: "An agent run built this
  work item. The agent wrote no text for the change request." A link is not followed: the agent wrote the
  file.
- The publishing step, in the template and in the workflow of this repo, calls the command. The shell
  lines that wrote the text leave the step.
- The brief stays as it is. The script decides, so the result does not depend on what the agent reads.
- `docs/contract.md`: the command, and the sentence on the line of the agent.
- Both manifests: the same version, 0.3.17 or later.

## Out of scope

Other parts of the text that the agent writes. The title of the change request. Empty lines that stay in
the middle of the text after a line is left out.

## Acceptance checks

## Automatic checks

1. The command prints the closing line one time for a text of the agent that holds a link to the issue of
   the run, in each form of a link, also with a list marker or with marks of emphasis. It keeps a line
   that links another issue and a line that holds more than the link. A file that is missing, empty, or the closing line alone gives the
   sentence.
   test: `tests/test_run.py::Publish.test_the_text_holds_the_closing_line_one_time`
2. A link in the place of the file of the agent is not followed.
   test: `tests/test_run.py::Publish.test_a_link_in_the_place_of_the_text_is_not_followed`
3. The publishing step of the template and of the workflow of this repo, run with a fake `gh` and a fake
   `git` on a text of the agent that starts with the closing line, opens a change request whose text
   holds the line one time, as its first line.
   test: `tests/test_run.py::Publish.test_the_published_text_closes_the_issue_one_time`
4. `docs/contract.md` names the command and the line that is left out, and both manifests name the same
   version, 0.3.17 or later.
   test: `tests/test_run.py::Documents.test_the_documents_and_the_version_carry_the_closing_line`
5. In the product test, the command of the installed plugin prints the closing line and the text of the
   agent, without the line of the agent that links the same issue.
   command: `python3 tests/product.py`, the step "text of a change request of a run"

## Manual checks

6. The next run at an adopter, with this version, publishes a change request whose text holds the closing
   line one time. who: the leader. Not automatic: a run needs the token of the model and a machine of the
   code host.
