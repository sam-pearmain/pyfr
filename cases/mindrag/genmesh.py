import argparse
import math
import random

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
        "--points",
        type=int,
        choices=[4, 5],
        default=5,
        help="the number of bezier curve control points",
    )
    parser.add_argument(
        "--order", type=int, choices=[1, 2], default=1, help="the mesh element order"
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
        default=3,
        help="the geometric fineness ratio (length / base diameter)",
    )
    parser.add_argument(
        "--filename", 
        type=str, 
        help="the mesh filename"
    )

    args = parser.parse_args()
    radius = _compute_base_radius(parser, args.fineness, LENGTH)

    if args.random:
        if args.points == 4:
            dofs = [
                random.uniform(0.01, radius * 0.2),
                random.uniform(0.1, LENGTH * 0.9),
                random.uniform(0.05, radius - 0.02),
            ]
        else:
            dofs = [
                random.uniform(0.005, radius * 0.2),
                random.uniform(0.1, LENGTH * 0.4),
                random.uniform(0.05, radius - 0.02),
                random.uniform(LENGTH * 0.5, LENGTH * 0.9),
                random.uniform(0.1, radius * 0.9),
            ]
    else:
        if not args.dofs:
            parser.error("dofs argument is required unless --random flag is given")

        dofs_string_list = args.dofs.split(",")
        dofs = [float(dof) for dof in dofs_string_list]

        if len(dofs) not in [3, 5]:
            parser.error(
                "must provide either 3 dofs for a 4-point curve or 5 dofs for a 5-point curve"
            )

        if args.points and args.points != (len(dofs) + 5) / 2:
            parser.error(
                "number of provided dofs does not match the number of specified control points"
            )
        else:
            args.points = 4 if len(dofs) == 3 else 5

    genmesh(
        dofs,
        radius,
        points=args.points,
        no_revolve=args.no_revolve,
        order=args.order,
        mesh_refinement=args.mesh_refinement,
        write_to_disk=True if args.write_out else False,
        filename=args.filename if args.filename else None, 
        gui=True if args.gui else False,
    )


def genmesh(
    dofs: list[float],
    radius: float,
    points: int = 4,
    no_revolve: bool = False,
    order: int = 1,
    mesh_refinement: str = "coarse",
    write_to_disk: bool = False,
    filename: str | None = None, 
    gui: bool = False,
):
    dof_str = "_".join([f"{d:.1f}" for d in dofs])
    meshname = f"body_{points}pt_{mesh_refinement}_{dof_str}"

    gmsh.initialize()
    gmsh.model.add(meshname)
    geom = gmsh.model.geo
    model = gmsh.model

    multiplier = {"coarse": 1, "medium": 1.5, "fine": 2}[mesh_refinement]
    progression = 0.1

    p1 = geom.addPoint(0.0, 0.0, 0.0)
    p2 = geom.addPoint(0.0, dofs[0], 0.0)

    if points == 4:
        p3 = geom.addPoint(dofs[1], dofs[2], 0.0)
        p_end = geom.addPoint(LENGTH, radius, 0.0)
        c2 = geom.addBezier([p1, p2, p3, p_end])
    else:
        p3 = geom.addPoint(dofs[1], dofs[2], 0.0)
        p4 = geom.addPoint(dofs[3], dofs[4], 0.0)
        p_end = geom.addPoint(LENGTH, radius, 0.0)
        c2 = geom.addBezier([p1, p2, p3, p4, p_end])

    p6 = geom.addPoint(UPSTREAM_OFFSET, 0.0, 0.0)
    p7 = geom.addPoint(UPSTREAM_OFFSET, radius, 0.0)
    p8 = geom.addPoint(LENGTH - 0.2, FARFIELD_RADIUS, 0.0)

    c1 = geom.addLine(p6, p1)
    c3 = geom.addLine(p_end, p8)
    c4 = geom.addBezier([p8, p7, p6])

    cl1 = geom.addCurveLoop([c1, c2, c3, c4])
    s1 = geom.addPlaneSurface([cl1])

    geom.mesh.setTransfiniteCurve(
        c1, int(20 * multiplier + 1), "progression".capitalize(), 1 - progression
    )
    geom.mesh.setTransfiniteCurve(
        c3, int(20 * multiplier + 1), "progression".capitalize(), 1 + progression
    )
    geom.mesh.setTransfiniteCurve(
        c2, int(80 * multiplier + 1), "progression".capitalize(), 1.02
    )
    geom.mesh.setTransfiniteCurve(c4, int(80 * multiplier + 1))

    geom.mesh.setTransfiniteSurface(s1, "left".capitalize(), [p6, p1, p_end, p8])
    geom.mesh.setRecombine(2, s1)

    geom.synchronize()

    if order > 1:
        model.mesh.setOrder(order)

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
                numElements=[int(12 * multiplier)],
                recombine=True,
            )
            vols.append(ext[1][1])
            walls.append(ext[2][1])
            outflows.append(ext[3][1])
            farfields.append(ext[4][1])

            face = [ext[0]]

        geom.synchronize()
        model.mesh.removeDuplicateNodes()

        model.addPhysicalGroup(3, vols,      1)
        model.addPhysicalGroup(2, walls,     2)
        model.addPhysicalGroup(2, outflows,  3)
        model.addPhysicalGroup(2, farfields, 4)
        model.setPhysicalName(3, 1, "fluid")
        model.setPhysicalName(2, 2, "wall")
        model.setPhysicalName(2, 3, "outflow")
        model.setPhysicalName(2, 4, "farfield")

    model.mesh.generate(2 if no_revolve else 3)

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
