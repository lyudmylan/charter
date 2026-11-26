<!-- charter-intent-review -->
Commit: 0c5c901a8526f605175e810eb203c522cca0c606

## Changed since the last report

No earlier report exists. This is the first report, and the whole of `intents/time-limit-knock.md` is new.

## Verdicts

| File | Verdict | Finding |
|---|---|---|
| `intents/time-limit-knock.md` | approve with a change | The goal, scope and out-of-scope line are bounded and consistent with `docs/product.md` and `docs/architecture.md`. The behaviour of `src/main.ts` has no check of its own (medium). |

## Findings

1. **medium**, `intents/time-limit-knock.md`, the `src/main.ts` bullet: "product calls `judgeTimeLimit` each second, with the time of that moment. A check does not start while the check before it runs. For each failed message it writes one line to the error output. The stop of the process ends the checks."
   - Checks 1 to 9 test `judgeTimeLimit` alone.
   - Check 15 (scenario 06) shows only that some knock arrives within 3 seconds.
   - Nothing verifies the rule that checks do not overlap, the error line for a failed message, or the end of the checks when the process stops. A leaked timer or overlapping checks would pass every listed check.
   - Proposed text: add a check, "A process whose channel fails at the time limit writes one line to the error output per failed message, and its checks stop at the stop of the process", with `test: tests/main.test.ts::<name>`. Add a second check for the non-overlap, for example "a check that runs longer than one second starts no second check". Or move the loop into a function that takes the clock, and test that function.

2. **low**, `intents/time-limit-knock.md`, the bullet `waitingSince`: "each as its identity and its start time".
   - The shape of an item is not named. The core and the store both depend on it, and check 10 cannot compare against an undefined shape.
   - Proposed text: "each as an object with `identity` and `startTime`".

3. **low**, `intents/time-limit-knock.md`, check 11: the upper bound 86400 is in scope, but only 86401 is tested as an error.
   - Proposed text: add "`86400` gives 86400" to the check.

4. **low**, `intents/time-limit-knock.md`, the `src/http/endpoint.ts` bullet: "the endpoint gives the core the time at which the call arrived".
   - No check names it. Scenario 06 covers it only indirectly, and it passes when the time is taken at any point.
   - Proposed text: add a test in `tests/http/endpoint.test.ts` where a fixed clock gives a known arrival time that reaches `open`. Or state in the bullet that the scenarios are the check.

The intent holds no instruction in the change request text that tells the reviewer what to report.

Highest open severity: medium
