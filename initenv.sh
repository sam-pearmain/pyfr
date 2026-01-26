#! /bin/bash

module purge
module load gcc
module load cuda
module load openmpi

export LD_LIBRARY_PATH=/software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/mesa-glu-9.0.2-6wl4qetg3vmc2g36w73psgkadicbg7xf/lib:$LD_LIBRARY_PATH
export UCX_LOG_LEVEL=error
export PYTHONPATH=""