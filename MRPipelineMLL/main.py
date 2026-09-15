from renderer import renderer, render_mode
from meshLoader import meshLoader
import numpy as np

mesh_path = "Data\OriginalShapeDatabase\Starship\m1355.obj"

r = renderer()
ml = meshLoader()

mesh = ml.load_mesh(mesh_path)
r.visualize_mesh(mesh, render_mode.SMOOTHSHADE)

# # OPTIONAL: Get basic mesh features
# vertices = np.asarray(mesh.vertices)
# triangles = np.asarray(mesh.triangles)

# print(vertices.shape[0])
# print(triangles.shape[0])

