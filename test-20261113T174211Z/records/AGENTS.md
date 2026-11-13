# MSI Slurm array workflow instructions

## Purpose and scope

Help users process independent files through Slurm arrays: prepare jobs, choose resources, submit, track, validate, and recover failures using ordinary Slurm commands.

The user supplies the input location, output location, and intended program or analysis. Establish authorized resource, concurrency, and retry ceilings. Proceed within those ceilings without repeated confirmation; ask focused questions only when missing information prevents a reliable decision.

Use the Genesis Slurm skill for general procedures and [MSI documentation](https://userdocs.msi.umn.edu/compute/slurm_job_submission.html) plus current cluster information for site requirements. Locate the installed skill; record its path. Preserve input filenames: array numbers refer to a frozen file list.

Work within the authorized run and output locations. Leave unrelated jobs and data alone. Historical test limits are examples, not authorization for another workload.

## Repository and run layout

- `AGENTS.md`: reusable workflow instructions.
- `README.md`: project overview and links to completed tests.
- `test-*/`: archived test runs; their scripts may contain fixed paths, accounts, and job IDs.
- Each new run needs its own directory and frozen mapping. Never edit an archived run to prepare another run.

Use this layout, or record equivalent paths in the run configuration:

```text
<run>/
  run-config.json          # command, validation, resources, limits, record paths
  cluster-profile.json     # access, account, partitions, environment, limits
  program-profile.json     # invocation, software, parallelism, checks, recovery
  manifest.json            # frozen input identities, task IDs, output destinations
  scripts/                 # batch scripts and processing/validation helpers
  attempts/                # fresh output, logs, and record for every attempt
  logs/                    # scheduler stdout/stderr, unique to job and task
  records/                 # instructions, submissions, accounting, decisions
  REPORT.md                # per-input outcomes and completion checklist
```

Inputs and final outputs may live at user-specified locations outside this layout. Record their exact paths. Format records as JSON, TSV, or another documented machine-readable format; keep equivalent information if filenames differ.

## Setup and useful commands

Verify required tools, cluster access, file access, software, accounts, partitions, and current limits before submitting. Replace example arguments with values established for the run:

```bash
command -v sbatch squeue scontrol sacct sinfo sacctmgr
hostname
sinfo -o '%P %a %l %D'
scontrol show partition <partition>
sacctmgr -nP show assoc where user="$USER" account=<account>
sacctmgr -nP show qos where name=<qos>
scontrol show config
sbatch --test-only <script> <arguments>
```

Use explicit resource requests; a successful request check is not a submitted or completed job. If a command is unavailable or restricted, record the gap and obtain reliable equivalent information before making a dependent decision.

After submission, query recorded job IDs, including batch steps for measurements:

```bash
squeue -r -j <job_ids> -o '%.20i %.12T %.10M %R'
scontrol show job <job_id>
sacct -nP -j <job_ids> --format=JobID,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS,Start,End
```

Limit changes and cancellations to this run's recorded job IDs. Do not rerun historical submission commands to check status.

## Required records

- **Cluster profile:** observation time, access method, cluster, account, eligible partitions/QoS, environment setup, applicable limits, and documentation or command evidence. Recheck mutable facts before each run.
- **Program profile:** one-input command and output arguments, options, software/version/modules/container, process/thread/GPU/node use, success checks, and proven restart or independently repeatable stages.
- **Run configuration:** run ID, instruction snapshot, selected inputs, exact command/environment, output checks, requested resources, authorized ceilings, resource rationale, and paths to all records.
- **Frozen manifest:** task ID, original input path/name, final destination, size, and a checksum or equivalent identity sufficient to detect changes. Never regenerate the mapping during retries.
- **Submission record:** unique submission identity, timestamp, exact command, selected tasks/attempts, intent written before submission, returned job IDs, and any uncertainty or reconciliation.
- **Attempt record:** input/task, attempt number, job IDs, host, command/environment, requested resources, output/log paths, start/end times, program and worker exit status, validation/publication results, scheduler state, measurements, and retry reason when applicable. Record unavailable fields explicitly and attach accounting when it arrives.
- **Final report:** per-input results, attempts and retry reasons, output verification, accounting/resources, missing measurements, unresolved work, and the completion checklist below.

Keep all attempts, logs, scripts, instruction snapshots, and decisions. Do not silently rewrite earlier evidence when adding later accounting or a retry.

## Prepare each run

1. Confirm the intended analysis and program-specific input rules. Check readable inputs and writable outputs; resolve ambiguous selection before submission.
2. Create a unique run directory. Freeze input identities, internal task numbers, and distinct output destinations. Quote filenames and paths throughout.
3. Save exact commands, environment, validation rules, resource requests, and limits. Keep other runs' results separate unless reuse has been verified.

## Choose resources

4. Check cluster/account restrictions and choose a compatible partition. Request only resources the program can use; distinguish independent processes from threads.
5. Estimate memory and runtime from comparable successful runs. Without sufficient evidence, pilot representative inputs, including demanding cases when identifiable.
6. Validate pilots and inspect measurements. Use bounded margins, group different workloads when useful, and count validated pilots as completed work.
7. Respect total submission and simultaneous-running limits across every array and job in this run. Prefer non-preemptible execution without proven safe restart.

## Submit and track

8. Generate scripts with explicit environment setup, resources, task selection, separate attempt logs, and unique temporary output locations.
9. Record intent before submission, then save returned IDs. Reconcile uncertain submissions with Slurm before trying again. Prevent overlapping attempts for one input.
10. Check live jobs and completed-job accounting. Waiting, running, and completing tasks are ineligible for retry. Missing or delayed accounting means an uncertain outcome; investigate before retrying.

## Validate and publish

11. Require successful program execution and program-specific checks of the current attempt. File existence, a zero exit alone, or a completion message is insufficient.
12. Publish only validated output, verify its final destination, then record success and a completion message identifying the input and outputs. A copy or validation failure stays unresolved.

## Recover failures

13. Diagnose stopped failures using scheduler records, program logs, and output checks:
    - Memory exhaustion: increase memory within authorized limits.
    - Time limit: increase runtime or choose a suitable partition within limits.
    - Temporary infrastructure failure: retry within the attempt limit.
    - Invalid input, command error, or missing software: fix the cause before retrying.
14. Preserve verified successes. Retry only unresolved inputs whose previous attempts have stopped; keep logs and record each retry reason.
15. Use fresh output unless safe recovery has been demonstrated. Elapsed time, output size, or a “nearly finished” message does not prove appending is safe.
16. Validated files and independent stages can be recovery points. Restoring a program's internal state requires actual checkpoint support.

## Known gotchas

- Spaces in filenames require quoted paths and a manifest parser that preserves complete names.
- Successful process exit can still produce incomplete output; validation must detect that.
- Old logs, outputs, or completion messages cannot establish success for a new attempt.
- A missing live-job entry alone does not establish a completed or retryable job; reconcile accounting.
- Accounting can lag. Blank memory fields mean unavailable, not zero; batch-step measurements may be available. Distinguish program-only measurements from allocation-wide usage.
- Array throttles apply per array. Keep the total concurrency within limits when several arrays or verification jobs exist.
- Queue priority, completion cleanup, and scheduler intervals can delay short jobs. Read current state; do not duplicate submissions to accelerate progress.
- Site settings, software, and accounts change. Revalidate saved profiles rather than assuming old test settings still apply.
- Archived scripts can contain absolute paths. Prepare new scripts and manifests without altering original evidence.

## Completion and handoff

Before declaring the run fully successful, verify and record:

- Every intended input has one validated final result; publications and destinations were checked.
- Every success has successful execution plus the program-specific validation evidence.
- No attempts remain waiting, running, completing, or uncertain; scheduler outcomes are reconciled.
- Only eligible unresolved inputs were retried, within attempt and resource ceilings; verified successes were preserved.
- Frozen input mappings and required records are intact; all attempt logs and retry reasons are retained.
- Available accounting supports resource and concurrency claims; unavailable measurements are named explicitly.
- The report states successful inputs, inputs recovered after retry, and unresolved inputs with reasons.

If work remains unresolved, report that outcome honestly rather than declaring full success. Before resuming, reconcile durable records with Slurm and stored outputs.

Use filenames and plain-language states: waiting, running, verifying, successful, retrying, or needs attention. Check progress while active or when invoked. Unattended checking requires an explicitly configured wake-up mechanism; an inactive chat is not monitoring jobs.
