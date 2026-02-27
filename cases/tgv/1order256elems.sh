#!/bin/bash
#SBATCH --job-name=tgv-1order265elem
#SBATCH --partition=interruptible_gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --gres=gpu:8
#SBATCH --time=24:00:00
#SBATCH --output=tgv-1order265elem-%j.log
#SBATCH --error=tgv-1order265elem-%j.err
#SBATCH --constraint=l40s

cd $HOME/pyfr

source .venv/bin/activate
source initenv.sh

MESHFILE="$HOME/pyfr/cases/tgv/256-elems-tgv-mesh.pyfrm"
PARTITIONED_MESHFILE=$HOME/pyfr/cases/tgv/256-elems-tgv-mesh-partitioned.pyfrm"
INIFILE="/scratch/users/k24108571/tgv-results/entropy-filter/order1-elems256/tgv-order1-elems256.ini"

cp ${MESHFILE} ${PARTITIONED_MESHFILE}

pyfr partition 8 -p scotch ${PARTITIONED_MESHFILE} 

mpiexec -n 8 pyfr run -b cuda ${PARTITIONED_MESHFILE} ${INIFILE}