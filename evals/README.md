# Evaluation suite

[cases.json](cases.json) defines eight research tasks and a recovery exercise with concrete checks. Synthetic fixtures let you rerun conflicting-evidence and measurement cases when network access is unavailable. CLI tests use real hosted models and native tools. The authored inputs and measurements from those inputs have different evidence roles.

## Local checks

```sh
python3 -m unittest discover -s evals -p 'test_*.py'
git diff --check
```

An Agent Skills validator can additionally check the bundle against the [specification](https://agentskills.io/specification). Run from a checkout directory named `weaponized-curiosity`.

## Live replays

The runner requires Python 3.10+, Git, a POSIX shell environment, and a logged-in CLI. It makes real requests against the active CLI account, so keep elapsed and provider usage budgets in view. Use only the supplied trusted fixtures and installed bundle when running with these permissions. The runner limits the CLI process group locally. It does not prove cancellation of a remote provider operation or isolate tools from the host by itself.

```sh
python3 evals/run.py codex algorithm normal --out eval-output/codex-normal
python3 evals/run.py codex algorithm auto --timeout 240 --out eval-output/codex-auto
python3 evals/run.py claude qualitative fallback --out eval-output/claude-fallback
```

Each run starts a fresh temporary Git workspace. The `normal` condition installs no bundle. Other conditions copy only the skill and references into that CLI's native discovery path. The evaluator uses fixture-only inputs. Web search is disabled for the pilot, so these runs exercise local evidence paths. The Claude Code fallback omits Agent and shell tools. The Codex fallback sets `agents.enabled=false`. Run outputs include the exact prompt, provider events, stderr, summary and selected research artifacts. Inspect them before sharing.

| Variant | Intended treatment |
| --- | --- |
| `normal` | Ordinary agent, with the fixture's original permissions |
| `solo` | Deep and zero agents, debate or experiments |
| `debate` | Deep with four requested workers, bounded critique and zero experiment batches |
| `full` | Deep, workers and critique, and two experiment batches |
| `auto` | Full workflow with two optimization attempts and up to four measurement batches |
| `quick`, `fallback`, `loop`, `resume` | Focused evidence, missing worker capability, a standalone optimization loop, and checkpoint reconciliation |

Treat intended and realized treatment separately. Record actual worker launches, completed checks, budget exceedances, failures, and controls. Score each case check 0 for absent or wrong, 1 for partial, and 2 for substantiated. Compare recommendation, evidence accuracy, novelty, experimental validity and reproduction detail, alongside request duration, observed tool calls and provider tokens when available. Record costs per provider without treating different cache, quota or internal pricing semantics as equivalent. The bundle SHA is the entrypoint's hash. For a multi-file change preserve the bundle Git revision or archive in the experiment manifest.

For estimates of marginal benefit, use fresh sessions, the same model and task authorization, randomized or counterbalanced order, matched aggregate budgets, and multiple unpublished tasks. Blind reviewers to labels where possible. Scores on this public fixture set provide regression evidence.

## Algorithm measurements

The checked-in baseline and benchmark provide a reproducible experiment. The validation split uses new workloads and edge cases, but the evaluator is visible to the agent. This is out-of-sample evidence if it was untouched during candidate selection. Use separately held artifacts and an external evaluator for stronger claims. Inspect candidate code before running it. To reproduce a run, copy the fixture into a temporary workspace and run:

```sh
python3 bench.py --split search --repeat 9
python3 bench.py --split validation --repeat 9
```

Use the same interpreter and machine conditions for comparisons, and report the raw timings and their variability. Speedups from the recorded fixture need not transfer to other workloads or hosts.
