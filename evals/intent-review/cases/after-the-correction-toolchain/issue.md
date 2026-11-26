#88 The tests workflow installs what the quality commands of the contract need

## Goal
A repo whose quality commands need an install step gets a `tests` workflow that works from the setup step, and the install step has one declared place.

The template `charter/templates/tests.yml` checks out the code, fetches Charter at the version of the contract, and runs the quality commands of the contract. That is enough for a repo with no install step, such as this one. In 2026-11 an adopter with a TypeScript toolchain added three steps by hand to the written workflow: the package manager, the runtime, and the install of the dependencies. The contract names the quality commands, and nothing names what they need first. A later run of the setup step, or a new version of the template, does not know these steps.

## In scope
- A declared place for the toolchain of the repo. The intent decides its form: a field of the contract, or a marked block of the workflow that the setup step and a later update leave in place.
- The setup step takes the toolchain as a flag or asks for it. When none is given, the written workflow is the one of today.
- The install step runs in the workflow `tests`, which runs the code of the change request and holds no secret, and in the workflow of a run (#92), before the agent starts.
- The three workflow templates and the workflows of this repo move from `actions/checkout@v4` to the current major version (v7 on 2026-11-19).
- `docs/contract.md`: the place and how the setup step uses it.
- Tests: a written workflow with a declared toolchain holds its steps before the quality step; a repo with none gets the workflow of today; a test refuses an old version of the checkout action in a template.

## Out of scope
- A cache of the dependencies.
- A CI other than GitHub Actions.
- One template for each language.

Intent: `intents/toolchain-in-the-tests-workflow.md`
