import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import shapeNormalizer
import config
import open3d as o3d
import time

start = time.time()
config.initialize(skip_renderer=True)
config.lg.set_to_print()
config.lg.log("Starting one normalization")
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings
sn = shapeNormalizer()


original_mesh_path = "Data\\OriginalShapeDatabase\\Cellphone\\D00542.obj"
new_path = 'Data\\NormalizedShapeDatabase'


original_mesh = config.ml.load_mesh(original_mesh_path)
split = original_mesh_path.split("\\")
database = '\\'.join(split[:-2])
clas = split[-2]
name = split[-1]
sn.run_one_mesh(original_mesh, [database, clas, name], new_path)

end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")