# Intent: a run of an agent writes no attribution line of a tool

Work item: #124. Approval: a person merges the change request that adds this file.

## Goal

The text of the change request that a run publishes holds no line with which a tool names itself as the
author.

## In scope

- The defect. A run at an adopter on 2026-11-24 published a change request whose text ended with the line
  `Generated with [Claude Code](https://claude.com/claude-code)`, with the sign of a robot before it. The
  agent wrote it. The organization of that adopter allows no such line in a commit or a change request,
  and a person removed it by hand.
- The cause. Claude Code tells the agent to end the text of a commit and of a change request with a line
  that names the tool. The setting `attribution` holds the two texts, `commit` and `pr`, and an empty text
  takes the instruction away. Source: the settings reference of Claude Code and its published schema of
  the settings, both official. The settings of a person hold the choice of that person; the settings of a
  run did not hold the key.
- `charter-check boundary` adds the key `attribution`, with an empty text for `commit` and for `pr`.
- The second guard. The agent can still write such a line, from what it learned and not from an
  instruction. `charter-run text` leaves out a line of the agent that is the line of Claude Code for a
  change request, or a trailer that names Claude or Anthropic as a co-author. A list marker, emphasis, and
  the sign of a robot before the line do not hide it. Each other line stays, also a sentence that names
  the tool and a co-author that is a person.
- Why a run needs no such line: the block of the run, at the end of the text of the change request, says
  that an agent built the change, with the commit, the turns, the duration, and the cost.
- The message of the commit of a run needs no change: a script writes it, from the title of the issue.
- `docs/contract.md`: the settings, and the step of the publishing.
- Both manifests: the same version, 0.3.18 or later.

## Out of scope

A field of the contract that lets an organization keep the line. The attribution in a session with a
person: the settings of that person hold it. A line of another tool than Claude Code: a run starts Claude
Code and no other tool. A text pattern of the organization source that fails the verdict on such a line.

## Acceptance checks

## Automatic checks

1. The settings of a run hold `attribution` with an empty text for `commit` and for `pr`, also with an
   empty boundary, and the command prints the same.
   test: `tests/test_boundary.py::Settings.test_the_settings_switch_the_attribution_off`
2. `charter-run text` leaves out the line of Claude Code for a change request and a trailer that names it
   as a co-author, in each form, and keeps a sentence that names the tool and a co-author that is a person.
   test: `tests/test_run.py::Publish.test_the_text_holds_no_line_that_names_a_tool_as_the_author`
3. In the product test, the settings of a run hold the key, and the text of a change request of a run
   holds no line of the tool that the sample text of the agent held.
   command: `python3 tests/product.py`, the steps "settings of a run" and "text of a change request of a run"
4. `docs/contract.md` names the setting and the line that the text leaves out, and both manifests name one
   version, 0.3.18 or later.
   test: `tests/test_run.py::Documents.test_the_documents_and_the_version_carry_the_attribution`

## Manual checks

5. On a machine of the code host, with the image and the version of Claude Code that the run workflow
   names, the request that Claude Code prepares for the model holds the instruction for the line with
   empty settings, and holds none with the settings of `charter-check boundary`.
   who: the engineer, with a workflow on a branch that is removed after it, and a local server in the place
   of the model, so the test makes no model call. Not automatic: the test installs Claude Code from the
   network, and the tests of this repo use no network.
