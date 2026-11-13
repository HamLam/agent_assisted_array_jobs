import sys,os,subprocess,fcntl,json
from common import ROOT as r,read,save,sha,now
from reconcile import reconcile
phase=sys.argv[1];assert phase in ('initial','retry','audit','check')
lock=(r/'records/submission.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for path,digest in read(r/'records/frozen-sha256.json').items():assert sha(r/path)==digest,'frozen file changed: '+path
config=read(r/'run-config.json');manifest=read(r/'manifest.json')
state=reconcile();assert state['all_stopped_known'],'previous wave active or accounting uncertain; no new submission'
tasks=[];argument='audit'
if phase in ('initial','check'):
 assert not list((r/'records').glob('submission-*.json')),'initial wave already has submission intent'
 tasks=[x['task'] for x in manifest];argument='1'
elif phase=='retry':
 assert not (r/'records/submission-retry.json').exists(),'retry already has submission intent'
 plan=[]
 states={a['job']:a for a in state['allocations']}
 for row in manifest:
  prev=read(r/'attempts'/('task-%d-attempt-1'%row['task'])/'result.json')
  if prev['status']=='successful':continue
  assert prev['worker_exit'] in (23,86),'unexpected cause must be resolved before automatic retry'
  job=prev['array_job_id']+'_'+str(row['task']);account=states[job]
  assert account['state']=='FAILED' and account['exit_code'].split(':')[0]==str(prev['worker_exit'])
  assert not (r/'attempts'/('task-%d-attempt-2'%row['task'])).exists()
  assert not __import__('pathlib').Path(row['output']).exists(),'unverified final output needs investigation'
  plan.append(dict(task=row['task'],name=row['name'],reason=prev['reason'],previous_job=job,accounting=account,decision='one retry with fresh output; unchanged resources'))
 tasks=[x['task'] for x in plan];assert tasks
 save(r/'records/retry-plan.json',dict(created_at=now(),tasks=plan,limits=config['authorized_ceilings']))
 argument='2'
else:
 for row in manifest:
  attempts=sorted((r/'attempts').glob('task-%d-attempt-*/result.json'%row['task']))
  assert attempts and read(attempts[-1])['status']=='successful','processing must succeed before final audit'
 assert not (r/'records/submission-audit.json').exists()
 save(r/'records/processing-final-reconciliation.json',state)
label=phase if phase!='check' else 'initial'
cmd=['sbatch','--parsable','--chdir='+str(r),'--job-name=upper-'+r.name[5:]+'-'+label,'--output='+str(r/'logs'/(label+'-%A_%a.out')),'--error='+str(r/'logs'/(label+'-%A_%a.err'))]
if tasks:cmd.append('--array='+','.join(map(str,tasks))+'%2')
if phase=='check':cmd.append('--test-only')
cmd.extend([str(r/'scripts/job.sbatch'),argument])
env={k:v for k,v in os.environ.items() if not k.startswith('SBATCH_')}
intent=dict(phase=phase,created_at=now(),unique_job_name='upper-'+r.name[5:]+'-'+label,command=cmd,tasks=tasks,attempt=None if argument=='audit' else int(argument),resources=config['resources'],status='submission intent',environment_override_policy='SBATCH_* variables removed; script has explicit requests')
record=r/'records'/('submission-'+phase+'.json' if phase!='check' else 'request-check.json')
assert not record.exists(),'do not repeat a recorded intent without reconciliation'
save(record,intent)
p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,env=env)
intent.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
if phase=='check':intent['status']='request accepted' if p.returncode==0 else 'request rejected'
elif p.returncode==0 and p.stdout.strip().split(';')[0].isdigit():intent.update(job_id=p.stdout.strip().split(';')[0],status='submitted')
else:intent['status']='uncertain: reconcile Slurm by unique name and time before any repeat'
save(record,intent);print(json.dumps(intent,indent=2));sys.exit(p.returncode)
