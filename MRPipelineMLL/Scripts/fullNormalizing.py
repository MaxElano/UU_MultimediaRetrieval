import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import preNormalizer, shapeNormalizerOpen3D
from preprocessChecker import preprocessChecker
import config
import open3d as o3d
import time

start = time.time()
config.initialize(skip_renderer=True)
config.lg.set_to_write()
config.lg.log("Starting entire normalization pipeline + testing")

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings

og_path = "Data\\OriginalShapeDatabase"
middle_path = "Data\\PreprocessedShapeDatabase"
new_path = "Data\\NormalizedShapeDatabase"

pn = preNormalizer()
pn.process_all_meshes(og_path, middle_path)

sn = shapeNormalizerOpen3D()
sn.normalize_all_meshes(middle_path, new_path)

ppc = preprocessChecker()
ppc.compute_all_checks(show_update_every=250, processed_data_path=new_path)    

end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")