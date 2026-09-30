# Charter

[![tests](https://github.com/lyudmylan/charter/actions/workflows/tests.yml/badge.svg)](https://github.com/lyudmylan/charter/actions/workflows/tests.yml)
[![verdict](https://github.com/lyudmylan/charter/actions/workflows/verdict.yml/badge.svg)](https://github.com/lyudmylan/charter/actions/workflows/verdict.yml)

Engineering discipline framework for human-agent teams: the AI-native software development
lifecycle, through the eyes of the engineering leader. This version is built for Claude Code.

Charter is a written contract and the checks that enforce it. The organization owns the gates,
the team owns the skills, and a person stays in control without approving every step.

## Documents

| Document | Content |
|---|---|
| [`docs/product.md`](docs/product.md) | What Charter is and why |
| [`docs/contract.md`](docs/contract.md) | The contract files, their fields, and the checker |
| [`AGENTS.md`](AGENTS.md) | The rules for work in this repo |
| [`tests/scenarios/`](tests/scenarios/) | The acceptance checks of each part |

## Layout

| Path | Content |
|---|---|
| `charter.toml` | The contract of this repo |
| `schema/contract.toml` | The schema of a contract: fields, kinds, directions |
| `scripts/charter_check.py` | The checker. Python 3.11 or later, standard library only. |
| `scripts/charter_gate.py` | The gates of a change: link, documents, quality, verdict |
| `scripts/charter_facts_github.py`, `.github/workflows/` | The gates on GitHub: the only parts that know the code host |
| `tests/` | The tests, the sample files, and the scenarios |

## Checks

Before a push, two commands: `python3 scripts/charter_gate.py quality --contract charter.toml` runs the
quality checks that `charter.toml` lists, and `python3 scripts/charter_check.py all charter.toml` runs
the contract checks.

The checker reads the organization source from a local cache. `docs/contract.md` says how to populate it.

## License

Apache 2.0. See `LICENSE` and `NOTICE`.
