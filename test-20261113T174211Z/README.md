# Revised-instructions Slurm workflow test

This run checks the revised [AGENTS.md](records/AGENTS.md) against the same six disposable inputs and unchanged failure-injection program used in the [original test](../test-20261112T221451Z/REPORT.md). It adds explicit setup evidence, required records, scheduler reconciliation history, and a final completion checklist.

## Why text files?

Uppercase conversion has an independently calculable answer, so the workflow can verify complete output bytes rather than trusting file existence or a success message. The six files exercise normal results, a filename with spaces, a partial-output failure, and incomplete output from a program that exits successfully. They test job management without needing a large scientific workload.

## Instruction changes

- Added a repository/run layout and setup/status command examples.
- Defined required cluster, program, run, manifest, submission, attempt, and report records.
- Added gotchas for spaces, stale output, delayed accounting, blank measurements, and array concurrency.
- Added a completion checklist and explicit handoff rules.
- Preserved the existing validation, frozen mappings, selective retries, resource ceilings, and fresh-output rules.

The previous instructions and their diff are saved in [`records/AGENTS.before.md`](records/AGENTS.before.md) and [`records/AGENTS.diff`](records/AGENTS.diff).

## Step-by-step run

- Rechecked Slurm access, account/partition/QoS requirements, system tools, and file permissions.
- Saved hashes of every original test file to check that the earlier run remained unchanged.
- Created a new run directory and copied the same six inputs and unchanged test program.
- Froze the input manifest, profiles, configuration, scripts, and instruction snapshot.
- Used the original run's measured resource usage to retain one CPU, 256 MiB, and five minutes per attempt; no new pilot was needed for this identical workload.
- Checked the request with `sbatch --test-only`, then recorded intent and submitted initial array `7114385`, throttled to two simultaneous tasks.
- Verified the four normal outputs. Detected exit 23 with partial output for `broken-compass.txt`, and rejected incomplete output from `short-lantern.txt` despite program exit 0.
- Reconciled the stopped attempts with Slurm accounting, saved success hashes and retry reasons, and confirmed neither failed output had been published.
- Submitted only tasks 5 and 6 as retry array `7114518`, once each, using fresh attempt directories. Both passed exact validation.
- Submitted verification-only Slurm job `7115125` after processing stopped, to recalculate expected output, compare all final bytes, check recorded evidence, and verify original-run integrity.
- Reconciled final accounting and generated the required-record checks, completion checklist, and report.

## Results and evidence

See [`REPORT.md`](REPORT.md) for final outcomes, measurements, and checklist status. Processing used eight attempts; a ninth Slurm job performed verification only. Every job requested one CPU, 256 MiB, five minutes, and no GPUs. Submission guards kept processing and verification waves separate.

- [`prompt.txt`](prompt.txt): original test requirements and authorized limits.
- [`run-config.json`](run-config.json), [`cluster-profile.json`](cluster-profile.json), and [`program-profile.json`](program-profile.json): configuration, evidence, limits, validation, and resource rationale.
- [`manifest.json`](manifest.json): frozen task/file identities and output mapping.
- [`scripts/`](scripts/): unchanged test program plus processing, submission, reconciliation, and audit helpers.
- `inputs/`, `expected/`, and `outputs/`: inputs, independent expected text, and validated final output.
- `attempts/` and `logs/`: every attempt's output, command/environment, exits, program logs, timing, and accounting.
- `records/`: instruction snapshots/diff, preflight evidence, submissions, reconciliation history, retry reasons, final audit, and completion checklist.

The scripts retain this run's absolute paths and cluster settings. Prepare a new directory, manifest, and configuration for another run. This test does not exercise real memory exhaustion, time-limit failures, lost submission responses, or restarting the agent between sessions.

The requested GitHub update is held for user review; no push was made as part of this rerun.
