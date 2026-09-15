from renderer import renderer
from meshLoader import meshLoader
import numpy as np

mesh_path = "Data\OriginalShapeDatabase\Starship\m1355.obj"

r = renderer()
ml = meshLoader()

mesh = ml.load_mesh(mesh_path)
r.visualize_mesh(mesh)

# # OPTIONAL: Get basic mesh features
# vertices = np.asarray(mesh.vertices)
# triangles = np.asarray(mesh.triangles)

# print(vertices.shape[0])
# print(triangles.shape[0])

