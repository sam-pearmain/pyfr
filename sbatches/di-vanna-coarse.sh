#!/bin/bash
#SBATCH --job-name=pyfr-inlet
#SBATCH --partition=interruptible_gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --output=pyfr-inlet-%j.log
#SBATCH --error=pyfr-inlet-%j.err
#SBATCH --constraint=h100

source ~/pyfr/.venv/bin/activate
source ~/pyfr/initenv.sh

cd /scratch/users/k24108571/di-vanna/coarse

pyfr import coarse.msh mesh.pyfrm
mpiexec -n 1 pyfr run -b cuda mesh.pyfrm coarse.ini