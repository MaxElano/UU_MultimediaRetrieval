import sys
sys.path.insert(0, 'D:\\UU\\Master\\Multimedia Retrieval\\Assignment\\Multimedia-Retrieval\\MRPipelineMLL') # location of src 

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
new_path = 'Data\\NormalizedShapeDatabase'

original_files = util.get_all_obj_files(original_path)
new_files = util.get_all_obj_files(new_path)

original_mesh = config.ml.load_mesh(util.get_path(original_files[0]))
new_mesh = config.ml.load_mesh(util.get_path(new_files[0]))

print(np.asarray(original_mesh.vertices)[0])
print(np.asarray(new_mesh.vertices)[0])

# Finish
end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")