# Plan: a run of an agent writes no attribution line of a tool (#124)

Intent: `intents/no-attribution-line.md`, checks 1 to 5.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. A test on the computer of the author, with a local server in the place of the model: Claude Code, started
   as a run starts it, prepares a request that holds the instruction for the line with empty settings, and
   none with the key `attribution`. It decided step 2.
2. `charter/scripts/charter_check.py`, the function `boundary_settings`: the key `attribution` with an
   empty text for `commit` and for `pr`, with its reason at the name of the key.
3. `charter/scripts/charter_run.py`, the function `text`: a line that names a tool as the author is left
   out, with the pattern and its reason next to the pattern of the closing line. The help text of the
   command says it.
4. `docs/contract.md`: the settings in the section "The boundary of a run"; the publishing step in the
   section "The run".
5. Both manifests: 0.3.18.
6. Tests: `Settings.test_the_settings_switch_the_attribution_off` in `tests/test_boundary.py`;
   `Publish.test_the_text_holds_no_line_that_names_a_tool_as_the_author` and
   `Documents.test_the_documents_and_the_version_carry_the_attribution` in `tests/test_run.py`.
7. `tests/product.py`: the step "settings of a run" asks for the key; the sample text of the agent ends
   with the line of the tool, and the step "text of a change request of a run" asks that it is gone.
8. A test workflow on its own branch, not for the main branch, on a machine of the code host: check 5.
   Its result goes to a comment on #124. The branch is removed after the test.
9. `plans/no-status-line.md`, step 2: one sentence leaves. It gave a rule of the plan gate that does not
   exist: the gate reads the intents that the linked issue names, not each intent that a change touches.

## Files

- `charter/scripts/charter_check.py`
- `charter/scripts/charter_run.py`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `intents/no-attribution-line.md`
- `plans/no-attribution-line.md`
- `plans/no-status-line.md`
- `tests/test_boundary.py`
- `tests/test_run.py`
- `tests/product.py`

## Not changed

The run workflow and its template: the settings and the text come from the scripts. The brief of the
agent: the settings take the instruction away, and the script is the guard.
