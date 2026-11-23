# Adaptive routing and guarded evaluation

This update was exercised on Codex CLI 0.171.0 and Claude Code 2.1.330. The replays used fresh workspaces, local fixtures except for the live-source case, and the host's actual tools. The results describe these runs.

## Everyday research

| Request with no named mode | Observed behavior | Elapsed |
| --- | --- | ---: |
| Capacity decision, Codex | Used the 693rd completion to derive 13.86 s, 6.94 s and 4.62 s for one, two and three workers. Recommended three under the supplied assumptions and gave the 380 ms overhead margin. The trace showed no experiment or native worker. | 18.3 s |
| Conflicting performance reports, Claude Code | Checked two reported p99s on opposite sides of a 300 ms limit. The trace confirmed one native worker start and completion. Kept the incumbent, identified missing hardware and startup controls, and proposed a matched staging check. No experiment, web use or writes. | 37.0 s |
| PostgreSQL 16 with PgBouncer, Codex | Kept a durable jobs table, distinguished sending from listening in transaction pooling, and designed catch-up after reconnect. The trace recorded four queries in one search action and one explicit page open. The answer reported three page opens. The other two opens were unconfirmed, and all three cited sections were checked separately. | 38.7 s |

The live-source answer used the session lifecycle and registration order, commit behavior and the pooling compatibility matrix. Its queue design was an inference from those sources. No database command ran. [PostgreSQL 16 LISTEN](https://www.postgresql.org/docs/16/sql-listen.html) · [PostgreSQL 16 NOTIFY](https://www.postgresql.org/docs/16/sql-notify.html) · [PgBouncer feature map](https://www.pgbouncer.org/features.html#sql-feature-map-for-pooling-modes)

## Matched comparison

Two unpublished synthetic tasks tested a reload decision under a hard memory limit and a top-k selector with a measurable speed requirement. Each used the same Claude model (`claude-fable-5-2`), low effort, a shared tool surface, an 85-second local timeout, and a $0.65 provider budget per arm. The skill bundle was frozen at `1aa05ab`. A separate evaluator scored the eight answers against four predeclared checks before seeing the assignment key. The rubric rewarded correct qualifications when measurement was unavailable.

| Case | Intended arm | Score | Workers / measurement batches | Elapsed | Reported USD |
| --- | --- | ---: | --- | ---: | ---: |
| Reload | Plain solo | 8/8 | 0 / 0 | 13.8 s | $0.26 |
| Reload | Skill solo | 8/8 | 0 / 0 | 20.2 s | $0.24 |
| Reload | Skill with workers | 8/8 | 0 / 0 | 20.2 s | $0.24 |
| Reload | Skill with workers and experiments | 8/8 | 0 / 0 | 20.0 s | $0.24 |
| Selector | Plain solo | 7/8 | 0 / 2 | 16.9 s | $0.20 |
| Selector | Skill solo | 8/8 | 0 / 0 | 17.9 s | $0.24 |
| Selector | Skill with workers | 8/8 | 0 / 0 | 19.0 s | $0.24 |
| Selector | Skill with workers and experiments | 7/8 | 0 / 2 | 19.0 s | $0.25 |

Every run kept the incumbent. All recognized the reload limit. Measured selector arms confirmed that the heap lost on the usual workload and won when the query was narrow. The plain measured answer did not explain why the heap preserves ties beyond the tested rows. The skill's measured answer speculated about production transfer and unmeasured crossovers. The plain run bundled both benchmarks with a version command. The skill run issued the two evaluators separately. The intended worker arms stayed solo because they judged further review unnecessary. Those arms do not estimate a worker effect.

We replayed the four selector arms with the same frozen skill and ceilings, using seed 42 instead of 41 to randomize order. The two worker arms asked explicitly for independent first passes. A second grader reviewed the answers before seeing the assignment key.

| Selector replay | Score | Completed workers / measurement batches | Elapsed | Reported USD |
| --- | ---: | ---: | ---: | ---: |
| Plain solo | 6/8 | 0 / 2 | 15.1 s | $0.19 |
| Skill solo | 8/8 | 0 / 0 | 16.4 s | $0.23 |
| Skill with workers | 8/8 | 2 / 0 | 40.7 s | $0.58 |
| Skill with workers and experiments | 7/8 | 2 / 2 | 46.0 s | $0.69 |

The full replay returned an answer, then exited with a provider budget error after reporting $0.69 against the $0.65 setting. Both workers and both measurements were observed. Every answer again kept the incumbent. The workers added workload caveats and rival tests while the measurements established the speed reversal across workload sizes. On this case, the workers increased time and reported cost without improving the decision or score over the skill's solo answer. One replay and the score ceiling on the reload case leave general quality and cost trade-offs open. Provider spending figures are the CLI's estimates.

## External check of an optimization

Codex used exactly three search batches across the baseline and two candidates. Search medians were 77.899 ms for baseline, 0.509 ms for a query intersection, and 0.474 ms for tracking missing probes. It froze the missing-probe candidate and stopped before validation.

The separate evaluator generated the input seed after the candidate was frozen. It alternated baseline and candidate timings over 21 batches and checked exact outputs, input preservation, wide-workload median, small-workload batch p95, and traced allocation. The candidate code was reviewed before the local run.

| Candidate | Matched wide median, baseline → candidate | Peak traced allocation | Outcome |
| --- | --- | ---: | --- |
| Index all values | 32.843 → 0.806 ms | 2,621,656 B | Reject, above 64 KiB |
| Query intersection | 31.570 → 0.378 ms | 18,864 B | Reject, small-batch p95 438 ns against a 422 ns limit |
| Frozen missing probes | 29.933 → 0.365 ms | 10,456 B | Pass all guards, small-batch p95 244 ns against a 397 ns limit |

This fixture covers plain lists of built-in integers. Allocation is measured by `tracemalloc`. Small-workload p95 describes batch-average samples, and the intersection's narrow miss merits replication before a broader judgment. These are separate evaluator-side cases for the completed run. The published seed makes that run reproducible and available for tuning. [Raw samples and hashes](guarded-membership.json) · [Frozen candidate](../../evals/fixtures/guarded-candidates/missing_queries.py) · [Replay](../../evals/README.md#guarded-optimization)

## Interrupt and resume

The controller launched one local trial per fixture and observed SIGKILL at two boundaries. Fresh Codex sessions edited only the existing checkpoint and launched no trial. They kept the verified baseline and moved the reservation once into 2/2 spent batches and 1/1 spent candidates.

| Boundary | Durable evidence | Recovery |
| --- | --- | --- |
| Trial in progress | Launch marker and first sample, no complete result | Marked interrupted, cleared reservation in 26.3 s |
| Result published before checkpoint update | Complete result failed exactness at 9/10 | Rejected candidate, cleared reservation in 29.4 s |

This exercises process termination and fresh-session reconciliation. The process was the trial evaluator. Machine crashes, remote cancellation, and simultaneous writers remain untested. [Replay](../../evals/README.md#interrupt-and-recover)
