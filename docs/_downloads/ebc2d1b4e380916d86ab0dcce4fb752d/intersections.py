import math
import numpy as np
import compas_libigl as igl

from compas.geometry import add_vectors, scale_vector, cross_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import Point, Vector, Line, Plane, Sphere
from compas.geometry import Translation
from compas.datastructures import Mesh

from compas_viewers.objectviewer import ObjectViewer

# ==============================================================================
# Input geometry
# ==============================================================================

mesh = Mesh.from_off(igl.get('tubemesh.off'))
mesh.quads_to_triangles()

z = mesh.vertices_attribute('z')
zmin = min(z)

T = Translation.from_vector([0, 0, -zmin])
mesh.transform(T)

# ==============================================================================
# Rays
# ==============================================================================

base = Point(-7, 0, 0)

sphere = Sphere(base, 1.0)

theta = np.linspace(0, np.pi, 20, endpoint=False)
phi = np.linspace(0, 2 * np.pi, 20, endpoint=False)
theta, phi = np.meshgrid(theta, phi)
theta = theta.ravel()
phi = phi.ravel()
r = 1.0
x = r * np.sin(theta) * np.cos(phi) + base.x
y = r * np.sin(theta) * np.sin(phi) + base.y
z = r * np.cos(theta)

xyz = np.vstack((x, y, z)).T
mask = xyz[:, 2] > 0
hemi = xyz[mask]

rays = []
for x, y, z in hemi:
    point = Point(x, y, z)
    vector = point - base
    vector.unitize()
    rays.append((base, vector))

# ==============================================================================
# Intersections
# ==============================================================================

index_face = {index: face for index, face in enumerate(mesh.faces())}

hits_per_ray = igl.intersection_rays_mesh(rays, mesh)

intersections = []
for ray, hits in zip(rays, hits_per_ray):
    if hits:
        base, vector = ray
        index = hits[0][0]
        distance = hits[0][3]
        face = index_face[index]
        point = base + vector * distance
        intersections.append(point)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = ObjectViewer()

viewer.add(mesh, settings={'color': '#cccccc', 'opacity': 0.5, 'edges.on': False})

for intersection in intersections:
    viewer.add(Line(base, intersection), settings={'edges.color': '#ff0000', 'edges.width': 3})

viewer.update()
viewer.show()
