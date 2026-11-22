# Plan: the boundary of a run without a person (#91)

Intent: `intents/boundary-of-a-run.md`, checks 1 to 15. The leader merged the intent on 2026-11-20.
Accepted by the leader in the conversation on 2026-11-20, before the code.
Check 16 is manual and belongs to the first run of #92.

## What the documentation of Claude Code changed in the design

Read on 2026-11-20: the pages on the sandbox, the permissions, and the settings reference.

- On Linux the write lists of the sandbox honour a wildcard only as a trailing `/**`. A pattern with
  another wildcard goes into the sandbox as the files that match it at the time the settings are
  written. A pattern that no file matches yet gives no entry in the sandbox; the deny rule of the file
  tools and the gate still cover it.
- A deny rule for a folder cannot be opened again for one file inside it. So a pattern that covers the
  plan files, such as `intents/**`, is written as the files under it that are not plan files, in both
  layers. A new file under the pattern is caught by the gate.
- A relative path in settings from the command line has no stated base. Each path in the settings is
  absolute, from the folder of the contract. The settings are valid for one checkout, which fits the
  decision that they are written at the start of each run.
- The refusal of a call that needs a question is one key, `permissions.denyInsteadOfPrompting`. It
  needs Claude Code 2.1.319 or later; #92 names the version that the run installs.
- `sandbox.network.strictAllowlist` is documented for user and managed settings only. The settings carry
  it, and the refusal key covers a host that it does not. The manual check 16 shows which one acts.

## Steps

1. `charter/schema/contract.toml`: the fields `boundary.no_write` and `boundary.no_read`, kind `set`,
   each with a note. The schema version stays 1.
2. `charter/scripts/charter_check.py`:
   - A function `files_under(root, pattern)`: the walk that `absent_hits` has today, moved out so that
     both uses share it. `absent_hits` calls it and keeps its result.
   - A function `is_plan(path)`: a file `intents/<part>.plan.md`. The two name constants move here from
     `charter_gate.py`, which reads them from the checker.
   - A function `boundary_settings(e, root)` that returns the settings as a table:
     `permissions.denyInsteadOfPrompting` true; `permissions.deny` with one `Edit(//<path>)` rule for each
     entry of `boundary.no_write` and one `Read(//<path>)` rule for each entry of `boundary.no_read`;
     `sandbox.enabled` true, `sandbox.failIfUnavailable` true, `sandbox.allowUnsandboxedCommands` false;
     `sandbox.filesystem.denyWrite` and `denyRead` with the same paths; `sandbox.network.allowedDomains`
     empty and `strictAllowlist` true; `sandbox.credentials.envVars` with the mode `deny` for the tokens
     of the model (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`) and of the code
     host (`GITHUB_TOKEN`, `GH_TOKEN`, `ACTIONS_RUNTIME_TOKEN`, `ACTIONS_ID_TOKEN_REQUEST_TOKEN`,
     `CHARTER_ORG_TOKEN`). The names are one list at the top of the script.
   - The translation of one pattern, one function: a path without a wildcard stays one path; `dir/**`
     that covers no plan file becomes the folder; each other pattern becomes the files that match it now,
     without the plan files.
   - A command `boundary CONTRACT`, with `--source` and `--cache-dir` as `check` has them. It prints the
     table as JSON. A contract that fails its check prints the failures and no settings.
   - The text at the top of the script names the command.
3. `charter/scripts/charter_gate.py`: a gate `boundary --contract C --changed FILE`. It reads one path
   on each line, drops empty lines, and reads each path without its dot segments. A path that is
   absolute or that leaves the repo fails. A plan file passes. A path under a pattern of
   `boundary.no_write` fails with the message "`{path}`: a run without a person cannot change this path,
   a pattern of `boundary.no_write`. A person makes this change, in its own change request." The gate
   reads the effective contract, with the organization source, so that a locked minimum counts.
4. `charter/templates/charter.toml`: a table `[boundary]` with
   `no_write = ["charter.toml", "AGENTS.md", "CLAUDE.md", "intents/**", ".github/**", ".claude/**"]` and
   `no_read = [".env", ".env.*", "**/.env", "**/.env.*"]`, and a comment that a repo adds its package
   files. `charter_setup.py` does not change: the values are fixed text of the template.
5. `charter.toml` of this repo: the same table. This is a change of a contract, and the merge by the
   leader approves it.
6. `charter/templates/AGENTS.md` and `AGENTS.md`, under "How a change moves", one rule line: "A run of
   an agent without a person does not change the files that the contract closes to it. A person makes
   such a change, in its own change request. [boundary.no_write]"
7. `docs/decisions.md`, section E: the rows E7 to E10 with the four decisions of the intent and their
   reasons, dated 2026-11-20, and one sentence in the row E4: "For a run without a person, E8 replaces
   the conformance check."
8. `docs/contract.md`: the two fields in the table of fields; a short section "The boundary of a run"
   with the command, the gate, and the two limits of the sandbox from the top of this plan; one sentence
   says that the fields need the version 0.3.6 of the core.
9. `docs/product.md`, section "Who does the work", two sentences: an agent that works with no person
   present cannot change the contract, the instructions, an approved intent, or the workflows, and it
   holds no credential of the code host. A script publishes its result after a check of what it changed.
10. Both manifests: 0.3.6.
11. `intents/boundary-of-a-run.md`: `Status: done`, and in check 16 "names both refusals" becomes "names
    the refused write and the refused network access", the open low finding of review round 3.
12. `tests/test_boundary.py`, new, with the four classes and the tests that the intent names:
    - `Fields`: 2 tests. The locked pattern uses an organization file in a temporary folder, as the
      lock tests of `tests/test_charter_check.py` do.
    - `Settings`: 8 tests, on the table that `boundary_settings` returns for a temporary repo, and one
      of them on the output of the command. The forms of the translation each have a case: a path, a
      folder, a pattern with a wildcard in the middle, a pattern with no file, a pattern that covers
      the plan files.
    - `Gate`: 5 tests, through the command with a file of changed paths.
    - `Defaults`: 6 tests, on a repo that the setup step made in a temporary folder, on the two
      instruction files, the decision record, the manifests, and the product document.
    `tests/test_charter_gate.py` and `tests/test_charter_check.py` change only where a constant moved.

## Files

- `charter/schema/contract.toml`
- `charter/scripts/charter_check.py`
- `charter/scripts/charter_gate.py`
- `charter/templates/charter.toml`
- `charter/templates/AGENTS.md`
- `charter.toml`
- `AGENTS.md`
- `docs/decisions.md`
- `docs/contract.md`
- `docs/product.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `intents/boundary-of-a-run.md`
- `intents/boundary-of-a-run.plan.md`
- `tests/test_boundary.py`
- `tests/test_charter_gate.py`
- `tests/test_charter_check.py`

## What this plan does not do

It runs no Claude Code. The tests read the settings as data. Whether a runner starts the sandbox, and
whether each key acts as the documentation says, is the manual check 16 in the first run of #92.
