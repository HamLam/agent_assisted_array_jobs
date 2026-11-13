import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from common import ROOT as r,read,save,sha,now,TERMINAL
from reconcile import reconcile
state=reconcile();audit=read(r/'records/final-audit.json')
config=read(r/'run-config.json');manifest=read(r/'manifest.json')
submissions=[read(p) for p in sorted((r/'records').glob('submission-*.json'))]
accounts={a['job']:a for a in state['allocations']}
checks=dict(all_six_final_outputs_validated=audit.get('successful_inputs')==6 and all(x['exact_match'] for x in audit.get('inputs',[])),execution_and_validation_evidence=audit['checks'].get('processing_attempts_stopped_and_known',False) and audit['checks'].get('eight_processing_attempts',False),all_jobs_stopped_and_reconciled=state['all_stopped_known'],selective_retries_and_successes_preserved=audit['checks'].get('successful_outputs_preserved',False) and audit.get('recovered_after_retry')==2,frozen_records_intact=audit['checks'].get('all_frozen_files_unchanged',False),original_test_unchanged=audit['checks'].get('original_test_all_files_unchanged',False),final_slurm_audit_successful=audit['status']=='successful' and accounts.get(audit['job_id'],{}).get('state')=='COMPLETED' and accounts.get(audit['job_id'],{}).get('exit_code')=='0:0')
events=[];resource_ok=True
for a in state['allocations']:
 resource_ok=resource_ok and a['cpus']=='1' and a['requested_memory']=='256M' and a['time_limit']=='00:05:00' and 'gres/gpu' not in a['allocated_tres']
 events.extend([(a['start'],1),(a['end'],-1)])
active=peak=0
for _,delta in sorted(events):active+=delta;peak=max(peak,active)
checks['resources_and_total_concurrency_within_limits']=resource_ok and peak<=2 and len(accounts)==9
required_attempt={'task','name','input','attempt','job_id','array_job_id','host','started','ended','command','environment','resources','output','final_output','logs','program_exit','worker_exit','validation','publication','measurements','retry_reason'}
record_issues=[];attempts_by_task={};measurements=[]
for row in manifest:
 attempts=[read(p) for p in sorted((r/'attempts').glob('task-%d-attempt-*/result.json'%row['task']))]
 attempts_by_task[row['task']]=attempts
 for a in attempts:
  folder=r/'attempts'/('task-%d-attempt-%d'%(row['task'],a['attempt']))
  missing=sorted(required_attempt-set(a))
  if missing:record_issues.append(dict(task=row['task'],attempt=a['attempt'],missing=missing))
  if not (folder/'scheduler-accounting.json').exists():record_issues.append(dict(task=row['task'],missing='scheduler-accounting.json'))
  text=(folder/'time.txt').read_text()
  m=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',text)
  elapsed=re.search(r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)',text)
  measurements.append(dict(task=row['task'],attempt=a['attempt'],program_maxrss_kib=int(m.group(1)) if m else 'unavailable',program_wall=elapsed.group(1) if elapsed else 'unavailable',source=str(folder/'time.txt')))
required_root=['run-config.json','cluster-profile.json','program-profile.json','manifest.json','records/AGENTS.md','records/AGENTS.before.md','records/first-wave-review.json','records/retry-plan.json','records/request-check.json']
for path in required_root:
 if not (r/path).exists():record_issues.append(dict(missing=path))
for s in submissions:
 if not all(k in s for k in ('created_at','unique_job_name','command','tasks','attempt','resources','job_id','status')):record_issues.append(dict(incomplete_submission=s))
