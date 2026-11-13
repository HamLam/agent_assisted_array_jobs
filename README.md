# Agent-assisted Slurm array job management

![Agent-assisted Slurm array job workflow](Agent_Array_workflow.png)

This project explores how an agent can manage many independent file-processing jobs through Slurm arrays. A user supplies the input location, output location, and intended program or analysis. The agent turns that request into a reproducible run: prepare inputs, select resources, submit arrays, check results, recover eligible failures, and report the outcome.

The agent manages the workflow through ordinary Slurm commands. Slurm schedules and executes the jobs; the program performs the analysis. Completion requires both successful execution and program-specific output validation.

## Roles and responsibilities

- **Understand the work.** Confirm inputs, outputs, program options, software needs, and success checks. Clarify missing details.
- **Learn the cluster.** Check access, accounts, partitions, software, and limits. Save reusable cluster and program profiles.
- **Set limits.** Agree on resource, concurrency, and retry ceilings; proceed within them without repeated approval.
- **Prepare the run.** Check file access, freeze input identities and task mappings, preserve filenames, and assign separate outputs.
- **Choose resources.** Use past results or measured pilots to size requests. Group different workloads and retain validated pilot results.
- **Submit safely.** Save scripts, environment, requests, submission intent, job IDs, and separate attempt logs. Reconcile uncertain submissions; prevent overlaps.
- **Track progress.** Check live jobs and accounting. Investigate uncertain outcomes before retrying.
- **Validate outputs.** Require successful execution and program-specific checks. Publish, verify, and record only valid results.
- **Recover selectively.** Diagnose stopped failures, fix their causes, and retry unresolved inputs within limits. Preserve successes.
- **Restart safely.** Use fresh output unless safe recovery is proven. Internal-state recovery requires checkpoints.
- **Keep records.** Save commands, environments, inputs, scripts, jobs, attempts, checks, measurements, and retry reasons. Reconcile records before resuming.
- **Report clearly.** Use filenames and plain-language states. Count successes, recoveries, unresolved inputs, and missing measurements.

The user chooses the analysis and authorizes its limits. Unattended monitoring needs an explicitly configured wake-up mechanism.

## How AGENTS.md guides a run

[`AGENTS.md`](AGENTS.md) gives the agent reusable rules for managing Slurm arrays:

- Get the input location, output location, and intended program from the user.
- Use the Genesis Slurm skill, MSI documentation, and current cluster information.
- Save cluster and program profiles, including software, output checks, and proven recovery methods.
- Establish resource, concurrency, and retry limits before submission.
- Check file access; freeze the input list, identities, task numbers, and output destinations for all attempts.
- Record the command, environment, checks, and resource requests; keep different runs separate.
- Choose compatible resources using past runs or representative pilots. Check pilot outputs and measurements; keep valid results.
- Respect submission and running limits. Prefer non-preemptible jobs when safe restart is unavailable.
- Generate scripts with separate logs and fresh temporary outputs for each attempt.
- Record submission intent, submit, and save job IDs. Check uncertain submissions before resubmitting; prevent overlapping attempts.
- Check live jobs and accounting. Never retry waiting, running, completing, or uncertain attempts.
- Require successful execution and output validation, then publish and verify final results before recording success.
- Diagnose stopped failures; adjust resources within limits or fix input, command, and software problems before retrying.
- Preserve successes and all logs. Retry only unresolved inputs, with fresh output unless safe recovery is proven.
- Treat validated files or stages as recovery points; internal-state recovery still requires checkpoints.
- Reconcile records with Slurm and outputs before resuming. Report progress, final counts, and unresolved work.
- Check progress while active or when invoked; configure a wake-up mechanism for unattended checks.

[`prompt.txt`](prompt.txt) defines the six-file test, deliberate failures, exact-output checks, and authorized test limits.

## Completed test

The [six-input text-file test](test-20261112T221451Z/README.md) demonstrates this workflow on MSI's `agate` cluster. It includes a filename containing spaces, a deliberate partial-output failure, and deliberately incomplete output from a program that exits successfully. All six final outputs passed exact comparison; two inputs recovered after one retry each.

The test folder contains its step-by-step summary, scripts, inputs, expected and final outputs, failed-attempt evidence, logs, resource profiles, and [final accounting report](test-20261112T221451Z/REPORT.md). These are archived artifacts from that run; applying the workflow to another program requires its own environment, validation rules, resource estimates, and recovery method.
