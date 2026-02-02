from math import radians, tan, sqrt

import gmsh


def main():
    gmsh.initialize()
    gmsh.model.add("inlet-unstructured")

    # --- physics ---
    reynolds = 2.3e6
    mu = 1.0 / reynolds
    rho = 1.0
    u_inf = 1.0

    skin_friction_coeff = 0.0592 * (reynolds ** -0.2)
    tau_w = 0.5 * rho * (u_inf ** 2) * skin_friction_coeff
    u_tau = sqrt(tau_w / rho)

    target_y_plus = 5.0
    h_wall = (target_y_plus * mu) / (rho * u_tau)
    est_dt = 0.1 * h_wall / 1.5

    print("--- Mesh Statistics (Under-resolved) ---")
    print(f"Target y+: {target_y_plus}")
    print(f"Calculated First Cell Height: {h_wall:.4e}")
    print(f"Estimated Max Time Step (dt): ~{est_dt:.4e}")
    print("----------------------------------------")

    # --- geometry ---
    l0 = 150.0  # the inlet's chord
    scale_factor = 1 / l0  # nondimensional length scale factor

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

    # x coords
    x_start = 0.0
    x_ramp_start = domain_length - intake_length
    x_kink = x_ramp_start + kink_length
    x_throat_start = x_ramp_start + ramp_length
    x_cowl_tip = x_throat_start + (cowl_height / tan(radians(cowl_angle)))
    x_end = domain_length
    y_throat = ramp_height + throat_height

    # --- points and line ---

    lc_base = 0.05 * scale_factor
    lc_mid = 0.2 * scale_factor
    lc_far = 0.5 * scale_factor

    # points
    p1: int = gmsh.model.geo.addPoint(x_start, 0, 0, lc_mid)
    p2: int = gmsh.model.geo.addPoint(x_ramp_start, 0, 0, lc_base)
    p3: int = gmsh.model.geo.addPoint(x_kink, kink_height, 0, lc_base)
    p4: int = gmsh.model.geo.addPoint(x_throat_start, ramp_height, 0, lc_base)
    p5: int = gmsh.model.geo.addPoint(x_end, ramp_height, 0, lc_base)
    p6: int = gmsh.model.geo.addPoint(x_end, y_throat, 0, lc_base)
    p7: int = gmsh.model.geo.addPoint(x_throat_start, y_throat, 0, lc_base)
    p8: int = gmsh.model.geo.addPoint(x_cowl_tip, intake_height, 0, lc_base)
    p9: int = gmsh.model.geo.addPoint(x_end, intake_height, 0, lc_base)
    p10: int = gmsh.model.geo.addPoint(x_end, domain_height, 0, lc_mid)
    p11: int = gmsh.model.geo.addPoint(x_start, domain_height, 0, lc_far)
    points: list[int] = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]

    # lines
    lines = []
    for i in range(len(points) - 1):
        line = gmsh.model.geo.addLine(points[i], points[i + 1])
        lines.append(line)

    closure = gmsh.model.geo.addLine(points[-1], points[0])
    lines.append(closure)
    
    walls = [lines[i] for i in [1, 2, 3, 5, 6, 7]]

    # curve loop & surface
    curveloop = gmsh.model.geo.addCurveLoop(lines)
    surface = gmsh.model.geo.addPlaneSurface([curveloop])

    gmsh.model.geo.synchronize()
    
    # # fields
    # distance = gmsh.model.mesh.field.add("Distance")
    # gmsh.model.mesh.field.setNumbers(distance, "CurvesList", walls)

    # threshold = gmsh.model.mesh.field.add("Threshold")
    # gmsh.model.mesh.field.setNumber(threshold, "InField", distance)
    # gmsh.model.mesh.field.setNumber(threshold, "SizeMin", h_wall)
    # gmsh.model.mesh.field.setNumber(threshold, "SizeMax", lc_far)
    # gmsh.model.mesh.field.setAsBackgroundMesh(threshold)

    bl = gmsh.model.mesh.field.add("BoundaryLayer")
    gmsh.model.mesh.field.setNumbers(bl, "CurvesList", [lines[0]] + walls)
    gmsh.model.mesh.field.setNumbers(bl, "PointsList", [p1, p5, p6, p9])
    gmsh.model.mesh.field.setNumbers(bl, "FanPointsList", [p4, p7, p8])
    gmsh.model.mesh.field.setNumber(bl, "Size", h_wall)
    gmsh.model.mesh.field.setNumber(bl, "Ratio", 1.1)
    gmsh.model.mesh.field.setNumber(bl, "Thickness", 0.5 * scale_factor)
    gmsh.model.mesh.field.setNumber(bl, "Quads", 1)
    gmsh.model.mesh.field.setAsBoundaryLayer(bl)

    # physical groups
    fluid = gmsh.model.addPhysicalGroup(2, [surface])
    farfield = gmsh.model.addPhysicalGroup(1, [lines[i] for i in [8, 9, 10]])
    outlet = gmsh.model.addPhysicalGroup(1, [lines[4]])
    bottom = gmsh.model.addPhysicalGroup(1, [lines[0]])
    wall = gmsh.model.addPhysicalGroup(1, walls)

    gmsh.model.setPhysicalName(2, fluid, "fluid")
    gmsh.model.setPhysicalName(1, farfield, "farfield")
    gmsh.model.setPhysicalName(1, outlet, "outlet")
    gmsh.model.setPhysicalName(1, bottom, "bottom")
    gmsh.model.setPhysicalName(1, wall, "wall")

    gmsh.option.setNumber("Mesh.Algorithm", 6)

    gmsh.model.mesh.generate(2)
    gmsh.write("mesh-unstructured.msh")
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == "__main__":
    main()
