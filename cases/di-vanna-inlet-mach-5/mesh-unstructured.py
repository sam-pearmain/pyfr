from math import radians, tan

import gmsh


def main():
    gmsh.initialize()
    gmsh.model.add("inlet-unstructured")

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

    lc_base = 0.5 * scale_factor
    lc_wall = 0.1 * scale_factor
    lc_far = lc_base

    # points
    p1: int = gmsh.model.geo.addPoint(x_start, 0, 0, lc_base)
    p2: int = gmsh.model.geo.addPoint(x_ramp_start, 0, 0, lc_base)
    p3: int = gmsh.model.geo.addPoint(x_kink, kink_height, 0, lc_base)
    p4: int = gmsh.model.geo.addPoint(x_throat_start, ramp_height, 0, lc_base)
    p5: int = gmsh.model.geo.addPoint(x_end, ramp_height, 0, lc_base)
    p6: int = gmsh.model.geo.addPoint(x_end, y_throat, 0, lc_base)
    p7: int = gmsh.model.geo.addPoint(x_throat_start, y_throat, 0, lc_base)
    p8: int = gmsh.model.geo.addPoint(x_cowl_tip, intake_height, 0, lc_base)
    p9: int = gmsh.model.geo.addPoint(x_end, intake_height, 0, lc_base)
    p10: int = gmsh.model.geo.addPoint(x_end, domain_height, 0, lc_base)
    p11: int = gmsh.model.geo.addPoint(x_start, domain_height, 0, lc_base)
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
    # gmsh.model.mesh.field.setNumber(threshold, "SizeMin", lc_wall)
    # gmsh.model.mesh.field.setNumber(threshold, "SizeMax", lc_far)
    # gmsh.model.mesh.field.setAsBackgroundMesh(threshold)

    bl = gmsh.model.mesh.field.add("BoundaryLayer")
    gmsh.model.mesh.field.setNumbers(bl, "CurvesList", [lines[0]] + walls)
    gmsh.model.mesh.field.setNumbers(bl, "PointsList", [p1, p5, p6, p9])
    gmsh.model.mesh.field.setNumbers(bl, "FanPointsList", [p7])
    gmsh.model.mesh.field.setNumber(bl, "Size", 0.02 * scale_factor)
    gmsh.model.mesh.field.setNumber(bl, "Ratio", 1.1)
    gmsh.model.mesh.field.setNumber(bl, "Thickness", 1 * scale_factor)
    gmsh.model.mesh.field.setNumber(bl, "Quads", 1)
    gmsh.model.mesh.field.setAsBoundaryLayer(bl)

    # physical groups
    gmsh.model.addPhysicalGroup(2, [surface], name="fluid")
    gmsh.model.addPhysicalGroup(1, [lines[i] for i in [8, 9, 10]], name="farfield")
    gmsh.model.addPhysicalGroup(1, [lines[4]], name="outlet")
    gmsh.model.addPhysicalGroup(1, [lines[0]], name="bottom")
    gmsh.model.addPhysicalGroup(1, walls, name="wall")
    
    gmsh.option.setNumber("Mesh.Algorithm", 6)

    gmsh.model.mesh.generate(2)
    gmsh.write("mesh-unstructured.msh")
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == "__main__":
    main()
