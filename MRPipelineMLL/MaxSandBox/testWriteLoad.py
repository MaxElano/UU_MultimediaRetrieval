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
specific_object_new = 'Quadruped\\m94'

original_mesh = config.ml.load_mesh(util.get_path([original_path, specific_object_original]))
config.ml.save_mesh_numpy(util.get_path([new_path, specific_object_new]), np.asarray(original_mesh.vertices), np.asarray(original_mesh.triangles))

seth = config.ml.load_mesh(util.get_path([new_path, specific_object_new]) + '.npz')

print(np.asarray(original_mesh.vertices)[0])
print(np.asarray(original_mesh.vertices)[1])
print(np.asarray(original_mesh.vertices).shape[0])
print(np.asarray(seth.vertices)[0])
print(np.asarray(seth.vertices)[1])
print(np.asarray(seth.vertices).shape[0])

# Finish
end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")