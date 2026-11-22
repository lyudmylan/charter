# Plan: the change request of a run holds the line that closes its issue one time (#116)

Intent: `intents/one-closing-line.md`, checks 1 to 6.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. `charter/scripts/charter_run.py`: the command `text`, with `--number` and `--request`. It reads the
   file with the function that follows no link, leaves out each line that only links the issue of the
   run, and prints the closing line, an empty line, and the rest, or the sentence when nothing is left.
   The pattern of a link comes from the facts collector, so the two scripts read a link in the same way.
2. `charter/templates/run.yml` and `.github/workflows/run.yml`, the publishing step: one call of the
   command in the place of the shell lines that wrote the text.
3. `docs/contract.md`, the section "The run": the command in the list, and one sentence in step 10.
4. Both manifests: 0.3.17.
5. Tests in `tests/test_run.py`: `Publish.test_the_text_holds_the_closing_line_one_time`,
   `Publish.test_a_link_in_the_place_of_the_text_is_not_followed`,
   `Publish.test_the_published_text_closes_the_issue_one_time`, and
   `Documents.test_the_documents_and_the_version_carry_the_closing_line`. The helper of the class `Publish`
   gives the step the folder of the scripts.
6. `tests/product.py`: the step "text of a change request of a run".

## Files

- `charter/scripts/charter_run.py`
- `charter/templates/run.yml`
- `.github/workflows/run.yml`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `tests/test_run.py`
- `tests/product.py`
- `intents/one-closing-line.md`
- `plans/one-closing-line.md`

## Not changed

`docs/product.md`: the product does the same work, and the change request says so with the line
`No document change`.
