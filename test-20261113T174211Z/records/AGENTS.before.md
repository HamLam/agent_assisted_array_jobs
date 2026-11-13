MSI Slurm array workflow instructions

Purpose

Help users process many independent data files through Slurm arrays. Handle job preparation, resource selection, submission, progress checks, and recovery through ordinary Slurm commands.

The user normally provides:
- Input data location.
- Output location.
- Program or command to run.

Use the Genesis Slurm skill for general Slurm procedures. Use MSI documentation and current cluster information for site-specific requirements. Preserve input filenames; array numbers are internal references to a saved file list.

Reusable setup

Maintain a cluster profile containing access details, submission account, available partitions, environment setup, and applicable limits.

Maintain a profile for each program containing:
- How to pass one input file and specify its outputs.
- Required options, software version, modules, or container.
- Whether it uses multiple CPUs, GPUs, or multiple nodes.
- What outputs demonstrate success and how to check them.
- Any proven restart or independently repeatable processing steps.

Learn these details from documentation, inspection, and trial runs. Ask a focused question only when missing information prevents a reliable decision. A program name alone may not specify the intended analysis.

Establish reusable ceilings for resource use, simultaneous tasks, and retries. Once submission and recovery are authorized within those ceilings, proceed without repeatedly requesting confirmation.

Prepare each run

1. Check that inputs are readable and the output location is writable. Select files using the program’s known input rules. If selection is ambiguous, resolve it before submission.

2. Create a unique run record. Freeze the input list and assign each file an internal task number and distinct output destination. Record enough file identity information to detect changed inputs. Never rebuild this mapping during retries.

3. Record the exact command, environment, output checks, and intended resource requests. Keep existing results from other runs separate unless their reuse has been verified.

Choose resources

4. Inspect current cluster/account restrictions. Choose a compatible partition and request only resources the program can use. Distinguish independent processes from threads; do not request extra CPUs merely because inputs are numerous.

5. Use comparable successful runs to estimate memory and runtime. If evidence is insufficient, submit a few representative inputs as pilot tasks, including demanding cases when identifiable.

6. Check pilot outputs and measured resource use. Choose bounded margins and group substantially different workloads into separate arrays when useful. Count validated pilot results as completed work.

7. Respect both total submission limits and simultaneous-running limits. Prefer non-preemptible execution for programs without a proven restart method.

Submit and track

8. Generate the Slurm script, including environment setup, per-task input selection, resource requests, and separate attempt logs. Use a unique temporary output location for each attempt.

9. Record submission intent before submitting, then save the returned job IDs. If submission outcome is uncertain, reconcile with Slurm before resubmitting. Prevent overlapping attempts for the same input.

10. Check current jobs and completed-job accounting. Waiting, running, and completing tasks are not eligible for retry. If accounting is delayed or unavailable, label the outcome uncertain and investigate.

Verify results

11. Require both successful program execution and the program-specific output checks. File existence alone is insufficient. Use only outputs and completion messages belonging to the current attempt.

12. Publish validated outputs to their final destinations, then record success and write a completion message identifying the input and outputs. A failed output copy or validation remains unresolved.

Recover failures

13. Diagnose each stopped, unsuccessful task using scheduler information, program logs, and output checks:
- Memory exhaustion: increase memory within limits.
- Time limit: increase runtime or select a suitable partition within limits.
- Temporary infrastructure failure: retry within the attempt limit.
- Invalid input, command errors, or missing software: resolve the cause before retrying.

14. Preserve verified successes. Retry only unresolved inputs whose previous attempts have stopped. Keep all attempt logs and record why each retry was chosen.

15. Restart failed computation with fresh output unless a safe recovery method has been demonstrated. Never infer that appending is safe from elapsed time, output size, or a “nearly finished” message.

16. Treat validated completed files or independent stages as recovery points. These records do not restore the internal state of a program without checkpoint support.

Report and resume

Keep a durable record of inputs, commands, environments, scripts, resource decisions, job IDs, attempts, output verification, and retry reasons.

When resuming, reconcile that record with Slurm and stored outputs before taking action.

Report progress using filenames and plain language: waiting, running, verifying, successful, retrying, or needs attention. At completion, state how many inputs succeeded, how many recovered after retry, and what remains unresolved.

Check progress while active or when invoked. Unattended checking requires an explicitly configured mechanism to wake the agent; do not imply that an inactive chat is monitoring jobs.
