# Intent: this repo moves to Charter 0.3.18

Work item: #42. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.18, so that the text of the change request of a run holds no line with
which a tool names itself as the author.

## In scope

- Why: a run in this repo published a change request whose text ended with the line of Claude Code,
  `Generated with [Claude Code](https://claude.com/claude-code)`. The organization allows no such line.
  Charter 0.3.18 corrects it in its scripts: the settings of a run hold `attribution` with an empty text
  for `commit` and for `pr`, and `charter-run text` leaves such a line out of the text of the agent.
- `charter.toml`: the version 0.3.18. The contract of this repo gets no new field. The workflows fetch
  the scripts at the version of the contract, so no workflow changes.
- One change request, with the intent and the plan in it: the change is one line and has no code of the
  product, and the merge of a person is the approval of the intent.

## Out of scope

The workflows, `AGENTS.md`, and the two templates: the setup step of 0.3.18 writes them as they are.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.18.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names the version 0.3.18.
   command: `grep -q '^version = "0\.3\.18"$' charter.toml`
4. The settings of a run give an empty text for the attribution.
   command: `charter-check boundary charter.toml | grep -q '"pr": ""'`

## Manual checks

5. Each of the five workflows, `AGENTS.md`, and the two templates is the file that the setup step of
   0.3.18 writes with the values of this repo and its toolchain steps.
   who: the engineer, with a setup in an empty folder and a comparison of the files. Not automatic:
   Charter has no command yet that updates a repo.
6. The text of the change request of the next run of an agent holds no line of Claude Code.
   who: the leader. Not automatic: the check needs a model call, a machine of the code host, and the
   label that a person puts.
