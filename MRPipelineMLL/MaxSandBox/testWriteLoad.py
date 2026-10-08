import sys
personal_path = "C:\\UU\\Master\\Multimedia Retrieval\\Assignment"
sys.path.insert(0, personal_path + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import shapeNormalizer
from preprocessChecker import preprocessChecker
import config
import open3d as o3d
import time
import utility as util
import numpy as np

# Setup
start = time.time()
config.initialize(skip_renderer=True)
config.lg.set_to_print()
config.lg.log("Start comparing")
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings


# Actual code
original_path = 'Data\\OriginalShapeDataBase'
new_path = 'Data\\TestDatabase'

# original_files = util.get_all_obj_files(original_path)
# new_files = util.get_all_obj_files(new_path)

specific_object_original = 'Quadruped\\m94.obj'
specific_object_new = 'Quadruped\\m94.obj'

original_mesh = config.ml.load_mesh(util.get_path([original_path, specific_object_original]))
temp_mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(original_mesh.vertices), o3d.utility.Vector3iVector(original_mesh.triangles))
temp_mesh.triangle_normals = o3d.utility.Vector3dVector([])
temp_mesh.vertex_normals = original_mesh.vertex_normals
#temp_mesh.compute_vertex_normals() #This line solves the duplicate vertices issue, without this loading new mesh has less vertices
util.create_folder(new_path + "\\Quadruped")
util.empty_file(util.get_path([new_path, specific_object_new]))
o3d.io.write_triangle_mesh(util.get_path([new_path, specific_object_new]), temp_mesh)

new_mesh = config.ml.load_mesh(util.get_path([new_path, specific_object_new]))

print(np.asarray(original_mesh.vertices)[0])
print(np.asarray(original_mesh.vertices)[1])
print(np.asarray(original_mesh.vertices).shape[0])
print(np.asarray(new_mesh.vertices)[0])
print(np.asarray(new_mesh.vertices)[1])
print(np.asarray(new_mesh.vertices).shape[0])

# Finish
end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")