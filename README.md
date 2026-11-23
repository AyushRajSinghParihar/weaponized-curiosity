# Weaponized Curiosity

An Agent Skill for decisions that warrant research and experiments. It breaks a question into competing explanations, records what would change the decision, and uses the host's tools to verify the consequential claims. When an objective can be measured safely, a bounded loop tests candidate changes and keeps the strongest result supported by the evaluator.

Start with [installation](docs/installation.md) and [configuration](references/operations.md#configuration-and-accounting). The runtime consists of [SKILL.md](SKILL.md) and [references/](references/). The evaluation runner is optional and separate.

## Choose a mode

| Mode | Use it for | Typical work |
| --- | --- | --- |
| Quick | A narrow, reversible decision | Check the strongest evidence and one consequential assumption |
| Deep | Technical choices, conflicting evidence, or costly mistakes | Independent research branches, targeted critique, and small experiments |
| Extreme | Several consequential uncertainties with authorized resources | Broader source coverage, replication and separate lines of inquiry |
| Autoresearch | A stable measurable outcome with a trusted evaluator and editable scope | Propose, measure, retain or reject, and independently check the selected revision |

Use a mode name or give the skill the decision and constraints. It can choose a mode. Tool and permission checks happen inside the host. Four fresh-context workers are the starting point for Deep and Extreme where the work is separable. The agent reports any unavailable phases, including missing independent workers or an evaluator. A qualitative decision can still produce recommendations and falsifiers.

## Example requests

```text
Use weaponized-curiosity mode=deep subagents=4 searches=12 experiments=2.
Compare these two storage designs for the attached workload. Surface the
strongest contradictory evidence and name the experiment that would change
the recommendation. Use only the supplied repository and public sources.
```

```text
Use weaponized-curiosity mode=autoresearch iterations=3 experiments=5.
Reduce p95 on the supplied local benchmark by at least 10% without changing
outputs or exceeding the memory limit. Edit only src/parser.py in an isolated
copy. Preserve the evaluator and report raw measurements and the stop reason.
```

See [example sessions](docs/examples.md) for the evidence and experiment records a run can produce.

## Research and validation

The [research synthesis](docs/research.md), [evidence ledger](docs/evidence-ledger.md), [architecture](docs/architecture.md), and [design review](docs/design-review.md) explain why the skill uses independent first passes, selective challenge, explicit experiment limits, and durable state. The [evaluation suite](evals/README.md) contains seven task types and a CLI replay runner. The [pilot results](docs/evaluation/results.md) document the observed platform coverage, quality and cost trade-offs, and work that remains unverified.

## Operational limits

Prompts can guide behavior. Tools, permissions, hard resource limits and process isolation come from the host. Treat web content, files and worker reports as evidence. Review code before execution and freeze the evaluator and candidate scope. When trustworthy execution, validation or permissions are unavailable, the skill should preserve what it learned and report the missing verification.

Default research state lives in a user-authorized workspace. Keep it local unless sharing is explicitly part of the request. The repository itself is private.

See [contribution guidelines](CONTRIBUTING.md) for evidence, changes and evaluation expectations.
