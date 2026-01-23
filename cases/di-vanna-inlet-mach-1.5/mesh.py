import gmsh
from math import radians, tan

L_REF = 150
S = 1.0 / L_REF

DOMAIN_LENGTH, DOMAIN_HEIGHT = (1.04 * 150) * S, (0.4 * 150) * S
INTAKE_LENGTH, INTAKE_HEIGHT = 150.0 * S, 44.0 * S
THROAT_HEIGHT, RAMP_LENGTH = 15.0 * S, 81.7 * S
RAMP_HEIGHT = 21.0 * S
RAMP_ANGLE_ONE, RAMP_ANGLE_TWO = 10.0, 22.0
COWL_ANGLE, COWL_HEIGHT = 30.0, 8.0 * S

KINK_LENGTH = (RAMP_HEIGHT - tan(radians(RAMP_ANGLE_TWO)) * RAMP_LENGTH) / (
    tan(radians(RAMP_ANGLE_ONE)) - tan(radians(RAMP_ANGLE_TWO))
)
KINK_HEIGHT = tan(radians(RAMP_ANGLE_ONE)) * KINK_LENGTH


def main():
    gmsh.initialize()
    gmsh.model.add("inlet")
    lc_wall = 0.05 * S
    lc_far = 0.5 * S

    # domain bounds
    p1 = gmsh.model.geo.addPoint(0, 0, 0, lc_wall)
    _p2 = gmsh.model.geo.addPoint(DOMAIN_LENGTH, 0, 0, lc_far)
    p3 = gmsh.model.geo.addPoint(DOMAIN_LENGTH, DOMAIN_HEIGHT, 0, lc_far)
    p4 = gmsh.model.geo.addPoint(0, DOMAIN_HEIGHT, 0, lc_far)

    # ramp points
    p5 = gmsh.model.geo.addPoint(DOMAIN_LENGTH - INTAKE_LENGTH, 0, 0, lc_wall)
    p6 = gmsh.model.geo.addPoint(
        DOMAIN_LENGTH - INTAKE_LENGTH + KINK_LENGTH, KINK_HEIGHT, 0, lc_wall
    )
    p7 = gmsh.model.geo.addPoint(
        DOMAIN_LENGTH - INTAKE_LENGTH + RAMP_LENGTH, RAMP_HEIGHT, 0, lc_wall
    )
    p8 = gmsh.model.geo.addPoint(DOMAIN_LENGTH, RAMP_HEIGHT, 0, lc_wall)

    # cowl points
    p9 = gmsh.model.geo.addPoint(
        DOMAIN_LENGTH - INTAKE_LENGTH + RAMP_LENGTH,
        RAMP_HEIGHT + THROAT_HEIGHT,
        0,
        lc_wall,
    )
    p10 = gmsh.model.geo.addPoint(
        DOMAIN_LENGTH, RAMP_HEIGHT + THROAT_HEIGHT, 0, lc_wall
    )
    p11 = gmsh.model.geo.addPoint(DOMAIN_LENGTH, INTAKE_HEIGHT, 0, lc_wall)
    p12 = gmsh.model.geo.addPoint(
        DOMAIN_LENGTH
        - INTAKE_LENGTH
        + RAMP_LENGTH
        + (COWL_HEIGHT / tan(radians(COWL_ANGLE))),
        INTAKE_HEIGHT,
        0,
        lc_wall,
    )

    # lines
    l1: int = gmsh.model.geo.addLine(p1, p5)
    l2: int = gmsh.model.geo.addLine(p5, p6)
    l3: int = gmsh.model.geo.addLine(p6, p7)
    l4: int = gmsh.model.geo.addLine(p7, p8)
    l5: int = gmsh.model.geo.addLine(p8, p10)
    l6: int = gmsh.model.geo.addLine(p10, p9)
    l7: int = gmsh.model.geo.addLine(p9, p12)
    l8: int = gmsh.model.geo.addLine(p12, p11)
    l9: int = gmsh.model.geo.addLine(p11, p3)
    l10: int = gmsh.model.geo.addLine(p3, p4)
    l11: int = gmsh.model.geo.addLine(p4, p1)

    # curve and plane
    cl1: int = gmsh.model.geo.addCurveLoop(
        [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]
    )
    sf1: int = gmsh.model.geo.addPlaneSurface([cl1])
    walls = [l1, l2, l3, l4, l6, l7, l8]

    gmsh.model.geo.synchronize()

    # distance field
    distance: int = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(distance, "CurvesList", walls)

    # threshold field
    threshold = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(threshold, "InField", distance)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMin", lc_wall)
    gmsh.model.mesh.field.setNumber(threshold, "DistMin", 6.0 * S)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMax", lc_far)
    gmsh.model.mesh.field.setNumber(threshold, "DistMax", 80.0 * S)
    gmsh.model.mesh.field.setAsBackgroundMesh(threshold)

    # meshing algorithm
    gmsh.option.setNumber("Mesh.Algorithm", 6)

    # physical groups
    fluid = gmsh.model.addPhysicalGroup(2, [sf1])
    inlet = gmsh.model.addPhysicalGroup(1, [l11])
    outlet = gmsh.model.addPhysicalGroup(1, [l5, l9])
    top = gmsh.model.addPhysicalGroup(1, [l10])
    wall = gmsh.model.addPhysicalGroup(1, walls)

    gmsh.model.setPhysicalName(2, fluid, "fluid")
    gmsh.model.setPhysicalName(1, inlet, "inlet")
    gmsh.model.setPhysicalName(2, outlet, "outlet")
    gmsh.model.setPhysicalName(2, top, "top")
    gmsh.model.setPhysicalName(2, wall, "wall")

    # generate and write out
    gmsh.model.mesh.generate(2)
    gmsh.write("inlet.msh")
    gmsh.finalize()


if __name__ == "__main__":
    main()