import argparse
import csv
import math
import random
import warnings

import gmsh

LENGTH = 1.0
FARFIELD_RADIUS = 0.4
UPSTREAM_OFFSET = -0.1


def main():
    parser = argparse.ArgumentParser(
        prog="genmesh",
        description="a programme for automated generation of hypersonic blunt bodies of revolution",
    )

    parser.add_argument(
        "dofs",
        nargs="?",
        default="",
        help="the degrees of freedom at each control point",
    )
    parser.add_argument(
        "--curve-type",
        choices=["bezier_4", "bezier_5", "powerlaw"],
        default="bezier_4",
        help="the type of contour parameterisation to use",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="whether to generate random values for control point dofs",
    )
    parser.add_argument(
        "--no-revolve",
        action="store_true",
        help="whether to revolve the mesh around its central axis",
    )
    parser.add_argument(
        "--write-out",
        action="store_true",
        help="writes the mesh to disk, the filename can be specified if required",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="whether to display the gui after mesh generation",
    )
    parser.add_argument(
        "--mesh-order",
        type=int,
        choices=[1, 2],
        default=2,
        help="the mesh element order",
    )
    parser.add_argument(
        "--mesh-refinement",
        choices=["coarse", "medium", "fine"],
        default="coarse",
        help="the level of mesh refinement",
    )
    parser.add_argument(
        "--fineness",
        type=float,
        default=3.0,
        help="the geometric fineness ratio (length / base diameter)",
    )
    parser.add_argument("--filename", type=str, help="the mesh filename")

    args = parser.parse_args()
    radius = _compute_base_radius(parser, args.fineness, LENGTH)

    if args.random and args.dofs:
        warnings.warn("dofs provided but --random flag also set, please check")

    if not args.dofs:
        if not args.random:
            parser.error(
                "no degrees of freedom specified, pass --random to automatically generate dofs"
            )

        if args.curve_type == "powerlaw":
            dofs = [random.uniform(0.65, 0.75)]
        elif args.curve_type == "bezier_4":
            dofs = [
                random.uniform(0.01, radius * 0.2),
                random.uniform(0.1, LENGTH * 0.9),
                random.uniform(0.05, radius - 0.02),
            ]
        elif args.curve_type == "bezier_5":
            dofs = [
                random.uniform(0.005, radius * 0.2),
                random.uniform(0.1, LENGTH * 0.4),
                random.uniform(0.05, radius - 0.02),
                random.uniform(LENGTH * 0.5, LENGTH * 0.9),
                random.uniform(0.1, radius * 0.9),
            ]
    else:
        dofs_string_list = args.dofs.split(",")
        dofs = [float(dof) for dof in dofs_string_list]

        n_expected_dofs = {
            "powerlaw": 1,
            "bezier_4": 3,
            "bezier_5": 5,
        }[args.curve_type]

        if len(dofs) != n_expected_dofs:
            parser.error(
                f"number of provided dofs {len(dofs)} does not equal the expected number of dofs for {args.curve_type}: {n_expected_dofs}"
            )

    genmesh(
        dofs,
        radius,
        curve_type=args.curve_type,
        no_revolve=args.no_revolve,
        order=args.mesh_order,
        mesh_refinement=args.mesh_refinement,
        write_to_disk=True if args.write_out else False,
        filename=args.filename if args.filename else None,
        gui=True if args.gui else False,
    )


