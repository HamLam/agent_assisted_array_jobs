# Agent-assisted Slurm array job management

This repository preserves a completed end-to-end test of an agent preparing, submitting, monitoring, validating, and recovering Slurm array jobs on the Minnesota Supercomputing Institute (MSI) cluster.

## Why use small text files?

The goal is to test the agent's job-management decisions with a tiny workload whose correct answer can be calculated independently. Each input is processed by a serial program that writes its text in uppercase. Exact byte comparison against output from `LC_ALL=C tr a-z A-Z` provides a clear success criterion beyond file existence, a completion message, or a zero exit code.

Six disposable inputs exercise ordinary processing, filenames containing spaces, preservation of filenames and newlines, a program that writes partial output and fails, and a program that exits successfully while producing incomplete output. This makes it possible to verify that the agent preserves successful results, detects both kinds of failure, waits for previous attempts to stop, and retries only unresolved inputs with fresh output. The deliberate failures remain in the archived program.

This test exercises the management workflow. Its small inputs do not establish resource requirements or restart behavior for a real scientific application.

## Step-by-step summary

- Read `prompt.txt`, `AGENTS.md`, the Genesis Slurm skill, and MSI's Slurm documentation.
- Verified access to cluster `agate`, the `support` account, the `msismall` partition, and applicable submission and resource limits.
- Created a dedicated test directory containing six disposable text inputs, including `quiet river.txt`.
- Froze the mapping between internal task numbers, original filenames, and final output destinations; recorded input sizes and SHA-256 hashes.
- Created an uppercase program with four normal cases and two deliberate first-attempt failures: partial output followed by exit 23, and incomplete output followed by exit 0.
- Created a Slurm worker that independently calculates expected uppercase output with `tr`, requires program exit 0 and exact byte equality, publishes validated output, and checks the published bytes again.
- Generated the Slurm array script and saved cluster/program profiles, resource requests, submission intent, and separate attempt logs.
- Submitted pilot array `7019159` for tasks 1, 5, and 6, with at most two simultaneous tasks, one CPU, 256 MiB memory, five minutes, and no GPUs per attempt.
- Confirmed that `cedar.txt` passed and both deliberate failures were detected. The incomplete-output case returned program exit 0, but validation rejected it and the worker exited 86.
- Reviewed pilot memory and runtime measurements and retained the resource request for the remaining small inputs.
- Submitted array `7019492` for normal tasks 2, 3, and 4; all passed, including the input whose filename contains spaces.
- Reconciled stopped attempts with Slurm accounting, recorded retry reasons, and preserved successful outputs and failed-attempt evidence.
- Submitted retry array `7020092` for tasks 5 and 6 only, using fresh output locations and one retry per input.
- Verified that both retries passed exact comparison, giving six successful final outputs, two inputs recovered after retry, and zero unresolved inputs.
- Checked accounting to confirm a maximum of two simultaneous task allocations and verified that the frozen manifest, program, worker, and Slurm script were unchanged.
- Preserved all run artifacts, including inputs, expected outputs, final outputs, partial failed outputs, logs, commands, job IDs, accounting, measurements, and the final evidence report.

## Results

| Input | First attempt | Retry | Final exact match |
|---|---|---|---|
| `cedar.txt` | Successful | Not needed | Pass |
| `quiet river.txt` | Successful | Not needed | Pass |
| `quartz-note.txt` | Successful | Not needed | Pass |
| `violet.txt` | Successful | Not needed | Pass |
| `broken-compass.txt` | Deliberate partial output; exit 23 | Successful | Pass |
| `short-lantern.txt` | Program exit 0; incomplete output rejected | Successful | Pass |

All eight processing attempts and their exact-output validation ran through Slurm. Each attempt requested one CPU, 256 MiB, and five minutes; arrays used a concurrency limit of two and submission waves did not overlap. Batch-step peak RSS was approximately 13 MiB. Array-task MaxRSS fields were blank; batch-step accounting and program-level GNU time measurements are retained instead.

## Repository contents

- [`test-20261112T221451Z/REPORT.md`](test-20261112T221451Z/REPORT.md): per-input results, retry reasons, array task IDs, resource requests, and final accounting evidence.
- [`test-20261112T221451Z/manifest.json`](test-20261112T221451Z/manifest.json): frozen input identities and task mapping.
- [`test-20261112T221451Z/uppercase.py`](test-20261112T221451Z/uppercase.py): the test program, including deliberate failures.
- [`test-20261112T221451Z/worker.py`](test-20261112T221451Z/worker.py) and [`array.sbatch`](test-20261112T221451Z/array.sbatch): processing, validation, output publication, and Slurm resource configuration.
- `test-20261112T221451Z/inputs/`, `expected/`, and `outputs/`: original inputs, independently calculated expectations, and validated final results.
- `test-20261112T221451Z/attempts/`, `logs/`, and `records/`: all attempt evidence, scheduler logs, submission records, accounting, and integrity checks.
- `test-20261112T221451Z/cluster-profile.json` and `program-profile.json`: saved environment, limits, validation rules, and recovery decisions.
- `test-20261112T221451Z/submit.py`, `report.py`, and `evidence.py`: the submission and reporting helpers used during this test.

The run directory is an archive of the actual cluster execution. Its scripts and records intentionally retain the original absolute paths, account, partition, timestamps, and job IDs. A new run needs its own directory and frozen manifest, along with paths and submission settings appropriate to that cluster.

## References

- [MSI Slurm job submission and scheduling](https://userdocs.msi.umn.edu/compute/slurm_job_submission.html)
- Genesis skill used for this run: `genesis-skills/skills/hpc-skills/slurm/SKILL.md` in the local sibling checkout.
