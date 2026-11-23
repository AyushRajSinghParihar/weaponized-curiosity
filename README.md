# Weaponized Curiosity

![A black linocut raven inspecting a red pebble.](assets/readme-banner.jpg)

Use Weaponized Curiosity when you want your agent to research a question, compare options, or test an idea before you commit to it. Give it the question in your own words.

> Use Weaponized Curiosity to research whether we should keep our Postgres job queue or move to a dedicated broker. Use our current workload and tell me what would make switching worthwhile.

That’s a complete prompt. The skill starts with the evidence most likely to change the answer. It can dig deeper if it finds a consequential gap. Add a mode or budget when you have one in mind.

## Install

Run this from your project and choose Codex, Claude Code, or both.

```sh
npx skills add AyushRajSinghParihar/weaponized-curiosity --skill weaponized-curiosity
```

You can ask for the skill by name or invoke it with `$weaponized-curiosity` in Codex and `/weaponized-curiosity` in Claude Code. The manual install only needs Git. [Installation guide](docs/installation.md)

## Make it your go-to for research

If you want to be able to say “research this,” put a line like this in your project instructions. Use `AGENTS.md` for Codex or `CLAUDE.md` for Claude Code.

> When I ask you to research something or compare options using evidence, use `weaponized-curiosity`.

## When to pick a mode

| Mode | When I’d use it |
| --- | --- |
| **Quick** | Check a claim, compare two options, or see whether a plan meets a hard requirement. |
| **Deep** | Work through conflicting evidence or a consequential decision. The agent can split the research among up to four independent workers where supported, then compare what they found. |
| **Extreme** | Give a difficult question more time for source review, competing explanations, and replication. |
| **Autoresearch** | Improve something you can measure. Set a target and a trial limit, then let the agent test changes against a fixed evaluator. |

You can give limits in plain English or use settings like `searches=12 experiments=2 minutes=10`. Use `experiments=0` for research and analysis only. [Mode settings and budgets](references/operations.md#configuration-and-accounting)

For example, here’s a bounded performance run.

```text
Use Weaponized Curiosity in Autoresearch mode. Cut p95 on my local benchmark
by at least 10% and keep the outputs identical. Edit only src/parser.py in
an isolated copy. Use at most three candidate changes and five measurement
batches. Save one batch for validation and include the raw timings.
```

## What comes back

For a quick question, expect an answer, the evidence behind it, and what would change the recommendation. Longer runs can save sources, hypotheses, trial results, and a checkpoint under `.research/<run-id>/`. Give the agent that path when you want to pick up where it left off.

The skill uses the tools and permissions your agent already has. If a tool is missing, the report says what the agent could check and where the evidence stops. [Example sessions](docs/examples.md) · [Skill instructions](SKILL.md)

## What we’ve tested

On the included membership benchmark, the optimization run took median search time from **100.462 ms to 0.732 ms** and passed the separate validation split. A regular Codex run also found a correct set-based solution. The validation cases were visible to the agent. [Raw timings](docs/evaluation/membership-auto.json)

Codex and Claude Code were also tested on architecture decisions, conflicting sources, product ideas, and checkpoint recovery. A replay caught a daily batch that could leave a job waiting almost 24 hours despite a 12-hour deadline. The evaluation report includes mistakes, costs, and which stages actually ran. [Evaluation results](docs/evaluation/results.md)

## Dig in

The research workflow was inspired by [Archie Sengupta’s tweet](https://x.com/archiexzzz/status/2124919619471474790).

Read why the workflow uses independent first passes and tests that can change the decision. [Research notes](docs/research.md) · [Source ledger](docs/evidence-ledger.md) · [Architecture](docs/architecture.md)

Found a question the skill handles badly? A prompt, what happened, and what a better answer would do are enough to get started. [Evaluation suite](evals/README.md) · [Contributing](CONTRIBUTING.md)

[MIT License](LICENSE)
