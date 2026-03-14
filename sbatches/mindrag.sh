#!/bin/bash
#SBATCH --job-name=pyfr-mindrag
#SBATCH --partition=interruptible_gpu
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=12:00:00
#SBATCH --output=pyfr-mindrag-%j.log
#SBATCH --error=pyfr-mindrag-%j.err
#SBATCH --constraint=h100

RUN_DIR="/scratch/users/k24108571/mindrag-mesh-sens"
N=2

cd "${HOME}/pyfr"
source .venv/bin/activate
source initenv.sh

for CASE_DIR in "${RUN_DIR}"/*/
do
    cd "${CASE_DIR}"

    rm -rf out 
    rm -f forces.csv
    mkdir out

    MESH=$(ls *.pyfrm | head -n 1)
    INI=$(ls *.ini | head -n 1)

    pyfr partition add -f -p scotch -e pri:1 -e hex:1 "${MESH}" "${N}"

    echo "starting pyfr in ${CASE_DIR}"
    mpiexec -n "${N}" pyfr run -b cuda "${MESH}" "${INI}"
done