#!/bin/bash
#SBATCH --job-name=tgv-3order128elems-artvisc
#SBATCH --partition=interruptible_gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --gres=gpu:8
#SBATCH --time=24:00:00
#SBATCH --output=tgv-3order128elems-artvisc-%j.log
#SBATCH --error=tgv-3order128elems-artvisc-%j.err
#SBATCH --constraint=l40s

source $HOME/pyfr/.venv/bin/activate
source $HOME/pyfr/initenv.sh

MESHFILE="$HOME/pyfr/cases/tgv/128-elems-tgv-mesh.pyfrm"
SCRATCH_DIR="/scratch/users/k24108571/tgv-results/artificial-viscosity/order3-elems128"
PARTITIONED_MESHFILE="${SCRATCH_DIR}/128-elems-tgv-mesh-partitioned.pyfrm"
INIFILE="${SCRATCH_DIR}/tgv-ord3-elems128.ini"

cd "${SCRATCH_DIR}"

if [ ! -f "${PARTITIONED_MESHFILE}" ]; then 
    echo "partitioning mesh file"
    cp "${MESHFILE}" "${PARTITIONED_MESHFILE}"
    pyfr partition -p scotch 8 "${PARTITIONED_MESHFILE}" .
fi 

echo "launching pyfr"
mpiexec -n 8 pyfr run -b cuda "${PARTITIONED_MESHFILE}" "${INIFILE}"

echo "hello kitty"
echo "hello kitty"
echo "hello kitty"
echo "hello kitty"
echo "hello kitty"