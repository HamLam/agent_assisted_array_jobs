import sys,os,subprocess,fcntl,socket
from pathlib import Path
from common import ROOT as r,read,save,sha,now,environment
assert os.environ.get('SLURM_JOB_ID'),'processing must run through Slurm'
task=int(os.environ['SLURM_ARRAY_TASK_ID']);attempt=int(sys.argv[1]);assert attempt in (1,2)
row=read(r/'manifest.json')[task-1];assert row['task']==task
lock=(r/'locks'/str(task)).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
a=r/'attempts'/('task-%d-attempt-%d'%(task,attempt));a.mkdir()
config=read(r/'run-config.json');out=a/row['name'];final=Path(row['output'])
cmd=['/usr/bin/time','-v','-o',str(a/'time.txt'),'/usr/bin/python3',str(r/'scripts/uppercase.py'),row['input'],str(out),'--mode',row['mode'],'--attempt',str(attempt)]
rec=dict(task=task,name=row['name'],input=row['input'],attempt=attempt,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ['SLURM_ARRAY_JOB_ID'],host=socket.gethostname(),started=now(),command=cmd,environment=environment(),python=sys.version,resources=config['resources'],output=str(out),final_output=str(final),logs=dict(stdout=str(a/'program.stdout'),stderr=str(a/'program.stderr'),measurements=str(a/'time.txt')),scheduler_state='unavailable until accounting reconciliation',measurements=dict(program_gnu_time=str(a/'time.txt'),allocation_maxrss='unavailable until accounting reconciliation'),retry_reason='not a retry',status='running',validation=dict(attempt_exact_match=False,final_exact_match=False),publication='not attempted',program_exit='unavailable',worker_exit='unavailable')
if attempt==2:
 recovery=read(r/'records/retry-plan.json')
 rec['retry_reason']=next(x['reason'] for x in recovery['tasks'] if x['task']==task)
save(a/'started.json',rec)
try:
 assert sha(r/'manifest.json')==read(r/'records/frozen-sha256.json')['manifest.json'],'manifest changed'
 assert Path(row['input']).stat().st_size==row['size'] and sha(row['input'])==row['sha256'],'input changed'
 assert not final.exists(),'refusing to replace a successful output'
 data=Path(row['input']).read_bytes()
 expected=subprocess.check_output(['/usr/bin/tr','a-z','A-Z'],input=data,env=dict(os.environ,LC_ALL='C'))
 ep=r/'expected'/row['name']
 if ep.exists():assert ep.read_bytes()==expected,'expected output changed'
 else:
  with ep.open('xb') as f:f.write(expected)
  ep.chmod(0o440)
 with (a/'program.stdout').open('w') as stdout,(a/'program.stderr').open('w') as stderr:
  rc=subprocess.call(cmd,stdout=stdout,stderr=stderr)
 exact=out.is_file() and out.read_bytes()==expected
 rec.update(program_exit=rc,expected_bytes=len(expected),actual_bytes=out.stat().st_size if out.exists() else None)
 rec['validation'].update(attempt_exact_match=exact,method='exact byte comparison against independent LC_ALL=C tr a-z A-Z')
 if rc:
  rec.update(status='needs attention',reason='program exited %d after deliberate partial output'%rc);code=rc
 elif not exact:
  rec.update(status='needs attention',reason='program exit 0 but exact byte comparison rejected incomplete output');code=86
 else:
  os.link(str(out),str(final));rec['publication']='published; verifying'
  assert final.read_bytes()==expected,'published output mismatch'
  final.chmod(0o440)
  rec['validation']['final_exact_match']=True
  rec.update(status='successful',publication='verified',output_sha256=sha(final),reason='successful execution, validation, and publication');code=0
  save(a/'completion.json',dict(input=row['input'],output=str(final),attempt=attempt,job_id=rec['job_id'],verified_at=now(),sha256=sha(final)))
except Exception as e:
 rec.update(status='needs attention',reason=repr(e));code=87
rec.update(ended=now(),worker_exit=code)
save(a/'result.json',rec);print(__import__('json').dumps(rec),flush=True);sys.exit(code)