def genmesh(
    dofs: list[float],
    radius: float,
    curve_type: str = "bezier_4",
    no_revolve: bool = False,
    order: int = 1,
    mesh_refinement: str = "coarse",
    write_to_disk: bool = False,
    filename: str | None = None,
    gui: bool = False,
):
    dof_str = "_".join([f"{d:.3f}" for d in dofs])
    meshname = f"body_{curve_type}_{mesh_refinement}_{dof_str}"

    gmsh.initialize()
    gmsh.model.add(meshname)
    geom = gmsh.model.geo
    model = gmsh.model

    multiplier = {"coarse": 1, "medium": 2, "fine": 4}[mesh_refinement]
    base = 1.06
    progression = math.pow(base, 1.0 / multiplier)
    inv_progression = math.pow(1.0 / base, 1.0 / multiplier)
    n_spline_points = 200

    if curve_type.startswith("bezier"):
        p1 = geom.addPoint(0.0, 0.0, 0.0)
        p2 = geom.addPoint(0.0, dofs[0], 0.0)

        if curve_type == "bezier_4":
            p3 = geom.addPoint(dofs[1], dofs[2], 0.0)
            p_end = geom.addPoint(LENGTH, radius, 0.0)
            c2 = geom.addBezier([p1, p2, p3, p_end])
        elif curve_type == "bezier_5":
            p3 = geom.addPoint(dofs[1], dofs[2], 0.0)
            p4 = geom.addPoint(dofs[3], dofs[4], 0.0)
            p_end = geom.addPoint(LENGTH, radius, 0.0)
            c2 = geom.addBezier([p1, p2, p3, p4, p_end])
    else:
        exponent = dofs[0]
        curve_points = []

        for i in range(n_spline_points + 1):
            theta = (i / n_spline_points) * (math.pi / 2.0)
            x_val = LENGTH * (1.0 - math.cos(theta))

            if x_val == 0.0:
                y_val = 0.0
            else:
                y_val = radius * math.pow((x_val / LENGTH), exponent)

            pt = geom.addPoint(x_val, y_val, 0.0)
            curve_points.append(pt)

        c2 = geom.addSpline(curve_points)
        p1 = curve_points[0]
        p_end = curve_points[-1]

    p6 = geom.addPoint(UPSTREAM_OFFSET, 0.0, 0.0)
    p7 = geom.addPoint(UPSTREAM_OFFSET, radius, 0.0)
    p8 = geom.addPoint(LENGTH - 0.2, FARFIELD_RADIUS, 0.0)

    c1 = geom.addLine(p6, p1)
    c3 = geom.addLine(p_end, p8)
    c4 = geom.addBezier([p8, p7, p6])

    cl1 = geom.addCurveLoop([c1, c2, c3, c4])
    s1 = geom.addPlaneSurface([cl1])

    geom.mesh.setTransfiniteCurve(c1, 20 * multiplier + 1, "Progression", inv_progression)
    geom.mesh.setTransfiniteCurve(c3, 20 * multiplier + 1, "Progression", progression)
    geom.mesh.setTransfiniteCurve(c2, 40 * multiplier + 1, "Progression", 1)
    geom.mesh.setTransfiniteCurve(c4, 40 * multiplier + 1, "Progression", 1)

    geom.mesh.setTransfiniteSurface(s1, "Left", [p6, p1, p_end, p8])
    geom.mesh.setRecombine(2, s1)

    geom.synchronize()

    if no_revolve:
        model.addPhysicalGroup(2, [s1], 1)
        model.addPhysicalGroup(1, [c1], 2)
        model.addPhysicalGroup(1, [c2], 3)
        model.addPhysicalGroup(1, [c3], 4)
        model.addPhysicalGroup(1, [c4], 5)
        model.setPhysicalName(2, 1, "fluid")
        model.setPhysicalName(1, 2, "axissym")
        model.setPhysicalName(1, 3, "wall")
        model.setPhysicalName(1, 4, "outflow")
        model.setPhysicalName(1, 5, "farfield")
    else:
        face = [(2, s1)]
        vols, walls, outflows, farfields = [], [], [], []

        for i in range(4):
            ext = geom.revolve(
                face,
                0.0, 0.0, 0.0,
                1.0, 0.0, 0.0,
                math.pi / 2,
                numElements=[8 * multiplier],
                recombine=True,
            )  # fmt: skip
            vols.append(ext[1][1])
            walls.append(ext[2][1])
            outflows.append(ext[3][1])
            farfields.append(ext[4][1])

            face = [ext[0]]

        geom.synchronize()
        model.mesh.removeDuplicateNodes()

        model.addPhysicalGroup(3, vols, 1)
        model.addPhysicalGroup(2, walls, 2)
        model.addPhysicalGroup(2, outflows, 3)
        model.addPhysicalGroup(2, farfields, 4)
        model.setPhysicalName(3, 1, "fluid")
        model.setPhysicalName(2, 2, "wall")
        model.setPhysicalName(2, 3, "outflow")
        model.setPhysicalName(2, 4, "farfield")

    model.mesh.generate(2 if no_revolve else 3)

    if order > 1:
        model.mesh.setOrder(order)
        gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
        gmsh.option.setNumber("Mesh.HighOrderNumLayers", 12)
        gmsh.option.setNumber("Mesh.HighOrderPassMax", 50)
        gmsh.option.setNumber("Mesh.HighOrderThresholdMin", 0.01)
        gmsh.option.setNumber("Mesh.HighOrderThresholdMax", 2.0)
        model.mesh.optimize("HighOrder", niter=50)

    if write_to_disk:
        if curve_type == "powerlaw":
            _write_powerlaw_points(dofs, n_spline_points, radius)
        elif curve_type == "bezier_4":
            _write_bezier_4_points(dofs, n_spline_points, radius)
        else:
            _write_bezier_5_points(dofs, n_spline_points, radius)

        if filename:
            gmsh.write(f"{filename}")
        else:
            gmsh.write(f"{meshname}.msh")

    if gui:
        gmsh.fltk.run()

    gmsh.finalize()


