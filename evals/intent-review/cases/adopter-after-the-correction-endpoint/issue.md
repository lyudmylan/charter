#2 The HTTP endpoint accepts an event and passes it to the core

## Goal
A sender posts an event to product, and the core judges it. product runs as one process.

## In scope
- One address that accepts an event in the form of the four values.
- The check of the input at run time. A call with a missing value or a wrong value gets an error answer and starts nothing.
- The start of product as a process, with the recording channel.
- The HTTP server of Node, with no new package.

## Out of scope
- The token of a sender, the format of Alertmanager, and the steps and the result of the agent: the epic "Events, results and time".
- The script in the package file that starts product: the issue of the commands in this epic.

Intent: `intents/http-endpoint.md`
