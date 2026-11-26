Intent: the HTTP endpoint accepts an event and passes it to the core

Part of #2

This change request adds the intent of the second work item of the thin path (#5): the HTTP endpoint and the start of product as one process. It changes no code.

## What the intent says
- One address accepts an event, `POST /events`, with the four values of an event as JSON.
- The endpoint checks the input at run time. A wrong call gets an error answer and starts nothing.
- `src/main.ts` starts product as a process, with three settings from the environment and the recording channel.
- Ten automatic checks and no manual check.

## Choices that need a decision at the review
- The command that starts product is `node src/main.ts`. Node runs the TypeScript files as they are, so there is no build step. For this, each relative import ends in `.ts`, and the type check refuses syntax that Node cannot run as it is. A test outside the repository showed that this works with the Node version and the TypeScript version of this repo.
- The first rule, "an urgent event gets a knock", is data in `src/main.ts` until the configuration exists (#7).
- The answer to a valid event names the level of the message that went out, or says that no message went out.
- A body of more than 1 MB gets an error answer.
- The process does not start without the path of its record file.
