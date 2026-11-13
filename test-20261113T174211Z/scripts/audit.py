import os,sys,subprocess,json,re
from pathlib import Path
from common import ROOT as r,read,save,sha,now,environment
assert os.environ.get('SLURM_JOB_ID'),'audit must run through Slurm'
result=dict(started=now(),job_id=os.environ['SLURM_JOB_ID'],environment=environment(),checks={},inputs=[],status='verifying')
def check(name,condition):
 result['checks'][name]=bool(condition)
 assert condition,name
try:
 manifest=read(r/'manifest.json');config=read(r/'run-config.json')
 check('all_frozen_files_unchanged',all(sha(r/p)==h for p,h in read(r/'records/frozen-sha256.json').items()))
 old=Path(config['original_run']);before=read(r/'records/original-run-before.json')
 after={str(p.relative_to(old)):sha(p) for p in old.rglob('*') if p.is_file()}
 check('original_test_all_files_unchanged',before==after)
 check('deliberate_failure_program_unchanged',sha(r/'scripts/uppercase.py')==sha(old/'uppercase.py'))
 reconciliation=read(r/'records/processing-final-reconciliation.json')
 check('processing_attempts_stopped_and_known',reconciliation['all_stopped_known'])
 accounts={a['job']:a for a in reconciliation['allocations']}
 all_attempts=[]
 for row in manifest:
  check('input_identity_task_%d'%row['task'],sha(row['input'])==row['sha256'] and Path(row['input']).stat().st_size==row['size'])
  expected=subprocess.check_output(['/usr/bin/tr','a-z','A-Z'],input=Path(row['input']).read_bytes(),env=dict(os.environ,LC_ALL='C'))
  check('exact_final_task_%d'%row['task'],Path(row['output']).read_bytes()==expected==(r/'expected'/row['name']).read_bytes())
  attempts=[read(p) for p in sorted((r/'attempts').glob('task-%d-attempt-*/result.json'%row['task']))]
  check('attempt_count_task_%d'%row['task'],len(attempts)==(2 if row['task'] in (5,6) else 1))
  latest=attempts[-1];job=latest['array_job_id']+'_'+str(row['task'])
  check('success_evidence_task_%d'%row['task'],latest['status']=='successful' and latest['program_exit']==latest['worker_exit']==0 and latest['validation']['final_exact_match'] and latest['publication']=='verified' and accounts[job]['state']=='COMPLETED' and accounts[job]['exit_code']=='0:0')
  for a in attempts:
   folder=r/'attempts'/('task-%d-attempt-%d'%(row['task'],a['attempt']))
   check('records_task_%d_attempt_%d'%(row['task'],a['attempt']),all((folder/p).exists() for p in ('started.json','result.json','program.stdout','program.stderr','time.txt','scheduler-accounting.json')) and all(k in a for k in ('command','environment','resources','started','ended','program_exit','worker_exit','validation','publication','retry_reason')))
   all_attempts.append(a)
  if row['task'] in (5,6):
   first=attempts[0];first_out=Path(first['output']);expected_exit=23 if row['task']==5 else 0
   check('deliberate_failure_task_%d'%row['task'],first['program_exit']==expected_exit and first['worker_exit']==(23 if row['task']==5 else 86) and first_out.read_bytes()!=expected and first['publication']=='not attempted' and first['status']=='needs attention')
  result['inputs'].append(dict(task=row['task'],name=row['name'],output=row['output'],bytes=len(expected),sha256=sha(row['output']),attempts=len(attempts),retry_reason=latest['retry_reason'],exact_match=True))
 check('eight_processing_attempts',len(all_attempts)==len(accounts)==8)
 first_review=read(r/'records/first-wave-review.json')
 check('failed_outputs_not_published_after_first_wave',first_review['unpublished_failed_tasks']==[5,6])
 check('successful_outputs_preserved',all(sha(p)==h for p,h in first_review['successful_output_sha256'].items()))
 events=[]
 for a in reconciliation['allocations']:
  check('resources_'+a['job'],a['cpus']=='1' and a['requested_memory']=='256M' and a['time_limit']=='00:05:00' and 'gres/gpu' not in a['allocated_tres'])
  check('known_times_'+a['job'],a['start'] not in ('Unknown','') and a['end'] not in ('Unknown',''))
  events.extend([(a['start'],1),(a['end'],-1)])
 active=peak=0
 for _,delta in sorted(events):active+=delta;peak=max(peak,active)
 check('processing_global_concurrency_within_limit',peak<=2)
 result.update(status='successful',successful_inputs=len(manifest),recovered_after_retry=2,unresolved=0,max_processing_concurrency=peak,original_run_file_count=len(before),processing_attempts=8)
 code=0
except Exception as e:
 result.update(status='needs attention',reason=repr(e));code=1
result.update(ended=now(),exit_code=code);save(r/'records/final-audit.json',result)
print(json.dumps(result,indent=2));sys.exit(code)
