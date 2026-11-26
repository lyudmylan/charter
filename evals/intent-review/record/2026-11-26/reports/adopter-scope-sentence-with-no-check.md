<!-- charter-intent-review -->
Commit: b9b281bc9c2dda4c143d066b8cdf33d222439872

| Intent | Verdict | Finding |
|---|---|---|
| `intents/http-endpoint.md` | approve with a change | No check verifies the success body when a message goes out. Some promised behaviour has no check, and the claim about `erasableSyntaxOnly` is too broad. |

The epic #5 could not be read, so consistency with its decisions is not checked.

**1. high**: `intents/http-endpoint.md`, check 1. An endpoint that always answers "no message went out" can pass the listed checks: check 2 expects that answer, and checks 1 and 9 do not read the body of a successful call.
- Sentence: "A `POST /events` with an open urgent event gets the answer 200, and the channel holds one knock with the identity and the start time of that event."
- Proposed: "A `POST /events` with an open urgent event gets the answer 200, its JSON body names the level of a knock, and the channel holds one knock with the identity and the start time of that event."

**2. medium**: `intents/http-endpoint.md`, "In scope", `tsconfig.json`. `erasableSyntaxOnly` does not refuse an import of a type that lacks the word `type`. Without `verbatimModuleSyntax`, the type check accepts it. Vitest can also pass, but `node src/main.ts` fails when it loads such an import by name. Check 9 covers only the files that the process loads.
- Sentence: "`tsconfig.json` gets `allowImportingTsExtensions` and `erasableSyntaxOnly`. The second one makes the type check refuse syntax that Node cannot run as it is."
- Proposed: "`tsconfig.json` gets `allowImportingTsExtensions`, `erasableSyntaxOnly` and `verbatimModuleSyntax`. The last two make the type check refuse syntax that Node cannot remove, and an import of a type without the word `type`."

**3. medium**: `intents/http-endpoint.md`, checks 9 and 10. No check covers the default host, the default port or SIGINT. The token is out of scope, so a process that listens on all addresses by default would let other computers send events, and it could still pass check 9.
- Sentence: "On SIGTERM the process ends with the exit code 0."
- Proposed: "With `PRODUCT_HOST` not set, the line ends with `http://127.0.0.1:<port>`. On SIGTERM the process ends with the exit code 0; the test starts it a second time and shows the same for SIGINT." Also add this automatic check: "With `PRODUCT_PORT` not set, the process uses the port 8080. test: `tests/process.test.ts::the default port is 8080`". The test can check a function that reads the settings, so it does not need a free port 8080.

**4. medium**: `intents/http-endpoint.md`, checks 4 to 7. The scope says "The error answer is JSON and names the reason", but only check 3 asks for any content in an error answer, and it does not ask for JSON. Check 4 also leaves out an empty `startTime`, although the scope requires text that is not empty.
- Sentence: "A wrong value gets the answer 400 and the channel holds no message: a state that is not `"open"` or `"closed"`, an identity that is empty, a start time that is a number, and `urgent` as text."
- Proposed: "A wrong value gets the answer 400 and the channel holds no message: a state that is not `"open"` or `"closed"`, an identity or a start time that is empty or a number, and `urgent` as text. In checks 3 to 6, each error answer is JSON and names the reason."

**5. low**: `intents/http-endpoint.md`, "In scope". "1 MB" can mean 1,000,000 or 1,048,576 bytes, so the limit is not exact.
- Sentence: "A call with a missing value, a wrong value, a body that is not JSON, or a body of more than 1 MB gets an error answer and starts nothing."
- Proposed: "A call with a missing value, a wrong value, a body that is not JSON, or a body of more than 1,048,576 bytes gets an error answer and starts nothing."

Highest open severity: high