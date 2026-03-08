import os
import subprocess
import sys

import numpy as np
import egobox as egx
from mpi4py import MPI

from .genmesh import genmesh

SCRATCH_DIR = "/scratch/users/k24108571/"
HOME_DIR = "/users/k24108571/"
WORKING_DIR = os.path.join(SCRATCH_DIR, "mindrag")
MINDRAG_DIR = os.path.join(HOME_DIR, "pyfr", "cases", "mindrag")
GENMESH_PATH = os.path.join(MINDRAG_DIR, "genmesh.py")

class SimulationManager:
    def __init__(self, dofs, id: int):
        self.id = id
        self.dofs = dofs
        self.comm = MPI.COMM_WORLD
        self.ranks = self.comm.Get_ranks()
        self.meshfile = None
        self.inifile = None

        self.rundir = os.path.join(WORKING_DIR, f"mindrag-run-{self.id}")

    def compute_drag(self) -> float:
        """Computes the drag of a single simulation"""

    def setup_directory(self):
        if os.path.exists(self.rundir):
            sys.stderr.write(f"directory {self.rundir} already exists")
            sys.exit(1)

        os.mkdir(self.rundir)
        os.mkdir(os.path.join(self.rundir, "out"))

    @property
    def ndofs(self) -> int:
        return len(self.dofs)

    def _genmesh(self):
        dofs_string = ",".join(map(str, self.dofs))
        subprocess.run(
            [
                "python", GENMESH_PATH, dofs_string, 
                f"--points={4 if self.ndofs == 3 else 5}", 
                f"--filename=mesh-{self.id}.msh", 
                "--write-out", 
                "--fineness=medium"
            ]
        )

    def _pyfr_import_mesh():
        pass

    def _pyfr_partition_mesh():
        pass

    def _pyfr_run():
        pass


def main():
    pass
    

if __name__ == "__main__":
    main()