import gmsh
from math import radians, tan

def main():
    gmsh.initialize()
    gmsh.model.add("inlet-structured")

    # --- geometry ---
    l0 = 150.0 # the inlet's chord
    scale_factor = 1 / l0 # nondimensional length scale factor

    domain_length = 1.05 
    domain_height = 0.36  

    intake_length = 150.0 * scale_factor
    intake_height = 44.0 * scale_factor
    throat_height = 15.0 * scale_factor
    ramp_length = 81.7 * scale_factor
    ramp_height = 21.0 * scale_factor
    cowl_height = 8.0 * scale_factor

    ramp_angle_one = 10.0
    ramp_angle_two = 22.0
    cowl_angle = 30.0
    kink_length = (ramp_height - tan(radians(ramp_angle_two)) * ramp_length) / (
        tan(radians(ramp_angle_one)) - tan(radians(ramp_angle_two))
    )
    kink_height = tan(radians(ramp_angle_one)) * kink_length
    y_split = ramp_height + throat_height

    # x coords
    x_start = 0.0
    x_ramp_start = domain_length - intake_length
    x_kink = x_ramp_start + kink_length
    x_throat_start = x_ramp_start + ramp_length
    x_cowl_tip = x_throat_start + (cowl_height / tan(radians(cowl_angle)))
    x_end = domain_length

    # --- mesh resolution ---
    paper_domain_length = 1.05
    paper_nx_total = 1024
    dx_constant = paper_domain_length / paper_nx_total # ~0.001025

    nx_1 = int(round((x_ramp_start - x_start) / dx_constant))
    nx_2 = int(round((x_kink - x_ramp_start) / dx_constant))
    nx_3 = int(round((x_throat_start - x_kink) / dx_constant))
    nx_cowl = int(round((x_cowl_tip - x_throat_start) / dx_constant))
    nx_wake = int(round((x_end - x_cowl_tip) / dx_constant))
    nx_throat = nx_cowl + nx_wake

    ny_bottom = 380   
    ny_top = 380

    # --- points and line ---

    # bottom
    p1 = gmsh.model.geo.addPoint(x_start, 0, 0)
    p2 = gmsh.model.geo.addPoint(x_ramp_start, 0, 0)
    p3 = gmsh.model.geo.addPoint(x_kink, kink_height, 0)
    p4 = gmsh.model.geo.addPoint(x_throat_start, ramp_height, 0)
    p5 = gmsh.model.geo.addPoint(x_end, ramp_height, 0)

    # middle split
    p6 = gmsh.model.geo.addPoint(x_start, y_split, 0)         
    p7 = gmsh.model.geo.addPoint(x_ramp_start, y_split, 0)    
    p8 = gmsh.model.geo.addPoint(x_kink, y_split, 0)          
    p9 = gmsh.model.geo.addPoint(x_throat_start, y_split, 0) 
    
    # cowl
    p10 = gmsh.model.geo.addPoint(x_cowl_tip, intake_height, 0)
    p11 = gmsh.model.geo.addPoint(x_end, intake_height, 0)
    p12 = gmsh.model.geo.addPoint(x_end, y_split, 0)

    # top
    p13 = gmsh.model.geo.addPoint(x_start, domain_height, 0)
    p14 = gmsh.model.geo.addPoint(x_ramp_start, domain_height, 0)
    p15 = gmsh.model.geo.addPoint(x_kink, domain_height, 0)
    p16 = gmsh.model.geo.addPoint(x_throat_start, domain_height, 0)
    p17 = gmsh.model.geo.addPoint(x_cowl_tip, domain_height, 0)
    p18 = gmsh.model.geo.addPoint(x_end, domain_height, 0)

    # horizontal lines
    l_bottom = gmsh.model.geo.addLine(p1, p2)
    l_wall_1 = gmsh.model.geo.addLine(p2, p3)
    l_wall_2 = gmsh.model.geo.addLine(p3, p4)
    l_throat_bot = gmsh.model.geo.addLine(p4, p5)

    l_mid_1 = gmsh.model.geo.addLine(p6, p7)
    l_mid_2 = gmsh.model.geo.addLine(p7, p8)
    l_mid_3 = gmsh.model.geo.addLine(p8, p9)
    l_throat_top = gmsh.model.geo.addLine(p12, p9)
    
    l_cowl_top = gmsh.model.geo.addLine(p9, p10)
    l_cowl_back = gmsh.model.geo.addLine(p10, p11)

    l_top_1 = gmsh.model.geo.addLine(p13, p14)
    l_top_2 = gmsh.model.geo.addLine(p14, p15)
    l_top_3 = gmsh.model.geo.addLine(p15, p16)
    l_top_4 = gmsh.model.geo.addLine(p16, p17)
    l_top_5 = gmsh.model.geo.addLine(p17, p18)

    # vertical lines
    l_inlet_bot = gmsh.model.geo.addLine(p1, p6)
    l_inlet_top = gmsh.model.geo.addLine(p6, p13)
    l_v1_bot = gmsh.model.geo.addLine(p2, p7)
    l_v1_top = gmsh.model.geo.addLine(p7, p14)
    l_v2_bot = gmsh.model.geo.addLine(p3, p8)
    l_v2_top = gmsh.model.geo.addLine(p8, p15)
    l_throat_inlet = gmsh.model.geo.addLine(p4, p9)
    l_v3 = gmsh.model.geo.addLine(p9, p16)
    l_v4 = gmsh.model.geo.addLine(p10, p17)
    l_out_int = gmsh.model.geo.addLine(p5, p12)
    l_out_ext = gmsh.model.geo.addLine(p11, p18)

    # surfaces 
    cl1_b = gmsh.model.geo.addCurveLoop([l_bottom, l_v1_bot, -l_mid_1, -l_inlet_bot])
    s1_b = gmsh.model.geo.addPlaneSurface([cl1_b])
    cl2_b = gmsh.model.geo.addCurveLoop([l_wall_1, l_v2_bot, -l_mid_2, -l_v1_bot])
    s2_b = gmsh.model.geo.addPlaneSurface([cl2_b])
    cl3_b = gmsh.model.geo.addCurveLoop([l_wall_2, l_throat_inlet, -l_mid_3, -l_v2_bot])
    s3_b = gmsh.model.geo.addPlaneSurface([cl3_b])
    cl4 = gmsh.model.geo.addCurveLoop([l_throat_bot, l_out_int, l_throat_top, -l_throat_inlet])
    s4 = gmsh.model.geo.addPlaneSurface([cl4])
    cl1_t = gmsh.model.geo.addCurveLoop([l_mid_1, l_v1_top, -l_top_1, -l_inlet_top])
    s1_t = gmsh.model.geo.addPlaneSurface([cl1_t])
    cl2_t = gmsh.model.geo.addCurveLoop([l_mid_2, l_v2_top, -l_top_2, -l_v1_top])
    s2_t = gmsh.model.geo.addPlaneSurface([cl2_t])
    cl3_t = gmsh.model.geo.addCurveLoop([l_mid_3, l_v3, -l_top_3, -l_v2_top])
    s3_t = gmsh.model.geo.addPlaneSurface([cl3_t])
    cl5 = gmsh.model.geo.addCurveLoop([l_cowl_top, l_v4, -l_top_4, -l_v3])
    s5 = gmsh.model.geo.addPlaneSurface([cl5])
    cl6 = gmsh.model.geo.addCurveLoop([l_cowl_back, l_out_ext, -l_top_5, -l_v4])
    s6 = gmsh.model.geo.addPlaneSurface([cl6])

    gmsh.model.geo.synchronize()

    # --- transfinite mesh settings ---
    # horizontal transfinite curves
    for line in [l_bottom, l_mid_1, l_top_1]: 
        gmsh.model.mesh.setTransfiniteCurve(line, nx_1)
    for line in [l_wall_1, l_mid_2, l_top_2]: 
        gmsh.model.mesh.setTransfiniteCurve(line, nx_2)
    for line in [l_wall_2, l_mid_3, l_top_3]: 
        gmsh.model.mesh.setTransfiniteCurve(line, nx_3)
    for line in [l_throat_bot, l_throat_top]:
        gmsh.model.mesh.setTransfiniteCurve(line, nx_throat) # Uses calculated nx_throat (which is nx_cowl + nx_wake)
    for line in [l_cowl_top, l_top_4]: 
        gmsh.model.mesh.setTransfiniteCurve(line, nx_cowl)
    for line in [l_cowl_back, l_top_5]: 
        gmsh.model.mesh.setTransfiniteCurve(line, nx_wake)

    # vertical transfinite curves
    for line in [l_inlet_bot, l_v1_bot, l_v2_bot]:
        gmsh.model.mesh.setTransfiniteCurve(line, ny_bottom, "Progression", 1.005)
    for line in [l_throat_inlet, l_out_int]:
        gmsh.model.mesh.setTransfiniteCurve(line, ny_bottom, "Bump", 0.05)
    for line in [l_inlet_top, l_v1_top, l_v2_top, l_v3, l_v4, l_out_ext]:
        gmsh.model.mesh.setTransfiniteCurve(line, ny_top, "Progression", 1.005)

    # transfinite surfaces
    gmsh.model.mesh.setTransfiniteSurface(s1_b, cornerTags=[p1, p2, p7, p6])
    gmsh.model.mesh.setTransfiniteSurface(s2_b, cornerTags=[p2, p3, p8, p7])
    gmsh.model.mesh.setTransfiniteSurface(s3_b, cornerTags=[p3, p4, p9, p8])
    gmsh.model.mesh.setTransfiniteSurface(s1_t, cornerTags=[p6, p7, p14, p13])
    gmsh.model.mesh.setTransfiniteSurface(s2_t, cornerTags=[p7, p8, p15, p14])
    gmsh.model.mesh.setTransfiniteSurface(s3_t, cornerTags=[p8, p9, p16, p15])
    gmsh.model.mesh.setTransfiniteSurface(s4, cornerTags=[p4, p5, p12, p9])
    gmsh.model.mesh.setTransfiniteSurface(s5, cornerTags=[p9, p10, p17, p16])
    gmsh.model.mesh.setTransfiniteSurface(s6, cornerTags=[p10, p11, p18, p17])

    # --- physical groups and export ---
    inlet_lines = [l_inlet_bot, l_inlet_top]
    top_lines = [l_top_1, l_top_2, l_top_3, l_top_4, l_top_5]
    bottom_lines = [l_bottom]
    wall_lines = [l_wall_1, l_wall_2, l_throat_bot, l_throat_top, l_cowl_top, l_cowl_back]

    all_surfaces = [s1_b, s1_t, s2_b, s2_t, s3_b, s3_t, s4, s5, s6]
    fluid = gmsh.model.addPhysicalGroup(2, all_surfaces)
    farfield = gmsh.model.addPhysicalGroup(1, inlet_lines + top_lines + [l_out_ext])
    outlet = gmsh.model.addPhysicalGroup(1, [l_out_int])
    bottom = gmsh.model.addPhysicalGroup(1, bottom_lines)    
    wall = gmsh.model.addPhysicalGroup(1, wall_lines)

    gmsh.model.setPhysicalName(2, fluid, "fluid")
    gmsh.model.setPhysicalName(1, farfield, "farfield")
    gmsh.model.setPhysicalName(1, outlet, "outlet")
    gmsh.model.setPhysicalName(1, bottom, "bottom")    
    gmsh.model.setPhysicalName(1, wall, "wall")

    gmsh.option.setNumber("Mesh.RecombineAll", 1)
    gmsh.option.setNumber("Mesh.Smoothing", 10)
    gmsh.model.mesh.generate(2)
    gmsh.write("mesh.msh")
    gmsh.fltk.run()
    gmsh.finalize()

if __name__ == "__main__":
    main()