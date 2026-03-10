import argparse
from math import radians, tan

import gmsh

geom = gmsh.model.geo
mesh = gmsh.model.mesh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mesh-refinement",
        type=str,
        choices=["coarse", "medium", "fine"],
        default="coarse",
    )
    parser.add_argument("--filename", type=str, default=None)
    parser.add_argument("--gui", type=bool, default=False)

    args = parser.parse_args()

    multipliers = {"coarse": 1, "medium": 2, "fine": 4}
    multiplier = multipliers[args.mesh_refinement]

    if not args.filename:
        filename = f"{args.mesh_refinement}.msh"
    else:
        filename = args.filename

    genmesh(multiplier, filename, args.gui)


def genmesh(multiplier: int, filename: str | None, gui: bool = False):
    gmsh.initialize()
    gmsh.model.add("inlet-structured-3d-coarse")

    l0 = 150.0
    scale_factor = 1.0 / l0

    domain_length = 1.05
    domain_height = 0.40

    intake_length = 150.0 * scale_factor
    intake_height = 44.0 * scale_factor
    throat_height = 15.0 * scale_factor
    ramp_length = 81.7 * scale_factor
    ramp_height = 21.0 * scale_factor

    ramp_angle_one = 10.0
    ramp_angle_two = 22.0
    cowl_angle = 30.0

    kink_length = (ramp_height - tan(radians(ramp_angle_two)) * ramp_length) / (
        tan(radians(ramp_angle_one)) - tan(radians(ramp_angle_two))
    )
    kink_height = tan(radians(ramp_angle_one)) * kink_length

    y_split_bot = ramp_height + throat_height
    blunt_height = 1.0 * scale_factor
    y_split_top = y_split_bot + blunt_height

    x_start = 0.0
    x_ramp_start = domain_length - intake_length
    x_kink = x_ramp_start + kink_length
    x_throat_start = x_ramp_start + ramp_length

    x_cowl_tip = x_throat_start + (
        (intake_height - y_split_top) / tan(radians(cowl_angle))
    )
    x_end = domain_length
    z_extrude = 0.1

    paper_nx_total = 256
    dx_constant = domain_length / paper_nx_total

    nx_1 = int(round((x_ramp_start - x_start) / dx_constant))
    nx_2 = int(round((x_kink - x_ramp_start) / dx_constant))
    nx_3 = int(round((x_throat_start - x_kink) / dx_constant))
    nx_cowl = int(round((x_cowl_tip - x_throat_start) / dx_constant))
    nx_wake = int(round((x_end - x_cowl_tip) / dx_constant))
    nx_throat = nx_cowl + nx_wake - 1

    ny_bottom = 45 * multiplier
    ny_mid = 4 * multiplier
    ny_top = 30 * multiplier
    nz_total = 20 * multiplier

    p1 = geom.addPoint(x_start, 0, 0)
    p2 = geom.addPoint(x_ramp_start, 0, 0)
    p3 = geom.addPoint(x_kink, kink_height, 0)
    p4 = geom.addPoint(x_throat_start, ramp_height, 0)
    p5 = geom.addPoint(x_end, ramp_height, 0)

    p6 = geom.addPoint(x_start, y_split_bot, 0)
    p7 = geom.addPoint(x_ramp_start, y_split_bot, 0)
    p8 = geom.addPoint(x_kink, y_split_bot, 0)
    p9 = geom.addPoint(x_throat_start, y_split_bot, 0)
    p10 = geom.addPoint(x_end, y_split_bot, 0)

    p11 = geom.addPoint(x_start, y_split_top, 0)
    p12 = geom.addPoint(x_ramp_start, y_split_top, 0)
    p13 = geom.addPoint(x_kink, y_split_top, 0)
    p14 = geom.addPoint(x_throat_start, y_split_top, 0)
    p15 = geom.addPoint(x_cowl_tip, intake_height, 0)

    p16 = geom.addPoint(x_start, domain_height, 0)
    p17 = geom.addPoint(x_ramp_start, domain_height, 0)
    p18 = geom.addPoint(x_kink, domain_height, 0)
    p19 = geom.addPoint(x_throat_start, domain_height, 0)
    p20 = geom.addPoint(x_cowl_tip, domain_height, 0)

    l1 = geom.addLine(p1, p2)
    l2 = geom.addLine(p2, p3)
    l3 = geom.addLine(p3, p4)
    l4 = geom.addLine(p4, p5)
    l5 = geom.addLine(p6, p7)
    l6 = geom.addLine(p7, p8)
    l7 = geom.addLine(p8, p9)
    l8 = geom.addLine(p9, p10)
    l9 = geom.addLine(p11, p12)
    l10 = geom.addLine(p12, p13)
    l11 = geom.addLine(p13, p14)
    l12 = geom.addLine(p14, p15)
    l13 = geom.addLine(p16, p17)
    l14 = geom.addLine(p17, p18)
    l15 = geom.addLine(p18, p19)
    l16 = geom.addLine(p19, p20)

    l17 = geom.addLine(p1, p6)
    l18 = geom.addLine(p2, p7)
    l19 = geom.addLine(p3, p8)
    l20 = geom.addLine(p4, p9)
    l21 = geom.addLine(p5, p10)
    l22 = geom.addLine(p6, p11)
    l23 = geom.addLine(p7, p12)
    l24 = geom.addLine(p8, p13)
    l25 = geom.addLine(p9, p14)
    l26 = geom.addLine(p11, p16)
    l27 = geom.addLine(p12, p17)
    l28 = geom.addLine(p13, p18)
    l29 = geom.addLine(p14, p19)
    l30 = geom.addLine(p15, p20)

    s1 = geom.addPlaneSurface([geom.addCurveLoop([l1, l18, -l5, -l17])])
    s2 = geom.addPlaneSurface([geom.addCurveLoop([l2, l19, -l6, -l18])])
    s3 = geom.addPlaneSurface([geom.addCurveLoop([l3, l20, -l7, -l19])])
    s4 = geom.addPlaneSurface([geom.addCurveLoop([l4, l21, -l8, -l20])])

    s5 = geom.addPlaneSurface([geom.addCurveLoop([l5, l23, -l9, -l22])])
    s6 = geom.addPlaneSurface([geom.addCurveLoop([l6, l24, -l10, -l23])])
    s7 = geom.addPlaneSurface([geom.addCurveLoop([l7, l25, -l11, -l24])])

    s8 = geom.addPlaneSurface([geom.addCurveLoop([l9, l27, -l13, -l26])])
    s9 = geom.addPlaneSurface([geom.addCurveLoop([l10, l28, -l14, -l27])])
    s10 = geom.addPlaneSurface([geom.addCurveLoop([l11, l29, -l15, -l28])])
    s11 = geom.addPlaneSurface([geom.addCurveLoop([l12, l30, -l16, -l29])])

    all_surfaces = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]

    surfaces_extrude = [(2, s) for s in all_surfaces]
    extruded_entities = geom.extrude(
        surfaces_extrude, 0, 0, z_extrude, numElements=[nz_total], recombine=True
    )

    geom.synchronize()

    for line in [l1, l5, l9, l13]:
        mesh.setTransfiniteCurve(line, nx_1)
    for line in [l2, l6, l10, l14]:
        mesh.setTransfiniteCurve(line, nx_2)
    for line in [l3, l7, l11, l15]:
        mesh.setTransfiniteCurve(line, nx_3)
    for line in [l4, l8]:
        mesh.setTransfiniteCurve(line, nx_throat)
    for line in [l12, l16]:
        mesh.setTransfiniteCurve(line, nx_cowl)

    for line in [l17, l18, l19, l20, l21]:
        mesh.setTransfiniteCurve(line, ny_bottom, "Progression", 1.005)

    for line in [l22, l23, l24, l25]:
        mesh.setTransfiniteCurve(line, ny_mid)

    for line in [l26, l27, l28, l29, l30]:
        mesh.setTransfiniteCurve(line, ny_top, "Progression", 1.01)

    mesh.setTransfiniteSurface(s1, cornerTags=[p1, p2, p7, p6])
    mesh.setTransfiniteSurface(s2, cornerTags=[p2, p3, p8, p7])
    mesh.setTransfiniteSurface(s3, cornerTags=[p3, p4, p9, p8])
    mesh.setTransfiniteSurface(s4, cornerTags=[p4, p5, p10, p9])

    mesh.setTransfiniteSurface(s5, cornerTags=[p6, p7, p12, p11])
    mesh.setTransfiniteSurface(s6, cornerTags=[p7, p8, p13, p12])
    mesh.setTransfiniteSurface(s7, cornerTags=[p8, p9, p14, p13])

    mesh.setTransfiniteSurface(s8, cornerTags=[p11, p12, p17, p16])
    mesh.setTransfiniteSurface(s9, cornerTags=[p12, p13, p18, p17])
    mesh.setTransfiniteSurface(s10, cornerTags=[p13, p14, p19, p18])
    mesh.setTransfiniteSurface(s11, cornerTags=[p14, p15, p20, p19])

    for s in all_surfaces:
        mesh.setRecombine(2, s)

    def get_extruded_surf(line_tag):
        l_bb = gmsh.model.getBoundingBox(1, line_tag)
        for dim, stag in gmsh.model.getEntities(2):
            s_bb = gmsh.model.getBoundingBox(dim, stag)
            if (
                abs(s_bb[0] - l_bb[0]) < 1e-5
                and abs(s_bb[1] - l_bb[1]) < 1e-5
                and abs(s_bb[3] - l_bb[3]) < 1e-5
                and abs(s_bb[4] - l_bb[4]) < 1e-5
                and abs(s_bb[2] - 0.0) < 1e-5
                and abs(s_bb[5] - z_extrude) < 1e-5
            ):
                return stag
        return None

    wall_lines = [l2, l3, l4, l8, l25, l12]
    farfield_lines = [l17, l22, l26, l13, l14, l15, l16]
    outlet_lines = [l21, l30]
    symplane_lines = [l1]

    wall_surfs = [get_extruded_surf(line) for line in wall_lines]
    farfield_surfs = [get_extruded_surf(line) for line in farfield_lines]
    outlet_surfs = [get_extruded_surf(line) for line in outlet_lines]
    symplane_surfs = [get_extruded_surf(line) for line in symplane_lines]

    for dim, stag in gmsh.model.getEntities(2):
        s_bb = gmsh.model.getBoundingBox(dim, stag)
        if abs(s_bb[2] - 0.0) < 1e-5 and abs(s_bb[5] - 0.0) < 1e-5:
            symplane_surfs.append(stag)
        elif abs(s_bb[2] - z_extrude) < 1e-5 and abs(s_bb[5] - z_extrude) < 1e-5:
            symplane_surfs.append(stag)

    wall_group = gmsh.model.addPhysicalGroup(2, wall_surfs)
    gmsh.model.setPhysicalName(2, wall_group, "wall")

    farfield_group = gmsh.model.addPhysicalGroup(2, farfield_surfs)
    gmsh.model.setPhysicalName(2, farfield_group, "farfield")

    outlet_group = gmsh.model.addPhysicalGroup(2, outlet_surfs)
    gmsh.model.setPhysicalName(2, outlet_group, "outlet")

    symplane_group = gmsh.model.addPhysicalGroup(2, symplane_surfs)
    gmsh.model.setPhysicalName(2, symplane_group, "symplane")

    volumes = [ent[1] for ent in extruded_entities if ent[0] == 3]
    fluid = gmsh.model.addPhysicalGroup(3, volumes)
    gmsh.model.setPhysicalName(3, fluid, "fluid")

    gmsh.option.setNumber("Mesh.RecombineAll", 1)
    mesh.generate(3)
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == "__main__":
    main()
