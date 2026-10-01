# Scenario: the tracker skill, from the practice of iteration 1

Work item: #7. Approved by a person on 2026-10-01, in the work item.

## Automatic checks

1. The skill is under 40 lines, and its description says when to use it and when not.
   test: `tests/test_skills.py::TrackerSkill.test_size_and_description`
2. The three eval cases pass with the skill, and the control case shows that the skill does not act on an
   unrelated request. command: `claude plugin eval charter-practices --trust-plugin --max-cost-usd 3`
   The run of 2026-10-01: 3 of 3 cases pass, overall score 1.0, the skill adds 0.5 on average, the
   control case is silent in 3 of 3 runs. Estimated cost at list price 1.63 USD, 392 seconds.

## Manual checks

3. The skill holds only knowledge that the model cannot have: the conventions of this organization, no
   general how-to text. who: the leader. Not automatic: a judgment on the text.
