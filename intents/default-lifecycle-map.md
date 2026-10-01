# Intent: the default lifecycle map in the contract template

Work item: #39. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The contract template of the setup step carries the default lifecycle map: what does the work in each of
the six phases, which built-in ability of Claude Code, and, in `work`, which skill of Charter.

## In scope

- The six phases of the playbook in the template, each with `work` and `builtin`, and the skill of
  Charter where one exists: the tracker skill in Plan.
- The template is the one list of the built-in abilities; `docs/contract.md` points to it.
- `charter.toml` of this repo takes the same six phases, because Charter follows its own contract.

## Out of scope

A gate on the map.

## Acceptance checks

## Automatic checks

1. The template names the six phases, and the checker accepts it.
   test: `tests/test_setup.py::Templates.test_lifecycle_map_has_the_six_phases`

## Manual checks

2. The map reads as the plan of a real project, not as theory. who: the leader. Not automatic: a judgment on the text.
