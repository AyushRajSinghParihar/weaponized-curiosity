# Evaluation results

See the [adaptive update](adaptive-update.md) for matched comparisons, live-source auditing, guarded optimization and process interruption replays.

Pilot run on 2026-11-24. The [cases and checks](../../evals/cases.json) cover seven research domains and a recovery scenario. The applications and tool invocations were real. Tasks and source fixtures were synthetic. A single developer reviewed answers and execution events against the listed checks, with no blinding or repeated random samples. Comparisons show what happened in these attempts and do not estimate average or causal improvements.

## Platform coverage

| Surface | Observed | Limit |
| --- | --- | --- |
| Codex CLI 0.171.0 | Repository skill used through the native discovery path, bundled references read, scoped file edits and commands, real measurements, bounded optimization, and durable checkpoint reconciliation | CLI JSONL in this environment recorded commands and edits but did not expose worker events for the compared runs. CLI worker counts in final reports are self-reported. The default model was not surfaced in the trace. |
| Development Codex session | Four separate fresh-context workers on the conflicts task. Three concurrent slots, later fourth dispatch, first-pass barrier, and two targeted follow-ups after all four submitted | Shared model and source fixture. Transcript freshness was set at dispatch. This run did not establish filesystem isolation between workers. |
| Claude Code 2.1.330 | Native skill appeared in CLI initialization with the bundle and was absent in the no-skill control. Slash invocation, reference reads, measurements, missing-worker fallback, four native agents and four completed task notifications in the refined run | The trace reported model `claude-fable-5-2` with low effort. The four-worker replay left the debate round unused. |
| Other harnesses | The skill uses portable metadata and local references | No live runs performed. |

The runner used fresh fixture workspaces, Codex `--ignore-user-config`, and project-only settings and an empty MCP configuration for Claude Code. Built-in and ambient skills or host instructions can still affect a run. Provider settings and accounting differ. Live source search was disabled in this fixture suite. Foundational project research used live retrieval separately.

## Five treatment arms on one algorithm

All five conditions below use the same Codex CLI surface and user task. Resource limits differ by design. CLI usage numbers are input tokens (cached included) plus output tokens as reported by the CLI. They may omit activity from independent workers. The normal control was free to verify or optimize under the original request, as it would be in a typical session.

| Intended arm | Actual result | Elapsed | Input / output tokens |
| --- | --- | ---: | ---: |
| Normal, no skill | Measured list, sort and set. Kept the set with a 279× search-fixture speedup and correct out-of-sample results. Called its visible validation split independent. | 61.0 s | 263,050 / 1,408 |
| Deep solo | Justified set indexing using workload and complexity. Ran zero trials, preserved the baseline and labeled the speedup unmeasured. | 23.3 s | 58,574 / 608 |
| Debate, zero experiments | Reported four reviews and one challenge. Surfaced dense span and hostile-collision regimes, and kept the baseline. Zero observed trials. | 105.3 s | 684,782 / 2,903 |
| Full, initial skill | Reported four reviews and one exchange. Measured the baseline and interpreted the zero-iteration cap as barring a candidate test. | 111.2 s | 657,047 / 2,431 |
| Full with autoresearch | Verified a baseline, tested two candidates, rejected sorted search, froze the set and checked it against visible out-of-sample cases. Kept the set after 137× search speedup. | 129.5 s | 605,292 / 3,633 |

The normal and autoresearch arms both reached a correct set-based solution. The latter retained more raw and decision evidence, made guard and rollback conditions explicit, and tested an implementation that preserves behavior for list and integer subclasses. Its guard overhead and cross-run conditions make the two speedup figures unsuitable for estimating the effect of the skill. The solo answer was faster and cheaper when the next action was only to choose a candidate to test. Contrary cases from the debate added technical breadth without changing the recommendation. This pilot found no evidence that four agents improve the decision on this straightforward workload, or that the added cost buys a general quality uplift. A separate local replay of the recorded code passed both splits at 77.812 ms baseline, 0.589 ms candidate and 1.023 ms out-of-sample. [Autoresearch measurements](membership-auto.json)

## Other case outcomes

The checks award 0 for absent or wrong, 1 for partial, or 2 for substantiated. These illustrative case scores include task-specific judgment and are not cross-case ranks.

