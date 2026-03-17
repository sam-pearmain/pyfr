import argparse
import os
import shutil
import subprocess

import egobox as egx
import numpy as np
import pandas as pd

os.environ["EGOR_USE_RUN_RECORDER"] = "WITH_ITER_STATE"


class EnvConfig:
    def __init__(self, env_type: str, n_gpus: int = 1):
        self.n_gpus = n_gpus
        
        if env_type == "hpc":
            self.scratch_dir = "/scratch/users/k24108571/"
            self.home_dir = "/users/k24108571/"
            self.working_dir = os.path.join(self.scratch_dir, "mindrag-optimisation")
            self.default_shape = "bezier_4"
        else:
            self.home_dir = os.path.expanduser("~")
            self.working_dir = os.path.join(
                self.home_dir, "pyfr", "cases", "mindrag", "mindrag-optimisation"
            )
            self.default_shape = "powerlaw"

        self.mindrag_dir = os.path.join(self.home_dir, "pyfr", "cases", "mindrag")
        self.genmesh_path = os.path.join(self.mindrag_dir, "genmesh.py")
        self.ini_template_file = os.path.join(self.mindrag_dir, "euler.ini")


CONFIG = EnvConfig("local")


class SimulationManager:
    id: int = 1

    def __init__(self, dofs: list[float]):
        self.dofs = dofs
        self.rundir = os.path.join(
            CONFIG.working_dir, f"mindrag-run-{SimulationManager.id}"
        )
        self.meshfile = f"mesh-{SimulationManager.id}.msh"
        SimulationManager._increment_simulation_id()

    def compute_drag(self) -> float:
        try:
            self._setup_directory()
            self._genmesh()
            self._pyfr_import_mesh()
            self._pyfr_partition_mesh()
            self._pyfr_run()
            return self._extract_drag()
        except subprocess.CalledProcessError:
            return np.nan
        except FileNotFoundError:
            return np.nan

    def _setup_directory(self):
        if os.path.exists(self.rundir):
            shutil.rmtree(self.rundir)

        os.makedirs(self.rundir)
        os.makedirs(os.path.join(self.rundir, "out"))
        shutil.copy(CONFIG.ini_template_file, os.path.join(self.rundir, "case.ini"))

    @property
    def ndofs(self) -> int:
        return len(self.dofs)

    @property
    def dofs_string(self) -> str:
        return ",".join(map(str, self.dofs))

    def _genmesh(self):
        if self.ndofs == 1:
            curve_type = "powerlaw"
        elif self.ndofs == 3:
            curve_type = "bezier_4"
        else:
            curve_type = "bezier_5"

        subprocess.run(
            [
                "python",
                CONFIG.genmesh_path,
                self.dofs_string,
                f"--curve-type={curve_type}",
                f"--filename={self.meshfile}",
                "--write-out",
                "--mesh-refinement=coarse",
            ],
            cwd=self.rundir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.run(["clear"])

    def _pyfr_import_mesh(self):
        subprocess.run(
            ["pyfr", "import", self.meshfile, "mesh.pyfrm"], cwd=self.rundir, check=True
        )

    def _pyfr_partition_mesh(self):
        if CONFIG.n_gpus > 1:
            subprocess.run(
                ["pyfr", "partition", str(CONFIG.n_gpus), "mesh.pyfrm", "."],
                cwd=self.rundir,
                check=True
            )

    def _pyfr_run(self):
        cmd = [
            "pyfr",
            "-p",
            "run",
            "-b",
            "cuda",
            "mesh.pyfrm",
            "case.ini",
        ]
        
        if CONFIG.n_gpus > 1:
            cmd = ["mpiexec", "-n", str(CONFIG.n_gpus)] + cmd

        subprocess.run(
            cmd,
            cwd=self.rundir,
            check=True,
        )

    def _extract_drag(self) -> float:
        force_file = os.path.join(self.rundir, "force.csv")
        if not os.path.exists(force_file):
            return np.nan

        try:
            data = pd.read_csv(force_file)
            initial_px = data["px"].iloc[0]
            data["px_gauge"] = data["px"] - initial_px

            length = 1.0
            fineness_ratio = 3.0
            diameter = length / fineness_ratio
            area_ref = np.pi * (diameter**2) / 4.0

            data_avg = data[(data["t"] >= 1.0) & (data["t"] <= 2.0)]

            if data_avg.empty:
                return np.nan

            cd_avg = data_avg["px_gauge"] / (0.5 * area_ref)
            return float(cd_avg.mean())
        except Exception:
            return np.nan

    @classmethod
    def _increment_simulation_id(cls):
        cls.id += 1


def evaluate_hypersonic_drag(x):
    x = np.atleast_2d(x)
    results = []

    for xi in x:
        sim = SimulationManager(xi.tolist())
        drag = sim.compute_drag()
        results.append(drag)

    return np.array(results).reshape(-1, 1)


def main():
    parser = argparse.ArgumentParser(description="Hypersonic Drag Optimisation")
    parser.add_argument(
        "--env",
        choices=["local", "hpc"],
        default="local",
    )
    parser.add_argument(
        "--shape",
        choices=["powerlaw", "bezier_4"],
        default=None,
    )
    parser.add_argument(
        "--gpus",
        type=int,
        default=1,
    )
    args = parser.parse_args()

    global CONFIG
    CONFIG = EnvConfig(args.env, args.gpus)

    shape = args.shape if args.shape else CONFIG.default_shape

    if not os.path.exists(CONFIG.working_dir):
        os.makedirs(CONFIG.working_dir)

    length = 1.0
    fineness = 3.0
    radius = length / (2 * fineness)

    if shape == "powerlaw":
        bounds = [[0.1, 0.9]]
        n_doe = 5
    else:
        bounds = [[0.01, radius * 0.2], [0.2, length * 0.8], [0.05, radius - 0.02]]
        n_doe = 15

    initial_doe = egx.lhs(bounds, n_doe, seed=42)
    print(initial_doe)

    egor = egx.Egor(
        bounds,
        doe=initial_doe,
        trego=True,
        failsafe_strategy=egx.FailsafeStrategy.IMPUTATION,
        outdir=CONFIG.working_dir,
        seed=42,
    )

    res = egor.minimize(evaluate_hypersonic_drag, max_iters=25)

    print(f"optimisation complete. minimum drag: {res.y_opt[0]}")
    print(f"optimal parameters: {res.x_opt}")


if __name__ == "__main__":
    main()