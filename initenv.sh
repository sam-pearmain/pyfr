#! /bin/bash

module purge
module load gcc
module load cuda
module load openmpi
module load scotch

export LD_LIBRARY_PATH=/software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/mesa-glu-9.0.2-6wl4qetg3vmc2g36w73psgkadicbg7xf/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$(dirname $(dirname $(which nvcc)))/lib64:$LD_LIBRARY_PATH
export UCX_LOG_LEVEL=error
export PYTHONPATH=""
export LD_LIBRARY_PATH=$(ls -d /software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/scotch-7.0.4*/lib | head -n 1):$LD_LIBRARY_PATH

SCOTCH_LIB_DIR=$(ls -d /software/spackages_v0_21_prod/apps/linux-ubuntu22.04-zen2/gcc-13.2.0/scotch-7.0.4*/lib | head -n 1)
export LD_PRELOAD=$SCOTCH_LIB_DIR/libscotcherr.so