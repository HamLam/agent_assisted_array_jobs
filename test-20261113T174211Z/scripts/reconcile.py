import subprocess,sys,json
from common import ROOT as r,read,save,now,TERMINAL

def reconcile():
 submissions=[read(p) for p in sorted((r/'records').glob('submission-*.json'))]
 if not submissions:return dict(all_stopped_known=True,allocations=[],observed_at=now(),active=[])
 assert all(s.get('job_id') for s in submissions),'uncertain submission: reconcile by unique job name and submission time before any new submission'
 ids=','.join(s['job_id'] for s in submissions)
 qcmd=['squeue','-r','-h','-j',ids,'-o','%i|%T|%R']
 q=subprocess.run(qcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
 if q.returncode and 'Invalid job id' not in q.stderr:raise RuntimeError(q.stderr)
 cmd=['sacct','-nP','-j',ids,'--format=JobID,JobName%80,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS,Timelimit,Start,End,AllocTRES%150']
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
 assert p.returncode==0,p.stderr
 allocations=[];steps=[]
 for line in p.stdout.splitlines():
  fields=line.split('|')
  assert len(fields)>=12,line
  job,name,state,exitcode,elapsed,cpus,mem,rss,limit,start,end,tres=fields[:12]
  item=dict(job=job,name=name,state=state,exit_code=exitcode,elapsed=elapsed,cpus=cpus,requested_memory=mem,max_rss=rss or 'unavailable',time_limit=limit,start=start,end=end,allocated_tres=tres)
  (steps if '.' in job else allocations).append(item)
 expected=[]
 for s in submissions:
  expected.extend([s['job_id']+'_'+str(t) for t in s['tasks']] if s['tasks'] else [s['job_id']])
 states={a['job']:a['state'].split()[0].rstrip('+') for a in allocations}
 active=[line for line in q.stdout.splitlines() if line.strip()]
 known=not active and all(states.get(j) in TERMINAL for j in expected)
 rec=dict(observed_at=now(),job_ids=ids,squeue_command=qcmd,sacct_command=cmd,squeue_returncode=q.returncode,squeue_stderr=q.stderr,active=active,expected_jobs=expected,allocations=allocations,steps=steps,all_stopped_known=known,missing=[j for j in expected if j not in states],sacct_stderr=p.stderr)
 history=r/'records/reconciliations';history.mkdir(exist_ok=True)
 stamp=now().replace(':','').replace('.','')
 save(history/(stamp+'.json'),rec)
 (history/(stamp+'.sacct.psv')).write_text(p.stdout)
 (history/(stamp+'.squeue.txt')).write_text(q.stdout)
 save(r/'records/reconciliation.json',rec)
 (r/'records/accounting.psv').write_text(p.stdout)
 for a in (r/'attempts').glob('*/result.json'):
  result=read(a);job=result['array_job_id']+'_'+str(result['task'])
  matches=[x for x in allocations+steps if x['job']==job or x['job'].startswith(job+'.')]
  if matches:save(a.parent/'scheduler-accounting.json',dict(observed_at=rec['observed_at'],records=matches))
 return rec
if __name__=='__main__':
 rec=reconcile()
 print(json.dumps(dict(all_stopped_known=rec['all_stopped_known'],active=rec['active'],outcomes=[(a['job'],a['state'],a['exit_code']) for a in rec['allocations']]),indent=2))
