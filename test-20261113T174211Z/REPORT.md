# Revised-instructions Slurm rerun

Run: `test-20261113T174211Z`. Updated: 2026-11-13T17:55:43.027957Z.

**6/6 successful; 2 recovered after one retry each; 0 unresolved.**

## What changed

- Revised the reusable AGENTS.md with a repository map, setup/status commands, required record fields, known gotchas, and a completion checklist.
- Kept the original frozen-input, validation, resource-ceiling, uncertain-submission, selective-retry, and fresh-output safeguards.
- Added per-attempt environment/exit/publication records, immutable reconciliation history, a selective retry plan, and a separate Slurm final audit.
- Used comparable successful resource measurements instead of another pilot for the identical program and six inputs.
- Kept the original run intact and did not push to GitHub.

## Per-input evidence

| Input | First program / worker exit | Retry | Final exact match |
|---|---|---|---|
| cedar.txt | 0 / 0 | Not needed | PASS |
| quiet river.txt | 0 / 0 | Not needed | PASS |
| quartz-note.txt | 0 / 0 | Not needed | PASS |
| violet.txt | 0 / 0 | Not needed | PASS |
| broken-compass.txt | 23 / 23 | 7114518_5; program exited 23 after deliberate partial output | PASS |
| short-lantern.txt | 0 / 86 | 7114518_6; program exit 0 but exact byte comparison rejected incomplete output | PASS |

The worker requires program exit 0 and exact byte equality against independent `LC_ALL=C tr a-z A-Z`, then compares the published bytes again. A separate Slurm audit recalculated expectations for all six final files. Both deliberate first-attempt failures remain byte-for-byte unchanged in the test program. Failed partial outputs and their logs are retained.

## Job and resource evidence

| Slurm job/task | State | Exit | CPUs | Memory request | Time limit | Batch peak RSS |
|---|---|---|---|---|---|---|
| 7114385_1 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13404K |
| 7114385_2 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13396K |
| 7114385_3 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13236K |
| 7114385_4 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13320K |
| 7114385_5 | FAILED | 23:0 | 1 | 256M | 00:05:00 | 13416K |
| 7114385_6 | FAILED | 86:0 | 1 | 256M | 00:05:00 | 13260K |
| 7114518_5 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13284K |
| 7114518_6 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 13444K |
| 7115125 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 | 10764K |

Maximum simultaneous allocations across processing and verification: **2**. Each job requested one CPU, 256 MiB, five minutes, no GPUs. Processing used eight attempts; the ninth job performed verification only.

Job/allocation-level MaxRSS is blank for 9 records. Batch-step RSS and program-only GNU time measurements are saved separately; blank measurements are not treated as zero. Program-only timing/memory excludes the worker and scheduler startup.

## Completion checklist

- [x] all six final outputs validated
- [x] execution and validation evidence
- [x] all jobs stopped and reconciled
- [x] selective retries and successes preserved
- [x] frozen records intact
- [x] original test unchanged
- [x] final slurm audit successful
- [x] resources and total concurrency within limits
- [x] required records complete
- [x] measurement gaps explicitly recorded

Original archive integrity: all **117 files** retain their previous content hashes. Normal-case outputs were also hashed before retry and checked unchanged afterward.

## Evidence files

- `records/AGENTS.before.md`, `records/AGENTS.md`, `records/AGENTS.diff`: original instructions, revised snapshot, and changes.
- `run-config.json`, profiles, and `manifest.json`: limits, commands, validation, resource rationale, environment, and frozen file identities.
- `records/submission-*.json`, `retry-plan.json`, and `reconciliations/`: intent, job IDs, retry eligibility/reasons, and scheduler evidence.
- `attempts/`: separate started/result/completion records, program logs, partial or complete output, GNU time, and attached scheduler accounting.
- `records/final-audit.json`: independent Slurm verification and immutable-original-run checks.
- `records/record-validation.json`, `completion-checklist.json`, and `accounting.psv`: required-record checks, completion evidence, and resource measurements.

## Interpretation

This rerun exercises the revised instructions in one active agent session. It verifies the six controlled outcomes and the required records/checklist. It does not simulate an agent restart, lost submission response, genuine memory exhaustion, or a real time-limit failure. Those recovery rules remain instructions, not claims of additional tests.

All changes and new artifacts remain local pending the user review requested before any GitHub push.
