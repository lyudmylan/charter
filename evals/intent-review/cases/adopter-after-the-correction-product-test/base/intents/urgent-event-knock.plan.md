# Plan: the core gives an urgent event a knock (#1)

Intent: `intents/urgent-event-knock.md`, checks 1 to 10. The intent, this plan and the code are in one
change request, and the merge by the leader approves the three. This is a decision of the leader of
2026-11-20, and the epic of this work item records it (#5, "Decisions made").

## Steps

1. `src/core/event.ts`: the type of an event. Its state is `"open"` or `"closed"`. Its identity and its
   start time are strings, as the detector gives them, and the core compares them and does not read
   inside them. `urgent` is true or false.
2. `src/core/rule.ts`: the type of a rule. A rule has a name, one condition and an action. A condition
   names one value of the event and the value that it must equal, for example `{ value: "urgent",
   equals: true }`. An action is `"knock"` or `"quiet message"`. A function `matches(rule, event)`
   compares the two values.
3. `src/core/channel.ts`: the interface of a channel and the type of a message. A message holds its
   level, the identity and the start time of its event, and the name of its rule. A channel has one
   operation, `send(message)`. The answer "accepted" or "failed" of a channel comes with #10.
4. `src/core/judge.ts`: the function `judgeEvent(event, rules, channel)`. A closed event gets no
   message. For an open event the first rule of the list that matches decides: the core builds one
   message with the action of that rule as its level and sends it to the channel. With no matching rule
   the core sends nothing. The function returns the message, or nothing.
5. `src/channel/recording.ts`: the recording channel. It receives the path of a file when it is created.
   `send` adds the message to the file as one line of JSON. A function `readMessages(path)` returns the
   messages of the file in the order of the lines, and an empty list when the file does not exist.
6. The tests, with Vitest. Each test has a comment with the intent and the number of its check.
   - `tests/core/judge.test.ts`: checks 1 to 6 and check 10. A channel that keeps its messages in a list stands in
     for a real channel. The rule "an urgent event gets a knock" is data in this file.
   - `tests/channel/recording.test.ts`: check 7, in a temporary folder that the test removes.
   - `tests/core/boundary.test.ts`: checks 8 and 9. Both read each file under `src/core/` and fail when
     they find no file there. Check 8 reads each import and each export with a source: the source must
     be a relative path that stays inside `src/core/`. A package or a module of Node also fails. Check 9
     looks for each term of the list in the text of each file, with no regard to case. The list is in the
     test file, and the text of the change request names its first terms.
7. `docs/architecture.md`, the table of parts: the row "Core" names `src/core/`, and the row "Channel"
   names `src/core/channel.ts` for the interface and `src/channel/` for the channels. The row "Channel"
   gets one sentence: the recording channel writes to a file until the record store exists.
8. `docs/product.md`, the section "Parts": the two sentences that say "not built yet" for the core and
   "the project skeleton" say what exists now.

## Files

`src/core/event.ts`, `src/core/rule.ts`, `src/core/channel.ts`, `src/core/judge.ts`,
`src/channel/recording.ts`, `tests/core/judge.test.ts`, `tests/core/boundary.test.ts`,
`tests/channel/recording.test.ts`, `docs/architecture.md`, `docs/product.md`,
`intents/urgent-event-knock.md`, `intents/urgent-event-knock.plan.md`.

## Choices of the author

- The interface of a channel is a file of the core, because the core calls it. The channels are outside
  the core and import the interface. So check 8 holds, and a new channel needs no change in the core.
- The first rule that matches decides. The order of the list is the order of the rules.
- Check 8 also refuses a package and a module of Node in the core. The core has none today. A later
  work item that needs one changes this check and says why.
- The imports keep the form of the skeleton, with the ending `.js`. The way to start product as a
  process is the subject of #2.
