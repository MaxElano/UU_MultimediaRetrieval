import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import shapeNormalizer
from preprocessChecker import preprocessChecker
import config
import open3d as o3d
import time

start = time.time()
config.initialize(skip_renderer=True)
config.lg.set_to_write()
config.lg.log("Starting entire normalization pipeline + testing")
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings
sn = shapeNormalizer()
original_path = 'Data\\OriginalShapeDataBase'
new_path = 'Data\\NormalizedShapeDatabase'
sn.normalize_all_meshes(original_path, new_path, show_update_every=100)

ppc = preprocessChecker()
ppc.compute_all_checks(show_update_every=100, processed_data_path=new_path)    

end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")