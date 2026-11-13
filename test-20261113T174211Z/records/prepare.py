from pathlib import Path
import json,hashlib,shutil,subprocess,datetime,os
r=Path(__file__).resolve().parent.parent
old=r.parent/'test-20261112T221451Z'
for name in ['scripts','inputs','outputs','expected','attempts','logs','locks']:(r/name).mkdir()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def capture(name,cmd):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
 (r/'records'/(name+'.stdout')).write_text(p.stdout);(r/'records'/(name+'.stderr')).write_text(p.stderr)
 return dict(command=cmd,exit=p.returncode,stdout='records/'+name+'.stdout',stderr='records/'+name+'.stderr')
now=datetime.datetime.utcnow().isoformat()+'Z'
rows=json.loads((old/'manifest.json').read_text())
for row in rows:
 src=Path(row['input']);dst=r/'inputs'/row['name'];shutil.copyfile(str(src),str(dst));dst.chmod(0o440)
 row.update(input=str(dst),output=str(r/'outputs'/row['name']),size=dst.stat().st_size,sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
save(r/'manifest.json',rows);(r/'manifest.json').chmod(0o440)
shutil.copyfile(str(old/'uppercase.py'),str(r/'scripts/uppercase.py'))
shutil.copyfile(str(old/'records/final-evidence.json'),str(r/'records/comparable-run-evidence.json'))
shutil.copyfile(str(old/'records/accounting.psv'),str(r/'records/comparable-accounting.psv'))
evidence={}
commands={
 'partition':['scontrol','show','partition','msismall'],
 'account':['sacctmgr','-nP','show','assoc','where','user=lamx0031','account=support'],
 'qos':['sacctmgr','-nP','show','qos','where','name=normal,common_agate'],
 'cluster-config':['scontrol','show','config'],
 'preexisting-jobs':['squeue','--me','-h','-o','%i|%T'],
 'python-version':['/usr/bin/python3','--version'],
 'tr-version':['/usr/bin/tr','--version'],
 'time-version':['/usr/bin/time','--version']}
for name,cmd in commands.items():evidence[name]=capture(name,cmd)
assert all(x['exit']==0 for x in evidence.values()),evidence
save(r/'cluster-profile.json',dict(observed_at=now,cluster='agate',access='local Slurm CLI on cn1002',account='support',partition='msismall',qos='normal',partition_qos='common_agate',preemption='OFF',environment='System Python 3.6.8; GNU tr and time; no modules required',limits=dict(account_max_jobs=5000,account_max_submit=5000,documented_scheduler_jobs=2000,max_array_size=100001,complete_wait_seconds=150),evidence=evidence,documentation='https://userdocs.msi.umn.edu/compute/slurm_job_submission.html',skill_path='/projects/standard/support/shared/lamx0031/Codex/genesis-skills/skills/hpc-skills/slurm/SKILL.md'))
resources=dict(cpus=1,memory_mib=256,time_seconds=300,gpus=0,nodes=1)
ceilings=dict(cpus_per_attempt=1,memory_mib_per_attempt=1024,time_seconds_per_attempt=300,max_running=2,max_retries_per_input=1,gpus=0)
program=dict(name='uppercase test',software='/usr/bin/python3 3.6.8',script='scripts/uppercase.py',command_template=['/usr/bin/python3','scripts/uppercase.py','INPUT','ATTEMPT_OUTPUT','--mode','MODE','--attempt','ATTEMPT'],parallelism='one serial process; one CPU; no GPUs, MPI, extra threads, modules, or containers',validation='Independent LC_ALL=C /usr/bin/tr a-z A-Z; program exit 0 and exact entire byte equality before and after publication',success='Validated final output and per-attempt completion.json; file existence or completion text alone never sufficient',recovery='Fresh output on retry; no append or checkpoint; deliberate first-attempt failures retained',version_sha256=hashlib.sha256((r/'scripts/uppercase.py').read_bytes()).hexdigest())
save(r/'program-profile.json',program)
config=dict(run_id=r.name,created_at=now,instructions='records/AGENTS.md',previous_instructions='records/AGENTS.before.md',test_request='prompt.txt',manifest='manifest.json',resources=resources,authorized_ceilings=ceilings,environment=dict(LC_ALL='C',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1'),command_template=program['command_template'],validation=program['validation'],resource_rationale='Comparable completed run test-20261112T221451Z used one CPU, 256 MiB and 5 minutes; batch peak RSS 12896-13048 KiB and elapsed 4-5 seconds. Retain the proven request; no additional pilot needed for identical program and inputs.',plan='First attempts 1-6%2, then only diagnosed stopped failures once; final Slurm audit after processing stops. No overlapping waves.',record_paths=dict(scripts='scripts',attempts='attempts',scheduler_logs='logs',records='records',report='REPORT.md',final_audit='records/final-audit.json',completion='records/completion-checklist.json'),input_selection='Exact six disposable ASCII text inputs from frozen prior manifest; no directory glob selection',original_run=str(old),publishing='Local preparation only; report to user before any GitHub push')
save(r/'run-config.json',config)
for row in rows:assert Path(row['input']).is_file() and os.access(row['input'],os.R_OK)
probe=r/'outputs/.writable-check';probe.write_text('writable');probe.unlink()
preexisting=(r/'records/preexisting-jobs.stdout').read_text().strip().splitlines();assert len(preexisting)+9<2000
save(r/'records/preflight.json',dict(observed_at=now,inputs_readable=True,outputs_writable=True,input_count=len(rows),existing_scheduler_entries=len(preexisting),compatible_with_authorized_ceilings=True,original_program_unchanged=(r/'scripts/uppercase.py').read_bytes()==(old/'uppercase.py').read_bytes(),source_documentation='https://userdocs.msi.umn.edu/compute/slurm_job_submission.html',evidence=evidence))
print(r)
