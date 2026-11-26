# Claude Code instructions

@AGENTS.md

`docs/product.md` is the product source of truth; ground planning and scope decisions in it.
The repo follows Charter: the contract is `charter.toml`, the rules are in `AGENTS.md`.

Rules that matter in this repo:

- product judges and knocks. It does not start the agent of a team and does not
  investigate (product.md). Rules decide the clear cases, and a model with a threshold
  judges the other results.
- The code of the core does not include specifics of a use case. The rules, the threshold and the
  instruction for the model are configuration. An event format, a channel and a model
  each sit behind an interface outside the core (docs/architecture.md).
- Public register from the first commit: no private material, no names of other projects
  of the organization. The text checks of the contract enforce it.
