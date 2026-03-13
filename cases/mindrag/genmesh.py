import argparse
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
        num_spline_points = 200
        curve_points = []
        
        for i in range(num_spline_points + 1):
            theta = (i / num_spline_points) * (math.pi / 2.0)
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

    geom.mesh.setTransfiniteCurve(c1, 31, "Progression", 1 - 0.04)
    geom.mesh.setTransfiniteCurve(c3, 31, "Progression", 1 + 0.04)
    geom.mesh.setTransfiniteCurve(c2, 81, "Progression", 1)
    geom.mesh.setTransfiniteCurve(c4, 81, "Progression", 1)

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
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                math.pi / 2,
                numElements=[12],
                recombine=True,
            )
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

    if mesh_refinement == "medium":
        model.mesh.refine()
    elif mesh_refinement == "fine":
        model.mesh.refine()
        model.mesh.refine()

    if order > 1:
        model.mesh.setOrder(order)

    model.mesh.optimize("HighOrder", niter=30)

    if write_to_disk:
        if filename:
            gmsh.write(f"{filename}")
        else:
            gmsh.write(f"{meshname}.msh")

    if gui:
        gmsh.fltk.run()

    gmsh.finalize()


def _compute_base_radius(
    parser: argparse.ArgumentParser, fineness_ratio: float, length: float = LENGTH
) -> float:
    if fineness_ratio < 2:
        parser.error("fineness ratio cannot be less that 2")

    return length / (2 * fineness_ratio)


if __name__ == "__main__":
    main()