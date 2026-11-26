# Intent: the core gives an urgent event a knock

Work item: #1. Approval: a person merges the change request that adds this file.

## Goal

The core judges an event with the rules that it receives, an urgent event gets a knock through the
interface of a channel, and a recording channel writes that knock where a test can read it.

## In scope

- `src/core/`: the first code of the core.
  - An event with the four values of `docs/architecture.md`: its state (open or closed), its identity,
    its start time, and whether it is urgent.
  - A rule as data. A rule has a name, a condition on the values of an event, and an action: a knock or
    a quiet message. A condition is a plain value that the core reads: a comparison of one value of the
    event with a given value. It is no function. A richer condition comes with the configuration (#7).
    The core holds no rule in its code. It receives the list of rules with each call.
    The action "quiet message" is in this work item because the interface of a channel has the two
    levels, and one check shows that the core can send the lower one.
  - The judgement at the moment "the event arrives". The core applies the rules to an open event. When one
    or more rules match, the first rule of the list that matches decides, and the core sends one message
    to the channel. The message holds its level, the identity
    and the start time of its event, and the name of the rule that decided.
  - An event whose state is closed gets no message. An event that no rule matches gets no message in
    this work item.
  - The interface of a channel, with two levels: a knock and a quiet message. The core calls a channel
    through this interface only.
- `src/channel/`: the recording channel. It sends no push. It writes each message as one line to a file
  that it receives when it is created, in the order of arrival, and a reader gets the messages back from
  that file. The test of the product (#3) reads this file.
- The first rule, as data in the tests: "an urgent event gets a knock".
- Two checks that hold for each later change of the core:
  - The code of the core imports no file outside `src/core/`.
  - The code of the core holds no term of the on-call use case. The list of the terms is in
    `tests/core/boundary.test.ts`. The review of the change that adds that test checks the first list
    against the terms that the text of the change request of this intent names.
- `docs/architecture.md`: the rows "Core" and "Channel" of the table of parts name their folders. The
  row "Channel" says that the recording channel writes to a file until the record store exists (#8).
- `docs/product.md`: the part "Core" and the sentence about the skeleton say what exists now.

## Out of scope

The state of an event across calls: the same event, a repeat of an open event, and the moment when the
detector closes it (#6). The file format of the configuration and the defaults of the on-call use case
(#7). The record store; the recording channel writes to a file until the record exists (#8). The model
and the threshold (#9). A push to a phone (#10). The HTTP endpoint and the start of product as a process
(#2). The evidence in a knock: it comes with the steps and the result of the agent (#6).

## Acceptance checks

## Automatic checks

1. With the rule "an urgent event gets a knock", an open urgent event gets one knock on the channel.
   test: `tests/core/judge.test.ts::an open urgent event gets one knock`
2. With the same rule, an open event that is not urgent gets no message.
   test: `tests/core/judge.test.ts::an event that is not urgent gets no message`
3. With the same rule, an urgent event whose state is closed gets no message.
   test: `tests/core/judge.test.ts::a closed event gets no message`
4. With an empty list of rules, an open urgent event gets no message. The core holds no rule in its code.
   test: `tests/core/judge.test.ts::with no rule an urgent event gets no message`
5. A rule whose action is a quiet message gives a matching event one quiet message and no knock.
   test: `tests/core/judge.test.ts::a rule with the action quiet message sends a quiet message`
6. The knock holds the identity and the start time of its event, and the name of the rule that decided.
   test: `tests/core/judge.test.ts::a knock names its event and its rule`
7. The recording channel writes a knock and a quiet message in the order of arrival, and a reader gets
   the same two messages back from the file.
   test: `tests/channel/recording.test.ts::a reader gets the messages back in the order of arrival`
8. The code of the core imports nothing outside `src/core/`: no file, no package, no module of Node.
   test: `tests/core/boundary.test.ts::the core imports no file outside the core`
9. No file under `src/core/` holds a term of the list, in code or in comments, with no regard to case.
   test: `tests/core/boundary.test.ts::the core holds no term of the on-call use case`
10. With two matching rules, a quiet message first and a knock second, the event gets one quiet message
    and no knock.
    test: `tests/core/judge.test.ts::the first matching rule decides`

## Manual checks

None.
