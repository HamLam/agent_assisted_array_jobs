import os,sys,json,hashlib,subprocess,fcntl,socket,datetime
from pathlib import Path
r=Path(__file__).resolve().parent
def now(): return datetime.datetime.utcnow().isoformat()+'Z'
task=int(os.environ['SLURM_ARRAY_TASK_ID']);attempt=int(sys.argv[1])
assert attempt in (1,2)
row=json.loads((r/'manifest.json').read_text())[task-1];assert row['task']==task
lock=open(str(r/'locks'/str(task)),'a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
a=r/'attempts'/('task-%d-attempt-%d'%(task,attempt));a.mkdir()
rec=dict(task=task,name=row['name'],attempt=attempt,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ['SLURM_ARRAY_JOB_ID'],host=socket.gethostname(),started=now(),resources=dict(cpus=1,memory_mib=256,time_seconds=300,gpus=0),status='running')
def save(): (a/'result.json').write_text(json.dumps(rec,indent=2)+'\n')
save()
try:
 data=Path(row['input']).read_bytes()
 assert len(data)==row['size'] and hashlib.sha256(data).hexdigest()==row['sha256'],'input identity changed'
 expected=subprocess.check_output(['/usr/bin/tr','a-z','A-Z'],input=data,env=dict(os.environ,LC_ALL='C'))
 ep=r/'expected'/row['name']
 if ep.exists(): assert ep.read_bytes()==expected,'expected result changed'
 else: ep.write_bytes(expected)
 out=a/row['name']
 cmd=['/usr/bin/time','-v','-o',str(a/'time.txt'),'/usr/bin/python3',str(r/'uppercase.py'),row['input'],str(out),'--mode',row['mode'],'--attempt',str(attempt)]
 rec['command']=cmd;save()
 with (a/'program.stdout').open('w') as stdout,(a/'program.stderr').open('w') as stderr:
  rc=subprocess.call(cmd,stdout=stdout,stderr=stderr)
 exact=out.exists() and out.read_bytes()==expected
 rec.update(program_exit=rc,attempt_exact_match=exact,expected_bytes=len(expected),actual_bytes=out.stat().st_size if out.exists() else None)
 if rc!=0:
  rec.update(status='needs attention',reason='program exited %d after deliberate partial output'%rc);code=rc
 elif not exact:
  rec.update(status='needs attention',reason='program exit 0 but exact byte comparison rejected incomplete output');code=86
 else:
  final=Path(row['output']);assert not final.exists(),'refusing to overwrite existing final'
  # Hard link publishes an already validated file atomically without replacement.
  os.link(str(out),str(final))
  assert final.read_bytes()==expected,'published output mismatch'
  rec.update(status='successful',final_exact_match=True,output=str(final),output_sha256=hashlib.sha256(final.read_bytes()).hexdigest());code=0
  (a/'completion.txt').write_text('SUCCESS: %s -> %s; exact byte comparison passed\n'%(row['input'],final))
except Exception as e:
 rec.update(status='needs attention',reason=repr(e));code=87
rec['ended']=now();save();print(json.dumps(rec),flush=True);sys.exit(code)
