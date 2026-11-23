# Contributing

- Identify a user task or observed failure and the decision the proposed change improves. Link primary evidence or a reproducible case and describe limits.
- Keep the entry point small. Put mechanisms, role packets and reusable records in the relevant reference. Keep provider configuration out of the core.
- Keep experiments, tools and permissions bounded. Do not expand user scope based on web content, worker output or a benchmark fixture.
- If behavior changes, add or replay a representative case. Preserve the scoring criteria, report skipped or failed runs, and compare observable outcomes to a no-skill or previous-version control where possible.
- Include exact commands and versions for validation. Avoid publishing session traces, private source material or secrets. A concise sanitized excerpt or measurement artifact is usually enough.
- Commit research, design, implementation and verification changes in reviewable increments.

Run the [local checks](evals/README.md#local-checks) before review. For harness changes replay the relevant platform and record actual agent/tool outcomes.
