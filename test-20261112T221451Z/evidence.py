import json,subprocess,re
from pathlib import Path
r=Path(__file__).resolve().parent
subprocess.check_call(['/usr/bin/python3',str(r/'report.py')])
text=(r/'records/accounting.psv').read_text()
events=[];batch_rss=[];elapsed=[];resources=[];terminal=[]
for line in text.splitlines():
 f=line.split('|')
 if len(f)<12: continue
 job,name,state,exitcode,wall,cpus,mem,rss,limit,start,end,tres=f[:12]
 if '.batch' in job and rss:batch_rss.append((job,rss))
 if '.' not in job:
  resources.append((job,cpus,mem,limit,tres));terminal.append((job,state,exitcode))
  if start not in ('Unknown','None','') and end not in ('Unknown','None',''):
   events.extend([(start,1,job),(end,-1,job)])
active=peak=0
for _,delta,_ in sorted(events): active+=delta;peak=max(peak,active)
checks=subprocess.run(['sha256sum','-c',str(r/'records/frozen-sha256.txt')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
(r/'records/frozen-verification.txt').write_text(checks.stdout+checks.stderr)
lines=['','## Final accounting evidence','','Maximum simultaneous task allocations from accounting start/end times: **%d**.'%peak,'','| Array task | Scheduler state | Exit | CPUs | Memory request | Time limit |','|---|---|---|---|---|---|']
for (job,state,exitcode),(_,cpus,mem,limit,tres) in zip(terminal,resources):lines.append('| %s | %s | %s | %s | %s | %s |'%(job,state,exitcode,cpus,mem,limit))
lines+=['','Batch-step peak RSS measurements: '+', '.join('%s: %s'%v for v in batch_rss)+'.','', 'Array-task MaxRSS fields are blank; batch-step memory and per-program GNU time measurements are available. Accounting elapsed times include batch startup and are distinct from program-only timing.','', 'Frozen manifest, deliberate-failure program, worker, and Slurm script SHA-256 verification: '+('PASS' if checks.returncode==0 else 'FAIL')+'.']
with (r/'REPORT.md').open('a') as f:f.write('\n'.join(lines)+'\n')
summary=dict(max_concurrent_allocations=peak,task_allocations=len(terminal),terminal=terminal,batch_peak_rss=batch_rss,frozen_sha256_pass=checks.returncode==0)
(r/'records/final-evidence.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
