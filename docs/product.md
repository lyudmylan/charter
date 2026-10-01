# Charter

Engineering discipline framework for human-agent teams: the AI-native software
development lifecycle, through the eyes of the engineering leader. This version is built
for Claude Code. The contract stays in open formats, so that other agent runtimes can
read it later.

## Purpose

An engineering leader is accountable for two outcomes: the organization delivers, and
production does not break. Charter removes the human as a bottleneck, step by step,
while the human stays in control and keeps full ownership of the result. It covers the
people and agents that build the software, not an agent inside a product. It answers
three questions:

1. What must be true before a change moves forward, whoever did the work?
2. Who decides what: a leader, a team lead, an engineer, an agent?
3. How do a leader and a human team keep a true picture of the software and the rules,
   without approving every step?

## How it works

- The **contract** is a file with the rules, the owner of each rule, and the rights of
  each role. Example: "a change to payment code needs the approval of a person". The rules
  of the organization live in their own repo. A repo contract references that repo by
  address and version; it holds no copy. The checker compares the two.
- A **gate** is a check that must pass before the next step. It is a deterministic
  script that checks the result, not the method.
- An **acceptance check** states what "it works" means for one work item, in a form that
  a script can run. It is part of the [intent](../intents/) of the work item, and a person
  approves it before the work starts.
- A **risk tier** says how dangerous a change is, for example low or high. It sets the
  depth of the review and who approves.
- The **evidence record** keeps what each gate found for every change, and the cost.
  A person examines a sample, not every step.
- **Stop rules** return control to a person: limits on loops and on repeated refusals,
  and one switch that stops all agents.

A rule belongs to the organization, a team, a repository, or a person. A lower owner can
make a rule stricter, but cannot weaken a locked rule; a locked limit is exact, because
the number of rounds before a person steps in is a policy. Only a person changes the
contract. A repository declares its issue tracker, code host, CI, and release stages, so
Charter fits any set of tools.

## Who does the work

Two types of actor: a person with an agent, and an agent that works autonomously. Every
actor has an identity, a boundary (what it can touch), and decision rights. A person has
them already; an agent must get them. Accountability always stays with a person. The
contract holds one table of roles and rights for all actors; the code host and Claude
Code enforce it. Separation of duties holds at every size: the author of a change is not
its reviewer. A larger organization changes who holds a role, not the rules.

## The lifecycle map

The phases are the six of the AI-native SDLC playbook of Anthropic (2026-08-21). The map says what
Charter adds in each phase.

| Phase | Artifacts of Charter | Verification | Included in Charter |
|---|---|---|---|
| Plan | `product.md`: the direction. The [intent](../intents/) of a work item: goal, in scope, out of scope, acceptance checks. The issue tracker: milestone, epic, issue. | A person approves the intent through a change request. | Yes |
| Design | The design spec of the work item. The architecture map, kept current. | A person approves the design spec. | Roadmap |
| Build | `plan.md`, accepted before the code. The change on a branch. The repository instructions. The gates, as code. | The plan exists before the code. The quality checks pass before the push. | Yes |
| Test | The acceptance checks, which the agent cannot change alone. The tests. The evals of the skills. | A reviewer that is not the author. The check "verdict". | Yes |
| Deploy | The evidence record. The merge by the approver of the risk tier. The release stages to production. | A person decides production. | Partly |
| Maintain | A failure re-enters the cycle as an intent and ends as a check. Each model upgrade is tested. | Monitoring. | Partly |

Every phase has its own verification. The issue tracker connects all phases, from the plan to
production and back.

## Principles

1. The organization owns the gates. The team owns the skills.
2. Autonomy of an agent is a grant: given by risk tier, extended by evidence, withdrawn
   after a failure.
3. Every failure becomes a check. Every model upgrade is tested.
4. Built-in first, then install, then build.
5. A skill carries only what the model cannot know. Its cost is measured.
6. Charter follows its own contract.

## Packaging

Charter ships as two plugins.

- `charter` holds the contract, the gates, the agent boundary, the stop rules, the
  evidence record, and the setup step: one command sets a repo up.
- `charter-practices` holds a small number of light skills. It needs `charter`, because
  its skills read the contract.
- An organization with its own skills installs `charter` and maps its skills to the
  phases of the lifecycle.
- The lifecycle map states, for every phase, what does the work, and names each built-in
  ability of Claude Code that Charter uses.