def _write_powerlaw_points(dofs, n_points, radius):
    points = []
    epsilon = 1e-5
    filename = "powerlaw-points.csv"

    for i in range(n_points):
        x_val = (i / (n_points - 1)) * LENGTH
        if x_val == 0.0:
            y_val = epsilon
        else:
            y_val = radius * math.pow((x_val / LENGTH), dofs[0]) + epsilon
        points.append((x_val, y_val, 0.0))

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(points)


def _write_bezier_4_points(dofs, n_points, radius):
    points = []
    epsilon = 1e-5
    filename = "bezier-points.csv"

    p0_x, p0_y = 0.0, 0.0
    p1_x, p1_y = 0.0, dofs[0]
    p2_x, p2_y = dofs[1], dofs[2]
    p3_x, p3_y = LENGTH, radius

    for i in range(n_points):
        t = i / (n_points - 1)
        u = 1.0 - t

        x_val = u**3 * p0_x + 3 * u**2 * t * p1_x + 3 * u * t**2 * p2_x + t**3 * p3_x

        y_val = (
            u**3 * p0_y + 3 * u**2 * t * p1_y + 3 * u * t**2 * p2_y + t**3 * p3_y
        ) + epsilon

        points.append((x_val, y_val, 0.0))

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(points)


def _write_bezier_5_points(dofs, n_points, radius):
    points = []
    epsilon = 1e-5
    filename = "bezier-points.csv"

    p0_x, p0_y = 0.0, 0.0
    p1_x, p1_y = 0.0, dofs[0]
    p2_x, p2_y = dofs[1], dofs[2]
    p3_x, p3_y = dofs[3], dofs[4]
    p4_x, p4_y = LENGTH, radius

    for i in range(n_points):
        t = i / (n_points - 1)
        u = 1.0 - t

        x_val = (
            u**4 * p0_x
            + 4 * u**3 * t * p1_x
            + 6 * u**2 * t**2 * p2_x
            + 4 * u * t**3 * p3_x
            + t**4 * p4_x
        )

        y_val = (
            u**4 * p0_y
            + 4 * u**3 * t * p1_y
            + 6 * u**2 * t**2 * p2_y
            + 4 * u * t**3 * p3_y
            + t**4 * p4_y
        ) + epsilon

        points.append((x_val, y_val, 0.0))

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(points)


def _compute_base_radius(
    parser: argparse.ArgumentParser, fineness_ratio: float, length: float = LENGTH
) -> float:
    if fineness_ratio < 2:
        parser.error("fineness ratio cannot be less that 2")

    return length / (2 * fineness_ratio)


if __name__ == "__main__":
    main()
