from math import radians, tan

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
    blunt_height = 1.0 * scale_factor
    y_split_top = y_split + blunt_height

    x_start = 0.0
    x_ramp_start = domain_length - intake_length
    x_kink = x_ramp_start + kink_length
    x_throat_start = x_ramp_start + ramp_length

    x_cowl_tip = x_throat_start + (
        (intake_height - y_split_top) / tan(radians(cowl_angle))
    )
    x_end = domain_length
    z_extrude = 0.1

    paper_nx_total = 1024
    dx_constant = domain_length / paper_nx_total

    nx_1 = int(round((x_ramp_start - x_start) / dx_constant))
    nx_2 = int(round((x_kink - x_ramp_start) / dx_constant))
    nx_3 = int(round((x_throat_start - x_kink) / dx_constant))
    nx_cowl = int(round((x_cowl_tip - x_throat_start) / dx_constant))
    nx_wake = int(round((x_end - x_cowl_tip) / dx_constant))
    nx_throat = nx_cowl + nx_wake - 1

    ny_bottom = 380
    ny_mid = 10
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
    p9_bot = geom.addPoint(x_throat_start, y_split, 0)

    p_mt1 = geom.addPoint(x_start, y_split_top, 0)
    p_mt2 = geom.addPoint(x_ramp_start, y_split_top, 0)
    p_mt3 = geom.addPoint(x_kink, y_split_top, 0)
    p9_top = geom.addPoint(x_throat_start, y_split_top, 0)

    p10 = geom.addPoint(x_cowl_tip, intake_height, 0)
    p11 = geom.addPoint(x_end, intake_height, 0)
    p12 = geom.addPoint(x_end, y_split, 0)

    p13 = geom.addPoint(x_start, domain_height, 0)
    p14 = geom.addPoint(x_ramp_start, domain_height, 0)
    p15 = geom.addPoint(x_kink, domain_height, 0)
    p16 = geom.addPoint(x_throat_start, domain_height, 0)
    p17 = geom.addPoint(x_cowl_tip, domain_height, 0)
    p18 = geom.addPoint(x_end, domain_height, 0)

    l_b1 = geom.addLine(p1, p2)
    l_b2 = geom.addLine(p2, p3)
    l_b3 = geom.addLine(p3, p4)
    l_b4 = geom.addLine(p4, p5)

    l_sb1 = geom.addLine(p6, p7)
    l_sb2 = geom.addLine(p7, p8)
    l_sb3 = geom.addLine(p8, p9_bot)
    l_sb4 = geom.addLine(p9_bot, p12)

    l_st1 = geom.addLine(p_mt1, p_mt2)
    l_st2 = geom.addLine(p_mt2, p_mt3)
    l_st3 = geom.addLine(p_mt3, p9_top)

    l_ct1 = geom.addLine(p9_top, p10)
    l_ct2 = geom.addLine(p10, p11)

    l_t1 = geom.addLine(p13, p14)
    l_t2 = geom.addLine(p14, p15)
    l_t3 = geom.addLine(p15, p16)
    l_t4 = geom.addLine(p16, p17)
    l_t5 = geom.addLine(p17, p18)

    l_v0_b = geom.addLine(p1, p6)
    l_v1_b = geom.addLine(p2, p7)
    l_v2_b = geom.addLine(p3, p8)
    l_v3_b = geom.addLine(p4, p9_bot)
    l_v5_b = geom.addLine(p5, p12)

    l_v0_m = geom.addLine(p6, p_mt1)
    l_v1_m = geom.addLine(p7, p_mt2)
    l_v2_m = geom.addLine(p8, p_mt3)
    l_v3_m = geom.addLine(p9_bot, p9_top)

    l_v0_t = geom.addLine(p_mt1, p13)
    l_v1_t = geom.addLine(p_mt2, p14)
    l_v2_t = geom.addLine(p_mt3, p15)
    l_v3_t = geom.addLine(p9_top, p16)
    l_v4 = geom.addLine(p10, p17)
    l_v5_t = geom.addLine(p11, p18)

    s1 = geom.addPlaneSurface([geom.addCurveLoop([l_b1, l_v1_b, -l_sb1, -l_v0_b])])
    s2 = geom.addPlaneSurface([geom.addCurveLoop([l_b2, l_v2_b, -l_sb2, -l_v1_b])])
    s3 = geom.addPlaneSurface([geom.addCurveLoop([l_b3, l_v3_b, -l_sb3, -l_v2_b])])
    s4 = geom.addPlaneSurface([geom.addCurveLoop([l_b4, l_v5_b, -l_sb4, -l_v3_b])])

    s5 = geom.addPlaneSurface([geom.addCurveLoop([l_sb1, l_v1_m, -l_st1, -l_v0_m])])
    s6 = geom.addPlaneSurface([geom.addCurveLoop([l_sb2, l_v2_m, -l_st2, -l_v1_m])])
    s7 = geom.addPlaneSurface([geom.addCurveLoop([l_sb3, l_v3_m, -l_st3, -l_v2_m])])

    s8 = geom.addPlaneSurface([geom.addCurveLoop([l_st1, l_v1_t, -l_t1, -l_v0_t])])
    s9 = geom.addPlaneSurface([geom.addCurveLoop([l_st2, l_v2_t, -l_t2, -l_v1_t])])
    s10 = geom.addPlaneSurface([geom.addCurveLoop([l_st3, l_v3_t, -l_t3, -l_v2_t])])
    s11 = geom.addPlaneSurface([geom.addCurveLoop([l_ct1, l_v4, -l_t4, -l_v3_t])])
    s12 = geom.addPlaneSurface([geom.addCurveLoop([l_ct2, l_v5_t, -l_t5, -l_v4])])

    geom.synchronize()

    for line in [l_b1, l_sb1, l_st1, l_t1]:
        mesh.setTransfiniteCurve(line, nx_1)
    for line in [l_b2, l_sb2, l_st2, l_t2]:
        mesh.setTransfiniteCurve(line, nx_2)
    for line in [l_b3, l_sb3, l_st3, l_t3]:
        mesh.setTransfiniteCurve(line, nx_3)
    for line in [l_b4, l_sb4]:
        mesh.setTransfiniteCurve(line, nx_throat)
    for line in [l_ct1, l_t4]:
        mesh.setTransfiniteCurve(line, nx_cowl)
    for line in [l_ct2, l_t5]:
        mesh.setTransfiniteCurve(line, nx_wake)

    for line in [l_v0_b, l_v1_b, l_v2_b, l_v3_b, l_v5_b]:
        mesh.setTransfiniteCurve(line, ny_bottom, "Progression", 1.005)

    for line in [l_v0_m, l_v1_m, l_v2_m, l_v3_m]:
        mesh.setTransfiniteCurve(line, ny_mid)

    for line in [l_v0_t, l_v1_t, l_v2_t, l_v3_t, l_v4, l_v5_t]:
        mesh.setTransfiniteCurve(line, ny_top, "Progression", 1.01)

    mesh.setTransfiniteSurface(s1, cornerTags=[p1, p2, p7, p6])
    mesh.setTransfiniteSurface(s2, cornerTags=[p2, p3, p8, p7])
    mesh.setTransfiniteSurface(s3, cornerTags=[p3, p4, p9_bot, p8])
    mesh.setTransfiniteSurface(s4, cornerTags=[p4, p5, p12, p9_bot])

    mesh.setTransfiniteSurface(s5, cornerTags=[p6, p7, p_mt2, p_mt1])
    mesh.setTransfiniteSurface(s6, cornerTags=[p7, p8, p_mt3, p_mt2])
    mesh.setTransfiniteSurface(s7, cornerTags=[p8, p9_bot, p9_top, p_mt3])

    mesh.setTransfiniteSurface(s8, cornerTags=[p_mt1, p_mt2, p14, p13])
    mesh.setTransfiniteSurface(s9, cornerTags=[p_mt2, p_mt3, p15, p14])
    mesh.setTransfiniteSurface(s10, cornerTags=[p_mt3, p9_top, p16, p15])
    mesh.setTransfiniteSurface(s11, cornerTags=[p9_top, p10, p17, p16])
    mesh.setTransfiniteSurface(s12, cornerTags=[p10, p11, p18, p17])

    all_surfaces = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]
    for s in all_surfaces:
        mesh.setRecombine(2, s)

    surfaces_extrude = [(2, s) for s in all_surfaces]
    extruded_entities = geom.extrude(
        surfaces_extrude, 0, 0, z_extrude, numElements=[nz_total], recombine=True
    )

    geom.synchronize()

    volumes = [ent[1] for ent in extruded_entities if ent[0] == 3]
    fluid = gmsh.model.addPhysicalGroup(3, volumes)
    gmsh.model.setPhysicalName(3, fluid, "fluid")

    gmsh.option.setNumber("Mesh.RecombineAll", 1)
    gmsh.option.setNumber("Mesh.Smoothing", 10)
    mesh.generate(3)
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == "__main__":
    main()
