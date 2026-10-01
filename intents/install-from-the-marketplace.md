# Intent: the core as a plugin, and the marketplace of the two plugins

Work item: #36. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The two plugins of Charter install from the Charter repo with `claude plugin install`.

## In scope

- The core moves into the plugin folder `charter/`: its manifest, `scripts/`, `schema/`. The tests, the
  intents, the documents, and the workflows of this repo stay at the root.
- The marketplace file `.claude-plugin/marketplace.json` at the root lists the two plugins by their folders.
  The name of the marketplace is `charter`, so the plugins are `charter@charter` and `charter-practices@charter`.
- The first version of each plugin in its manifest: 0.1.0. The version lives there only.
- The workflows and the quality checks of this repo run the scripts from `charter/scripts/`.

## Out of scope

Publication in a marketplace of Anthropic. The setup step.

## Acceptance checks

## Automatic checks

1. The two plugins and the marketplace validate. command: `claude plugin validate charter`
   command: `claude plugin validate charter-practices`
2. The tests and the quality checks pass from the new place. command: `python3 -m unittest discover -s tests`
3. The plugins install on this computer from the local marketplace, and the installed core runs the checker.
   command: `claude plugin marketplace add ./ && claude plugin install charter@charter`

## Manual checks

4. The gates of this repo ran from the new place on the change request of this work item: the check "verdict" is green.
   who: the leader. Not automatic: the proof is the check on GitHub.
