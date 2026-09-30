# Scenario: the four gates

Work item: #4. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. Each gate has a passing sample and a failing sample, and the tests run with one command.
   test: `tests/test_charter_gate.py::Link.test_open_linked_issue_passes`
   test: `tests/test_charter_gate.py::Link.test_no_linked_issue_fails`
   test: `tests/test_charter_gate.py::Documents.test_document_changed_with_code_passes`
   test: `tests/test_charter_gate.py::Documents.test_code_changed_without_document_or_reason_fails`
   test: `tests/test_charter_gate.py::Quality.test_passing_commands_pass`
   test: `tests/test_charter_gate.py::Quality.test_failing_command_fails_and_names_it`
   test: `tests/test_charter_gate.py::Verdict.test_ready`
   test: `tests/test_charter_gate.py::Verdict.test_not_ready_names_each_reason`
   command: `python3 -m unittest discover -s tests`
2. The verdict script prints one line, "ready" or "not ready", then the reasons, and exits 0 or 1.
   test: `tests/test_charter_gate.py::Verdict.test_first_line_is_the_verdict_and_exit_code_matches`
3. No gate needs a model call. test: `tests/test_charter_gate.py::NoModel.test_the_gate_script_imports_no_network_or_model_library`

## Manual checks

None.