| Case and run | Checks | Result and limitation |
| --- | ---: | --- |
| Architecture, Claude Quick | 7/8 | Compared all options, highlighted deterministic send identity and the 24-hour provider window, and proposed reversible rollout. Claimed a daily batch plus retry meets a 12-hour tolerance without establishing when messages become eligible. The Codex normal control called out this gap. |
| Performance, Codex Quick | 8/8 | Used 30 matched rows per cohort and nearest-rank p95. With parsing removed, warm p95 went 129 to 122 ms, and cold 212 to 206 ms. Ruled out a 10% parser-only gain within the fixture's additive timing model. Left production effects unverified. |
| Technical hypothesis, Claude Deep solo | 7/8 | Distinguished bulk heat, local plume, and HVAC coincidence. Gave discriminating observations and said no test ran. A minimal first test could have reused the two available sensors and randomized device state before adding meters and loggers. |
| Product ideation, Claude Quick | 8/8 | Produced a pull page, channel-native push digest, and physical call-board approach. Each had a different adoption failure and a cheap next step. Novelty was assessed as difference between mechanisms. No market or user validation ran. |
| Conflicting evidence, Codex Quick and separate four-worker session | 8/8 on each | Identified two underlying evidence families rather than counting the newsletter twice. Favored the matched laptop evidence with caveats. The Quick run left the suggested approval file absent. Four workers added a conditional warm-routing idea and a way to discriminate phase effects, with the same cold-default decision. The normal Codex control already reached the same primary decision. |
| No measurable objective, both host fallbacks | 8/8 on each | Compared priorities without proxy optimization, described reversible options, and correctly reported zero genuine workers. Claude overstated inherent bandwidth cost in one alternative, but conditioned its overall choice on unavailable reader and file-size evidence. The normal Claude control also correctly skipped the loop. |
| Recovery, Codex revised skill | 8/8 | Reconciled a completed result left pending in a prebuilt checkpoint. Rejected the 82 ms candidate for 9/10 output matches, retained the 100 ms verified baseline, and recorded 2/2 batches and 1/1 attempts. Updated only the checkpoint in the fixture and launched no test. This was a live replay of a simulated interruption. |

The technical, product, architecture and qualitative tasks establish whether the skill can produce and qualify a decision without fresh empirical work. Source attribution on the conflicts task and calculation on the performance task were checked against supplied fixtures. Experimental validity and reproducibility were judged from the traced commands and preserved inputs, not just the reports.

## Improve the skill using its own loop

The [bounded improvement protocol](improvement-protocol.md) allowed two wording revisions. It used the same Claude algorithm/full setting for replays and separated benchmark batches from setup commands.

| Revision | Observed outcome | Decision |
| --- | --- | --- |
| Initial skill | Claude ran baseline, candidate and validation despite a two-batch cap, with an additional denied compound attempt. Codex full ran only the baseline because it conflated the iteration and experiment limits. | Baseline failure |
| I1, explicit common cap | Claude completed two measurements and skipped validation, but attempted a compound benchmark that was denied and a denied out-of-scope correctness command. One real reviewer launched. | Reject under dispatch criterion |
| I2, preallocated command schedule and separate iteration limit | Claude and Codex each performed exactly two isolated benchmark invocations and omitted validation. The Claude replay launched and completed four native workers. The Codex replay measured a candidate even with zero optimization iterations. Evaluator files were preserved. | Retain |

On Claude I2, the search median was 98.9 ms versus 0.316 ms. End-to-end took 62.6 s, and the CLI reported 184,616 cached/input tokens plus 5,295 output tokens and estimated cost of $0.883. The initial Claude run took 71.5 s and reported 115,845 cached/input tokens plus 2,257 output at $0.319. The I2 run included observed workers, so the latency and cost difference cannot be attributed to the wording change alone. On Codex I2, matched search medians were 81.0 ms and 0.699 ms. Elapsed time was 100.4 s with 555,819 input and 3,333 output tokens. Both replays provide search-split evidence. Independent validation was not authorized inside the exhausted two-batch limit.

Local tests verify metadata, reference routing, bundle placement, deterministic fixture facts and contracts, parsed event preservation, and local process timeout. Fixtures for injected provider events are mocks. The real fixture runs used native providers. Hidden adversarial holdouts, a real process death during an experiment, concurrent writers, broad live-search quality and budget-matched generalization remain unverified.

## Public release replay

The architecture pilot exposed a failure to test the 12-hour delivery requirement against a daily schedule. The release replay kept the original prompt and compared two successive instruction changes. A separate, synthetic [capacity case](../../evals/cases.json) checked a numerical unserved-work boundary. All runs used Quick mode, with no searches, experimental commands, or workers.

| Run | Result | Elapsed |
| --- | --- | ---: |
| Architecture, original skill on Claude Code 2.1.330 | Treated daily batching with retries as sufficient for a 12-hour requirement. | 26.6 s |
| Architecture, generic boundary check on Claude Code | Repeated the deadline error. A general instruction to check the hardest requirement did not change the decision. | 22.4 s |
| Architecture, concrete boundary check on Claude Code | Traced eligibility just after the daily run, identified nearly 24 hours of waiting, and made the batch option conditional on a shorter cadence with time for retries. Actual processing and retry durations were unmeasured. | 32.4 s |
| Capacity, generic boundary check on Codex CLI 0.171.0 | Identified the correct minimum of three workers and used burst arrivals. Reported the 694th as the nearest-rank p99 out of 700, yielding incorrect one- and three-worker times. | 15.5 s |
| Capacity, concrete boundary check on Codex CLI | Used rank 693 and calculated 13.86 s, 6.94 s and 4.62 s for one, two and three workers. Three met the idealized bound. The result flagged unmeasured overhead without specifying a production test. | 15.8 s |

The retained instruction asks the coordinator to use a concrete adverse input for each hard requirement, account for waiting across the entire path, and derive counts before rounding. These were single fresh runs per condition on known prompts. They verify the observed corrections on those cases.
