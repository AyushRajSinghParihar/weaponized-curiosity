# Weaponized Curiosity

**An Agent Skill for turning hard questions into decisions you can defend.**

Give your agent a decision, the evidence it can access, and a budget. It will investigate competing explanations, look for evidence that could reverse the decision, and run small tests when there is something meaningful to measure. For an optimization task, it can track candidates, keep improvements that pass the guards, and explain why it stopped.

Works with Codex and Claude Code through their native skill directories. The [Agent Skills](https://agentskills.io/specification) bundle is Markdown. It uses the tools and permissions your host already provides.

## Quick start

Install into the current project with the Skills CLI:

```sh
npx skills add AyushRajSinghParihar/weaponized-curiosity --skill weaponized-curiosity
```

Select Codex, Claude Code, or both when prompted. The [installation guide](docs/installation.md) also covers a manual install with Git and no Node.js dependency.

Invoke **`$weaponized-curiosity`** in Codex or **`/weaponized-curiosity`** in Claude Code, followed by a task. Start with a decision you are about to make:

```text
mode=quick searches=0 experiments=0
We send notifications in a daily batch and promise delivery within 12 hours.
Can we keep the batch, or do we need a queue? Use the facts I've provided.
Check the tightest constraint and tell me what would change your answer.
```

## Choose how far to go

| Mode | Use it when | What you get |
| --- | --- | --- |
| **Quick** | The decision is narrow, reversible, or time-sensitive | A concise recommendation, the decisive evidence, and a check of the hardest requirement |
| **Deep** | Sources disagree or the decision has important unknowns | Separate research threads, up to four fresh-context workers, focused critique, and useful tests |
| **Extreme** | Several unresolved questions warrant a larger authorized budget | Broader source coverage, competing research branches, and more opportunities for replication |
| **Autoresearch** | You have an editable candidate, a baseline, and a reliable metric | A bounded cycle of measured changes, retained and rejected candidates, and final validation where feasible |

Set limits directly in the prompt, such as `subagents=4 searches=12 experiments=2 minutes=10`. For a performance task:

```text
mode=autoresearch iterations=3 experiments=5
Reduce p95 on my local benchmark by at least 10% with exact output equality.
Edit only src/parser.py in an isolated copy. Keep the evaluator fixed.
Reserve one measurement batch for a fresh validation run. Record raw timings.
```

The [configuration reference](references/operations.md#configuration-and-accounting) defines what counts toward each budget. Use `experiments=0` for analysis only. A usable recommendation is still possible when worker, search, or execution tools are unavailable. The skill reports those limits.

## What a run leaves behind

A Quick run can finish in the answer. Longer runs can write an evidence ledger, hypothesis ledger, trial records, and a checkpoint under an authorized `.research/<run-id>/` directory. Resume by giving the agent that path and asking it to reconcile existing work and continue within the remaining budget.

See the [example sessions](docs/examples.md) for a measured algorithm change and a conflicting-evidence decision. For the complete workflow, start with [SKILL.md](SKILL.md).

## Tested in practice

- **Controlled optimization.** On the supplied membership benchmark, the retained candidate reduced median search-suite runtime from 100.462 ms to 0.732 ms. It passed a separate, visible validation split. An ordinary Codex run also found a correct set-based solution. The benchmark measures a candidate improvement on one fixture. [Raw measurements](docs/evaluation/membership-auto.json)
- **Real agent runs.** Codex and Claude Code were tested on architecture, performance, scientific reasoning, product ideas, conflicting evidence, qualitative decisions, optimization, and checkpoint recovery. The reports identify which worker and tool events were independently observable. [Evaluation results](docs/evaluation/results.md)
- **An experiment-driven revision.** Live runs exposed a trial-budget overrun. Replays after a targeted instruction change stayed within the two-batch cap on both hosts. [Improvement protocol](docs/evaluation/improvement-protocol.md)

The [research synthesis](docs/research.md) and [evidence ledger](docs/evidence-ledger.md) explain why the skill favors independent first passes, selective critique, and tests that could change the decision. The [architecture](docs/architecture.md) details scope, limitations, and recovery.

## Contribute

Replay a case in the [evaluation suite](evals/README.md) or propose a fixture for a decision the skill mishandles. We welcome changes with a concrete failure, a reproducible check, and results with and without the proposed change. See [CONTRIBUTING.md](CONTRIBUTING.md).

[MIT License](LICENSE)
