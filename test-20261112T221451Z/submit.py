import sys,json,subprocess,datetime
from pathlib import Path
r=Path(__file__).resolve().parent
label,array,attempt=sys.argv[1:]
assert label in ('pilot','remaining','retry')
assert attempt in ('1','2')
# Every wave is fully reconciled before another starts: global concurrency <= 2.
for p in (r/'records').glob('submission-*.json'):
 old=json.loads(p.read_text());assert old.get('job_id'),'uncertain submission must be reconciled first'
 queued=subprocess.check_output(['squeue','-h','-j',old['job_id'],'-o','%i %T']).decode()
 assert not queued.strip(),'previous wave is still queued or active: '+queued
 if label=='retry':
  for i in (5,6):
   prev=json.loads((r/'attempts'/('task-%d-attempt-1'%i)/'result.json').read_text())
   assert prev['status']=='needs attention'
   job=prev['array_job_id']+'_'+str(i)
   accounting=subprocess.check_output(['sacct','-X','-nP','-j',job,'--format=JobIDRaw,State,ExitCode']).decode()
   assert accounting.strip() and all(line.split('|')[1].split()[0] in ('FAILED','COMPLETED') for line in accounting.splitlines()),'previous outcome uncertain'
record=r/'records'/('submission-'+label+'.json')
cmd=['sbatch','--parsable','--array='+array,'--job-name=upper-'+label+'-221451','--output='+str(r/'logs'/(label+'-%A_%a.out')),'--error='+str(r/'logs'/(label+'-%A_%a.err')),str(r/'array.sbatch'),attempt]
intent=dict(label=label,array=array,attempt=int(attempt),command=cmd,time=datetime.datetime.utcnow().isoformat()+'Z',status='submission intent')
with record.open('x') as f: json.dump(intent,f,indent=2)
p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
intent.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
if p.returncode==0 and p.stdout.strip().split(';')[0].isdigit():intent.update(job_id=p.stdout.strip().split(';')[0],status='submitted')
else:intent['status']='submission uncertain: reconcile before any repeat'
record.write_text(json.dumps(intent,indent=2)+'\n');print(json.dumps(intent,indent=2));sys.exit(p.returncode)
