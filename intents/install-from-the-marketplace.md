# Intent: the core as a plugin, and the marketplace of the two plugins

Work item: #36. Status: done. Approval: a person merges the change request that adds this file.

## Goal

The two plugins of Charter install from the Charter repo with `claude plugin install`.

## In scope

- The core moves into the plugin folder `charter/`: its manifest, `charter/scripts/`, `schema/`. The tests, the
  intents, the documents, and the workflows of this repo stay at the root.
- During the beta, the marketplace file lives in a private repo of the owner, `charter-marketplace`, and
  lists the two plugins from the public Charter repo by their folders (a GitHub source with a path). The
  name of the marketplace is `charter`, so the plugins are `charter@charter` and `charter-practices@charter`.
  At the release, the file moves into the Charter repo. Nobody finds the plugins in a listing before that.
- The first version of each plugin in its manifest: 0.1.0. The version lives there only. The release tag
  follows the convention of the Claude Code documentation on plugin dependencies: `charter--v0.1.0`. The
  leader pushes it with `claude plugin tag --push` after the plugin folder merges.
- The workflows, the quality checks, `AGENTS.md`, the README, and the commands in the done intents name
  `charter/scripts/`. In `charter.toml`, `charter/**` replaces `schema/**` and `scripts/**` in the high tier
  and in `documents.code_paths`.

## Out of scope

Publication in a marketplace of Anthropic. The setup step. The move of the marketplace file into the Charter repo: that is the release.

## Acceptance checks

## Automatic checks

1. The two plugins and the marketplace validate. command: `claude plugin validate charter`
   command: `claude plugin validate charter-practices`
2. The tests and the quality checks pass from the new place. command: `python3 -m unittest discover -s tests`
3. The plugins install on this computer from the private marketplace. command: `claude plugin install charter@charter`

## Manual checks

The run of 2026-10-01: the two plugins validate; 70 tests pass; the tags `charter--v0.1.0` and
`charter-practices--v0.1.0` are pushed; both plugins install from the private marketplace at 0.1.0.

4. The gates of this repo ran from the new place on the change request of this work item: the check "verdict" is green.
   who: the leader. Not automatic: the proof is the check on GitHub.