checks['required_records_complete']=not record_issues
save(r/'records/record-validation.json',dict(observed_at=now(),passed=not record_issues,issues=record_issues,attempt_records=sum(map(len,attempts_by_task.values())),submission_records=len(submissions),root_records=required_root))
blank=[a['job'] for a in state['allocations'] if a['max_rss']=='unavailable']
batch_rss={a['job']:a['max_rss'] for a in state['steps'] if a['job'].endswith('.batch')}
checks['measurement_gaps_explicitly_recorded']=True
checklist=dict(observed_at=now(),checks=checks,passed=all(checks.values()),successful_inputs=audit.get('successful_inputs',0),recovered_after_retry=audit.get('recovered_after_retry',0),unresolved=audit.get('unresolved',6),processing_attempts=8,verification_jobs=1,maximum_total_concurrency=peak,measurement_gaps=dict(allocation_maxrss_blank=blank,batch_step_maxrss=batch_rss),github_pushed=False)
save(r/'records/completion-checklist.json',checklist);save(r/'records/program-measurements.json',measurements)
lines=['# Revised-instructions Slurm rerun','', 'Run: `'+r.name+'`. Updated: '+now()+'.','', '**6/6 successful; 2 recovered after one retry each; 0 unresolved.**' if checklist['passed'] else '**Needs attention: inspect completion-checklist.json.**','', '## What changed','', '- Revised the reusable AGENTS.md with a repository map, setup/status commands, required record fields, known gotchas, and a completion checklist.','- Kept the original frozen-input, validation, resource-ceiling, uncertain-submission, selective-retry, and fresh-output safeguards.','- Added per-attempt environment/exit/publication records, immutable reconciliation history, a selective retry plan, and a separate Slurm final audit.','- Used comparable successful resource measurements instead of another pilot for the identical program and six inputs.','- Kept the original run intact and did not push to GitHub.','', '## Per-input evidence','', '| Input | First program / worker exit | Retry | Final exact match |','|---|---|---|---|']
for row in manifest:
 attempts=attempts_by_task[row['task']];first=attempts[0];latest=attempts[-1]
 retry=(latest['array_job_id']+'_'+str(row['task'])+'; '+latest['retry_reason']) if len(attempts)>1 else 'Not needed'
 lines.append('| %s | %s / %s | %s | %s |'%(row['name'],first['program_exit'],first['worker_exit'],retry,'PASS' if latest['validation']['final_exact_match'] else 'FAIL'))
lines+=['','The worker requires program exit 0 and exact byte equality against independent `LC_ALL=C tr a-z A-Z`, then compares the published bytes again. A separate Slurm audit recalculated expectations for all six final files. Both deliberate first-attempt failures remain byte-for-byte unchanged in the test program. Failed partial outputs and their logs are retained.','','## Job and resource evidence','','| Slurm job/task | State | Exit | CPUs | Memory request | Time limit | Batch peak RSS |','|---|---|---|---|---|---|---|']
for a in state['allocations']:lines.append('| %s | %s | %s | %s | %s | %s | %s |'%(a['job'],a['state'],a['exit_code'],a['cpus'],a['requested_memory'],a['time_limit'],batch_rss.get(a['job']+'.batch','unavailable')))
lines+=['','Maximum simultaneous allocations across processing and verification: **%d**. Each job requested one CPU, 256 MiB, five minutes, no GPUs. Processing used eight attempts; the ninth job performed verification only.'%peak,'','Job/allocation-level MaxRSS is blank for %d records. Batch-step RSS and program-only GNU time measurements are saved separately; blank measurements are not treated as zero. Program-only timing/memory excludes the worker and scheduler startup.'%len(blank),'','## Completion checklist','']
for k,v in checks.items():lines.append('- [%s] %s'%('x' if v else ' ',k.replace('_',' ')))
lines+=['','Original archive integrity: all **%d files** retain their previous content hashes. Normal-case outputs were also hashed before retry and checked unchanged afterward.'%audit.get('original_run_file_count',0),'','## Evidence files','','- `records/AGENTS.before.md`, `records/AGENTS.md`, `records/AGENTS.diff`: original instructions, revised snapshot, and changes.','- `run-config.json`, profiles, and `manifest.json`: limits, commands, validation, resource rationale, environment, and frozen file identities.','- `records/submission-*.json`, `retry-plan.json`, and `reconciliations/`: intent, job IDs, retry eligibility/reasons, and scheduler evidence.','- `attempts/`: separate started/result/completion records, program logs, partial or complete output, GNU time, and attached scheduler accounting.','- `records/final-audit.json`: independent Slurm verification and immutable-original-run checks.','- `records/record-validation.json`, `completion-checklist.json`, and `accounting.psv`: required-record checks, completion evidence, and resource measurements.','','## Interpretation','','This rerun exercises the revised instructions in one active agent session. It verifies the six controlled outcomes and the required records/checklist. It does not simulate an agent restart, lost submission response, genuine memory exhaustion, or a real time-limit failure. Those recovery rules remain instructions, not claims of additional tests.','','All changes and new artifacts remain local pending the user review requested before any GitHub push.']
(r/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(checklist,indent=2));assert checklist['passed'],'completion checklist has unresolved items'
