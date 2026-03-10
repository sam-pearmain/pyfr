#!/bin/bash
#SBATCH --job-name=tgv-128-part
#SBATCH --partition=interruptible_gpu
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=24:00:00
#SBATCH --output=tgv-128-part-%j.log
#SBATCH --error=tgv-128-part-%j.err
#SBATCH --constraint=a100

MESH_DIR="$HOME/pyfr/cases/tgv"
SCRATCH_DIR="/scratch/users/k24108571"
ORDER=3
MESH=128
DT="1.25e-3"

CASE_DIR="tgv-results/entropy-filter/order${ORDER}-elems${MESH}"
RESULTS_DIR="${SCRATCH_DIR}/${CASE_DIR}"
INI_FILE="tgv-ord${ORDER}-elems${MESH}.ini"

rm -rf "${RESULTS_DIR}"
mkdir -p "${RESULTS_DIR}/out"

source $HOME/pyfr/.venv/bin/activate
source $HOME/pyfr/initenv.sh

cd "${RESULTS_DIR}"

cat << EOF > "${INI_FILE}"
[backend]
precision = double
rank-allocator = linear

[backend-cuda]
device-id = local-rank

[constants]
gamma = 1.4
mu = 6.25e-4
Pr = 0.71
cpTref = 1.6
cpTs = 0.6466776496430534
p_0 = 0.45714285714285713

[solver]
system = navier-stokes
order = ${ORDER}
viscosity-correction = sutherland
shock-capturing = entropy-filter

[solver-time-integrator]
scheme = rk4
controller = none
tstart = 0
tend = 20
dt = ${DT}

[solver-entropy-filter]
d-min = 1e-6
p-min = 1e-6
e-tol = 1e-6
e-func = physical
niters = 2

[solver-interfaces]
riemann-solver = hllc
ldg-beta = 0.5
ldg-tau = 0.1

[solver-interfaces-quad]
flux-pts = gauss-legendre

[solver-elements-hex]
soln-pts = gauss-legendre

[soln-ics]
rho = 1 + (1.0 / (16.0 * p_0)) * (cos(2 * x) + cos(2 * y))*(cos(2 * z) + 2)
u = sin(x) * cos(y) * cos(z)
v = -cos(x) * sin(y) * cos(z)
w = 0
p = p_0 + (1.0 / 16.0) * (cos(2 * x) + cos(2 * y))*(cos(2 * z) + 2)

[soln-plugin-integrate]
nsteps = 100
file = integral.csv
header = true
invvol = 1.0 / pow((2.0 * pi), 3)
Tratio = (p / (rho * 0.45714285714285713))
muratio = ((1.4042 * pow(%(Tratio)s, 1.5)) / (%(Tratio)s + 0.4042))
vor1 = (grad_w_y - grad_v_z)
vor2 = (grad_u_z - grad_w_x)
vor3 = (grad_v_x - grad_u_y)
divU = (grad_u_x + grad_v_y + grad_w_z)

int-Ek = %(invvol)s*0.5*rho*(u*u + v*v + w*w)
int-eps_s = %(invvol)s*(1.0/1600.0)*%(muratio)s*(%(vor1)s*%(vor1)s + %(vor2)s*%(vor2)s + %(vor3)s*%(vor3)s)
int-eps_d = %(invvol)s*(4.0/4800.0)*%(muratio)s*(%(divU)s*%(divU)s)

[soln-plugin-writer]
dt-out = 1
basedir = out/
basename = tgv-{t:.2f}

[soln-plugin-nancheck]
nsteps = 1000
EOF

MESH_FILE="${MESH_DIR}/${MESH}-elems-tgv-mesh.pyfrm"

pyfr partition -p scotch 2 "${MESH_FILE}" .

mpiexec -n 2 pyfr run -b cuda "${MESH_FILE}" "${INI_FILE}"