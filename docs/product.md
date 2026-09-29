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
  each role. Example: "a change to payment code needs the approval of a person".
- A **gate** is a check that must pass before the next step. It is a deterministic
  script that checks the result, not the method.
- An **acceptance check** states what "it works" means for one work item, in a form that
  a script can run. A person approves it before the work starts.
- A **risk tier** says how dangerous a change is, for example low or high. It sets the
  depth of the review and who approves.
- The **evidence record** keeps what each gate found for every change, and the cost.
  A person examines a sample, not every step.
- **Stop rules** return control to a person: limits on loops and on repeated refusals,
  and one switch that stops all agents.

A rule belongs to the organization, a team, a repository, or a person. A lower owner can
make a rule stricter, but cannot weaken a locked rule. Only a person changes the
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

| Phase | Verification | Record in the issue tracker | Included in Charter |
|---|---|---|---|
| Direction | A person approves | Milestone and epics | Yes |
| Plan | A person approves the acceptance checks | Issue with the acceptance checks | Yes |
| Design | To decide | Design decision, linked to the issue | Roadmap |
| Build | The acceptance checks pass | Change, linked to the issue | Yes |
| Review | A reviewer that is not the author | Findings that were not corrected | Yes |
| Merge | One verdict; approval by risk tier | The issue closes | Yes |
| Release | A check for each stage; a person decides production | The release lists its issues | Roadmap |
| Operate | Monitoring | An incident becomes an issue | Roadmap |
| Improve | Tests of the skills; audit of stale rules | A failure becomes an issue, then a check | Partly |

Every phase has its own verification. The issue tracker connects all phases, from
direction to production and back.

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

- `charter` holds the contract, the gates, the agent boundary, the stop rules, and the
  evidence record.
- `charter-practices` holds a small number of light skills. It needs `charter`, because
  its skills read the contract.
- An organization with its own skills installs `charter` and maps its skills to the
  phases of the lifecycle.
- The lifecycle map states, for every phase, what does the work, and names each built-in
  ability of Claude Code that Charter uses.
