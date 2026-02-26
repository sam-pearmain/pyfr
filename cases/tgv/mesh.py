import math

import gmsh


def main():
    gmsh.initialize()
    gmsh.model.add("tgv")

    pi = math.pi
    L = 1.0
    d = 2.0 * pi * L

    box = gmsh.model.occ.addBox(-pi * L, -pi * L, -pi * L, d, d, d)
    gmsh.model.occ.synchronize()

    surfaces = gmsh.model.getEntities(2)
    s_xmin = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[0] + pi * L) < 1e-6
    ][0]
    s_xmax = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[0] - pi * L) < 1e-6
    ][0]
    s_ymin = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[1] + pi * L) < 1e-6
    ][0]
    s_ymax = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[1] - pi * L) < 1e-6
    ][0]
    s_zmin = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[2] + pi * L) < 1e-6
    ][0]
    s_zmax = [
        s[1]
        for s in surfaces
        if abs(gmsh.model.occ.getCenterOfMass(2, s[1])[2] - pi * L) < 1e-6
    ][0]

    gmsh.model.addPhysicalGroup(2, [s_xmin], name="periodic_0_l")
    gmsh.model.addPhysicalGroup(2, [s_xmax], name="periodic_0_r")
    gmsh.model.addPhysicalGroup(2, [s_ymin], name="periodic_1_l")
    gmsh.model.addPhysicalGroup(2, [s_ymax], name="periodic_1_r")
    gmsh.model.addPhysicalGroup(2, [s_zmin], name="periodic_2_l")
    gmsh.model.addPhysicalGroup(2, [s_zmax], name="periodic_2_r")

    gmsh.model.addPhysicalGroup(3, [box], name="fluid")

    gmsh.model.mesh.setPeriodic(
        2, [s_xmax], [s_xmin], [1, 0, 0, d, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    )
    gmsh.model.mesh.setPeriodic(
        2, [s_ymax], [s_ymin], [1, 0, 0, 0, 0, 1, 0, d, 0, 0, 1, 0, 0, 0, 0, 1]
    )
    gmsh.model.mesh.setPeriodic(
        2, [s_zmax], [s_zmin], [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, d, 0, 0, 0, 1]
    )

    N = 17
    for c in gmsh.model.getEntities(1):
        gmsh.model.mesh.setTransfiniteCurve(c[1], N)

    for s in surfaces:
        gmsh.model.mesh.setTransfiniteSurface(s[1])
        gmsh.model.mesh.setRecombine(2, s[1])

    gmsh.model.mesh.setTransfiniteVolume(box)

    gmsh.model.mesh.generate(3)
    gmsh.write("tgv.msh")

    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == "__main__":
    main()
