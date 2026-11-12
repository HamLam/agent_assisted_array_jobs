# Slurm uppercase workflow test

Updated: 2026-11-12T22:30:22.192866Z

Each attempt requested 1 CPU, 256 MiB, five minutes, no GPUs. Arrays use `%2`; waves do not overlap. Only stopped attempts with a known accounting state are eligible for retry.

| Input | Attempts / Slurm array task | Result | Exact final match |
|---|---|---|---|
| cedar.txt | 7019159_1 (attempt 1) | successful | PASS |
| quiet river.txt | 7019492_2 (attempt 1) | successful | PASS |
| quartz-note.txt | 7019492_3 (attempt 1) | successful | PASS |
| violet.txt | 7019492_4 (attempt 1) | successful | PASS |
| broken-compass.txt | 7019159_5 (attempt 1), 7020092_5 (attempt 2) | program exited 23 after deliberate partial output; successful | PASS |
| short-lantern.txt | 7019159_6 (attempt 1), 7020092_6 (attempt 2) | program exit 0 but exact byte comparison rejected incomplete output; successful | PASS |

Successful: 6/6. Recovered after retry: 2. Unresolved: 0.

## Verification evidence

`manifest.json` freezes task IDs, original filenames, destinations, sizes, and input SHA-256. `uppercase.py` retains both deliberate first-attempt branches. Inside Slurm, `worker.py` independently runs `/usr/bin/tr a-z A-Z` with `LC_ALL=C`, compares entire output bytes, requires program exit 0, atomically publishes validated output, and compares final bytes again. Each `attempts/task-*-attempt-*/result.json` records validation and program exit, with separate program stdout/stderr, fresh output, and GNU time measurements. Rejected attempt output is retained and never published.

## Scheduler and measurements

Submitted array IDs: 7019159,7019492,7020092. Full scheduler data: `records/accounting.psv`. Job-level MaxRSS may be blank for these very short tasks; inspect batch-step MaxRSS and per-program `time.txt` rather than claiming blank measurements are zero. GNU time measures the program process, not the whole Slurm allocation.

## Resume

Read submission records and reconcile every job ID using squeue and sacct before acting. Do not repeat an uncertain submission. Frozen task IDs: normal 1-4, fail-once 5, incomplete-once 6. At most two attempts per input. All computation and exact byte validation run through Slurm.

## Final accounting evidence

Maximum simultaneous task allocations from accounting start/end times: **2**.

| Array task | Scheduler state | Exit | CPUs | Memory request | Time limit |
|---|---|---|---|---|---|
| 7019159_1 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |
| 7019159_5 | FAILED | 23:0 | 1 | 256M | 00:05:00 |
| 7019159_6 | FAILED | 86:0 | 1 | 256M | 00:05:00 |
| 7019492_2 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |
| 7019492_3 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |
| 7019492_4 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |
| 7020092_5 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |
| 7020092_6 | COMPLETED | 0:0 | 1 | 256M | 00:05:00 |

Batch-step peak RSS measurements: 7019159_1.batch: 12960K, 7019159_5.batch: 12896K, 7019159_6.batch: 12908K, 7019492_2.batch: 13032K, 7019492_3.batch: 12920K, 7019492_4.batch: 13048K, 7020092_5.batch: 13012K, 7020092_6.batch: 12924K.

Array-task MaxRSS fields are blank; batch-step memory and per-program GNU time measurements are available. Accounting elapsed times include batch startup and are distinct from program-only timing.

Frozen manifest, deliberate-failure program, worker, and Slurm script SHA-256 verification: PASS.
