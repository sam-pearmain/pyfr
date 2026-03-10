from math import cos, radians, sin, tan

import gmsh

geom = gmsh.model.geo
mesh = gmsh.model.mesh


def main():
    gmsh.initialize()
    gmsh.model.add("inlet-structured-3d")

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
    y_split = ramp_height + throat_height

    x_start = 0.0
    x_ramp_start = domain_length - intake_length
    x_kink = x_ramp_start + kink_length
    x_throat_start = x_ramp_start + ramp_length

    cowl_sharp_x = x_throat_start + (
        (intake_height - y_split) / tan(radians(cowl_angle))
    )

    r_blunt = 0.5 * scale_factor
    theta = radians(cowl_angle)

    xc = cowl_sharp_x + r_blunt / sin(theta / 2.0)
    yc = intake_height - r_blunt

    x_cowl_bot = xc - r_blunt * sin(theta)
    y_cowl_bot = yc - r_blunt * cos(theta)

    x_cowl_top = xc
    y_cowl_top = yc + r_blunt

    x_end = domain_length
    z_extrude = 0.1

    paper_nx_total = 1024
    dx_constant = domain_length / paper_nx_total

    nx_1 = int(round((x_ramp_start - x_start) / dx_constant))
    nx_2 = int(round((x_kink - x_ramp_start) / dx_constant))
    nx_3 = int(round((x_throat_start - x_kink) / dx_constant))
    nx_cowl_front = int(round((x_cowl_bot - x_throat_start) / dx_constant))
    nx_cowl_arc = 10
    nx_wake = int(round((x_end - x_cowl_top) / dx_constant))
    nx_throat = nx_cowl_front + nx_cowl_arc + nx_wake - 2

    ny_bottom = 380
    ny_top = 120
    nz_total = 80

    p1 = geom.addPoint(x_start, 0, 0)
    p2 = geom.addPoint(x_ramp_start, 0, 0)
    p3 = geom.addPoint(x_kink, kink_height, 0)
    p4 = geom.addPoint(x_throat_start, ramp_height, 0)
    p5 = geom.addPoint(x_end, ramp_height, 0)

    p6 = geom.addPoint(x_start, y_split, 0)
    p7 = geom.addPoint(x_ramp_start, y_split, 0)
    p8 = geom.addPoint(x_kink, y_split, 0)
    p9 = geom.addPoint(x_throat_start, y_split, 0)

    p10_bot = geom.addPoint(x_cowl_bot, y_cowl_bot, 0)
    p10_center = geom.addPoint(xc, yc, 0)
    p10_top = geom.addPoint(x_cowl_top, y_cowl_top, 0)

    p11 = geom.addPoint(x_end, y_cowl_top, 0)
    p12 = geom.addPoint(x_end, y_split, 0)

    p13 = geom.addPoint(x_start, domain_height, 0)
    p14 = geom.addPoint(x_ramp_start, domain_height, 0)
    p15 = geom.addPoint(x_kink, domain_height, 0)
    p16 = geom.addPoint(x_throat_start, domain_height, 0)
    p17_bot = geom.addPoint(x_cowl_bot, domain_height, 0)
    p17_top = geom.addPoint(x_cowl_top, domain_height, 0)
    p18 = geom.addPoint(x_end, domain_height, 0)

    l_bottom = geom.addLine(p1, p2)
    l_wall_1 = geom.addLine(p2, p3)
    l_wall_2 = geom.addLine(p3, p4)
    l_throat_bot = geom.addLine(p4, p5)

    l_mid_1 = geom.addLine(p6, p7)
    l_mid_2 = geom.addLine(p7, p8)
    l_mid_3 = geom.addLine(p8, p9)
    l_throat_top = geom.addLine(p12, p9)

    l_cowl_front = geom.addLine(p9, p10_bot)
    l_cowl_arc = geom.addCircleArc(p10_bot, p10_center, p10_top)
    l_cowl_back = geom.addLine(p10_top, p11)

    l_top_1 = geom.addLine(p13, p14)
    l_top_2 = geom.addLine(p14, p15)
    l_top_3 = geom.addLine(p15, p16)
    l_top_4_front = geom.addLine(p16, p17_bot)
    l_top_4_arc = geom.addLine(p17_bot, p17_top)
    l_top_5 = geom.addLine(p17_top, p18)

    l_inlet_bot = geom.addLine(p1, p6)
    l_inlet_top = geom.addLine(p6, p13)
    l_v1_bot = geom.addLine(p2, p7)
    l_v1_top = geom.addLine(p7, p14)
    l_v2_bot = geom.addLine(p3, p8)
    l_v2_top = geom.addLine(p8, p15)
    l_throat_inlet = geom.addLine(p4, p9)
    l_v3 = geom.addLine(p9, p16)

    l_v4_bot = geom.addLine(p10_bot, p17_bot)
    l_v4_top = geom.addLine(p10_top, p17_top)

    l_out_int = geom.addLine(p5, p12)
    l_out_ext = geom.addLine(p11, p18)

    cl1_b = geom.addCurveLoop([l_bottom, l_v1_bot, -l_mid_1, -l_inlet_bot])
    s1_b = geom.addPlaneSurface([cl1_b])
    cl2_b = geom.addCurveLoop([l_wall_1, l_v2_bot, -l_mid_2, -l_v1_bot])
    s2_b = geom.addPlaneSurface([cl2_b])
    cl3_b = geom.addCurveLoop([l_wall_2, l_throat_inlet, -l_mid_3, -l_v2_bot])
    s3_b = geom.addPlaneSurface([cl3_b])
    cl4 = geom.addCurveLoop([l_throat_bot, l_out_int, l_throat_top, -l_throat_inlet])
    s4 = geom.addPlaneSurface([cl4])

    cl1_t = geom.addCurveLoop([l_mid_1, l_v1_top, -l_top_1, -l_inlet_top])
    s1_t = geom.addPlaneSurface([cl1_t])
    cl2_t = geom.addCurveLoop([l_mid_2, l_v2_top, -l_top_2, -l_v1_top])
    s2_t = geom.addPlaneSurface([cl2_t])
    cl3_t = geom.addCurveLoop([l_mid_3, l_v3, -l_top_3, -l_v2_top])
    s3_t = geom.addPlaneSurface([cl3_t])

    cl5_front = geom.addCurveLoop([l_cowl_front, l_v4_bot, -l_top_4_front, -l_v3])
    s5_front = geom.addPlaneSurface([cl5_front])

    cl5_arc = geom.addCurveLoop([l_cowl_arc, l_v4_top, -l_top_4_arc, -l_v4_bot])
    s5_arc = geom.addPlaneSurface([cl5_arc])

    cl6 = geom.addCurveLoop([l_cowl_back, l_out_ext, -l_top_5, -l_v4_top])
    s6 = geom.addPlaneSurface([cl6])

    geom.synchronize()

    for line in [l_bottom, l_mid_1, l_top_1]:
        mesh.setTransfiniteCurve(line, nx_1)
    for line in [l_wall_1, l_mid_2, l_top_2]:
        mesh.setTransfiniteCurve(line, nx_2)
    for line in [l_wall_2, l_mid_3, l_top_3]:
        mesh.setTransfiniteCurve(line, nx_3)
    for line in [l_throat_bot, l_throat_top]:
        mesh.setTransfiniteCurve(line, nx_throat)

    for line in [l_cowl_front, l_top_4_front]:
        mesh.setTransfiniteCurve(line, nx_cowl_front)
    for line in [l_cowl_arc, l_top_4_arc]:
        mesh.setTransfiniteCurve(line, nx_cowl_arc)
    for line in [l_cowl_back, l_top_5]:
        mesh.setTransfiniteCurve(line, nx_wake)

    for line in [l_inlet_bot, l_v1_bot, l_v2_bot]:
        mesh.setTransfiniteCurve(line, ny_bottom, "progression".capitalize(), 1.005)
    for line in [l_throat_inlet, l_out_int]:
        mesh.setTransfiniteCurve(line, ny_bottom, "bump".capitalize(), 0.05)
    for line in [l_inlet_top, l_v1_top, l_v2_top, l_v3, l_v4_bot, l_v4_top, l_out_ext]:
        mesh.setTransfiniteCurve(line, ny_top, "progression".capitalize(), 1.01)

    mesh.setTransfiniteSurface(s1_b, cornerTags=[p1, p2, p7, p6])
    mesh.setTransfiniteSurface(s2_b, cornerTags=[p2, p3, p8, p7])
    mesh.setTransfiniteSurface(s3_b, cornerTags=[p3, p4, p9, p8])
    mesh.setTransfiniteSurface(s1_t, cornerTags=[p6, p7, p14, p13])
    mesh.setTransfiniteSurface(s2_t, cornerTags=[p7, p8, p15, p14])
    mesh.setTransfiniteSurface(s3_t, cornerTags=[p8, p9, p16, p15])
    mesh.setTransfiniteSurface(s4, cornerTags=[p4, p5, p12, p9])
    mesh.setTransfiniteSurface(s5_front, cornerTags=[p9, p10_bot, p17_bot, p16])
    mesh.setTransfiniteSurface(s5_arc, cornerTags=[p10_bot, p10_top, p17_top, p17_bot])
    mesh.setTransfiniteSurface(s6, cornerTags=[p10_top, p11, p18, p17_top])

    surfaces = [
        (2, s1_b),
        (2, s2_b),
        (2, s3_b),
        (2, s1_t),
        (2, s2_t),
        (2, s3_t),
        (2, s4),
        (2, s5_front),
        (2, s5_arc),
        (2, s6),
    ]
    extruded_entities = geom.extrude(
        surfaces, 0, 0, z_extrude, numElements=[nz_total], recombine=True
    )

    geom.synchronize()

    volumes = [ent[1] for ent in extruded_entities if ent[0] == 3]
    fluid = gmsh.model.addPhysicalGroup(3, volumes)
    gmsh.model.setPhysicalName(3, fluid, "fluid")

    gmsh.option.setNumber("Mesh.RecombineAll", 1)
    gmsh.option.setNumber("Mesh.Smoothing", 10)
    mesh.generate(3)
    gmsh.write("mesh_3d.msh")
    gmsh.finalize()


if __name__ == "__main__":
    main()
