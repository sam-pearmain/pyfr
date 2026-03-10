#!/bin/bash
#SBATCH --job-name=pyfr-mindrag
#SBATCH --partition=interruptible_gpu
#SBATCH --ntasks=6
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --gres=gpu:6
#SBATCH --time=24:00:00
#SBATCH --output=pyfr-mindrag-%j.log
#SBATCH --error=pyfr-mindrag-%j.err
#SBATCH --constraint=l40s

RUN_DIR="/scratch/users/k24108571/mindrag-mesh-sens"
N=6

cd "${HOME}/pyfr"
source .venv/bin/activate
source initenv.sh

cd "${RUN_DIR}/fine"

rm -rf /out 
rm forces.csv
mkdir out

MESH=$(ls *.pyfrm | head -n 1)
INI=$(ls *.ini | head -n 1)

pyfr partition "${N}" -p scotch -e pri:1 -e hex:1 "${MESH}" .

echo "starting pyfr"
mpiexec -n "${N}" pyfr run -b cuda "${MESH}" "${INI}"