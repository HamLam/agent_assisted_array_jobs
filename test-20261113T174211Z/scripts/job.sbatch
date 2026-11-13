#!/bin/bash -l
#SBATCH --account=support
#SBATCH --partition=msismall
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=256M
#SBATCH --time=00:05:00
#SBATCH --no-requeue
#SBATCH --mail-type=NONE
set -euo pipefail
cd /projects/standard/support/shared/lamx0031/Codex/slurm_agent/test-20261113T174211Z
export LC_ALL=C OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
if [[ "$1" == "audit" ]]; then
    exec /usr/bin/python3 scripts/audit.py
fi
exec /usr/bin/python3 scripts/worker.py "$1"
