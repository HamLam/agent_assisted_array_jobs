import json,os,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
TERMINAL={'COMPLETED','FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE','REVOKED'}
def now():return datetime.datetime.utcnow().isoformat()+'Z'
def read(path):return json.loads(Path(path).read_text())
def save(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.tmp')
 with tmp.open('w') as f:
  json.dump(data,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(str(tmp),str(path))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def environment():
 keys=['LC_ALL','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','SLURM_CPUS_PER_TASK','SLURM_MEM_PER_NODE','SLURM_JOB_PARTITION','SLURM_JOB_ACCOUNT','SLURM_JOB_QOS','SLURM_JOB_ID','SLURM_ARRAY_JOB_ID','SLURM_ARRAY_TASK_ID']
 return {k:os.environ.get(k,'unavailable') for k in keys}
