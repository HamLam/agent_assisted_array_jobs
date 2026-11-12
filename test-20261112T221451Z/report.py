from pathlib import Path
import json,subprocess,datetime
r=Path(__file__).resolve().parent
subs=[json.loads(p.read_text()) for p in sorted((r/'records').glob('submission-*.json'))]
ids=','.join(s['job_id'] for s in subs)
cmd=['sacct','-nP','-j',ids,'--format=JobID,JobName,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS,Timelimit,Start,End,AllocTRES']
p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
(r/'records/accounting.psv').write_text(p.stdout)
(r/'records/accounting.stderr').write_text(p.stderr)
rows=json.loads((r/'manifest.json').read_text())
lines=['# Slurm uppercase workflow test','', 'Updated: '+datetime.datetime.utcnow().isoformat()+'Z','', 'Each attempt requested 1 CPU, 256 MiB, five minutes, no GPUs. Arrays use `%2`; waves do not overlap. Only stopped attempts with a known accounting state are eligible for retry.','', '| Input | Attempts / Slurm array task | Result | Exact final match |','|---|---|---|---|']
success=0;recovered=0
for row in rows:
 attempts=[]
 for i in (1,2):
  p=r/'attempts'/('task-%d-attempt-%d'%(row['task'],i))/'result.json'
  if p.exists(): attempts.append(json.loads(p.read_text()))
 ok=bool(attempts and attempts[-1].get('status')=='successful' and attempts[-1].get('final_exact_match'))
 success+=int(ok);recovered+=int(ok and len(attempts)>1)
 jobs=', '.join('%s_%s (attempt %s)'%(a['array_job_id'],row['task'],a['attempt']) for a in attempts) or 'not run'
 reason='; '.join(a.get('reason',a['status']) for a in attempts) or 'waiting for submission'
 lines.append('| %s | %s | %s | %s |'%(row['name'],jobs,reason,'PASS' if ok else 'unverified'))
lines+=['','Successful: %d/6. Recovered after retry: %d. Unresolved: %d.'%(success,recovered,6-success),'','## Verification evidence','','`manifest.json` freezes task IDs, original filenames, destinations, sizes, and input SHA-256. `uppercase.py` retains both deliberate first-attempt branches. Inside Slurm, `worker.py` independently runs `/usr/bin/tr a-z A-Z` with `LC_ALL=C`, compares entire output bytes, requires program exit 0, atomically publishes validated output, and compares final bytes again. Each `attempts/task-*-attempt-*/result.json` records validation and program exit, with separate program stdout/stderr, fresh output, and GNU time measurements. Rejected attempt output is retained and never published.','','## Scheduler and measurements','','Submitted array IDs: '+ids+'. Full scheduler data: `records/accounting.psv`. Job-level MaxRSS may be blank for these very short tasks; inspect batch-step MaxRSS and per-program `time.txt` rather than claiming blank measurements are zero. GNU time measures the program process, not the whole Slurm allocation.','','## Resume','','Read submission records and reconcile every job ID using squeue and sacct before acting. Do not repeat an uncertain submission. Frozen task IDs: normal 1-4, fail-once 5, incomplete-once 6. At most two attempts per input. All computation and exact byte validation run through Slurm.']
(r/'REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines[:20]))
