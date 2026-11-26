# product

product judges when a person is needed in human-in-the-loop scenarios, and then it knocks. A knock is
a push to the person to act now. product serves a human-agent team. In such a team, agents do part of
the work, and a person must be brought in exactly when needed. On-call is the first use case. There an
agent investigates each alert, and product judges whether the engineer on call is needed.

In a human-agent team, a person owns each result. One CTO with three agents is such a team. The first
user is the engineer on call, and the problem is to get alerted only when needed.

product does not start the agent and does not investigate. The monitoring of the team sends product a
copy of each alert. The agent that investigates sends product its steps while it runs, and its result
at the end. product judges when the alert arrives, when the result arrives, and when the time limit
passes. A severe alert gets a knock at once, and full downtime is such an alert. Any other alert waits
for the result of the agent. A result gets a knock, or it gets one message with the evidence, and the
message wakes nobody. A repeat of the same alert sends no second message. When the time limit passes
with no result, product knocks. Each knock carries what the agent found until that moment. A push
through a channel with no encryption carries a short text with no evidence. product records each
judgement with its evidence and the cost of its model calls. A team sets a limit on that cost per day.
At the limit product calls no model, and it knocks.

Rules decide the clear cases: a severe alert, the time limit, and a result that the agent marks
as inconclusive. A model judges the other results and returns a number for its confidence. The model
also reads the knowledge about the services of the team. A threshold turns the number into the action.
The rules and the threshold come with defaults, and each team sets its own.

The monitoring of the team creates the alerts. The repository holds default alert rules as a
configuration template for that monitoring, and a team replaces them with its own. The default alert
rules work only where the services of the team report measurements under the names that the rules use.

A team connects its monitoring and its agent to product once, at setup. A setup agent writes the
configuration, and a knowledge agent writes the knowledge about the services of the team. An engineer
of the team runs both in a coding agent, and reviews and applies the result.

product knocks every time a person is needed and only then. A false positive is a knock that did not
need a person. A false negative is a missed alert, when a person had to receive a knock but did not. On
the scenarios of the product lab the limit for each error is zero. The product lab runs a small
service with seeded defects, and each scenario has a known answer. In the healthy scenarios the known
answer is "no person is needed". Some scenarios stay unseen while the rules and the threshold are
tuned, and the limit holds for them too. The repository publishes both counts as they are. This is the
claim of the on-call use case, and it holds for the lab scenarios only. product promises no zero on
the services of a team.

The first version holds the on-call use case only, with one agent that investigates. It is done when
product runs every lab scenario from alert to action, the count of each error is zero, and the
repository publishes the result.

The first version leaves out:

- The judgement during the run of the agent, and the check of the result against the steps. The first
  version uses the steps only for the content of a knock. The judgement during the run comes in the
  second version. The check of the result against the steps comes later.
- A second use case.
- Actions that change a system. The agent only reads, and product only judges and knocks.
- Use on the services of a real team. The first version runs on the lab service only.
- A schedule of who is on call, and a next person when nobody answers. The first version knocks one
  person.
- Other channels, such as PagerDuty and Slack. The first version has one channel, a push to a phone.
- A user interface.

## Direction

The goal of the current period is the first version. The second version adds the judgement during the
run of the agent. It covers a danger that no alert rule covers, such as a disk that fills in ten
minutes. A second use case comes later.

## Parts

- The core receives the alert, the steps and the result, judges, sends the knock or the message, and
  records each judgement with its cost. Its code has no on-call term in it and uses nothing from a use
  case, and a test checks this. Its first code judges an event with one rule, and the rest is not built
  yet.
- The on-call use case holds the default rules, the default model with its instruction and its
  threshold, the template of alert rules, the lab scenarios and the results. It is not built yet.
- The setup agent and the knowledge agent connect the stack of a team and write the knowledge. They
  are not built yet.

The repository holds the first code of the core, an HTTP endpoint for events and a recording channel
today, and product starts as one process. [`architecture.md`](architecture.md) says how product
is built.
