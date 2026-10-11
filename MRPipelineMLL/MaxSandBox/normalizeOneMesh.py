import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import shapeNormalizerPyMeshLab
import config
import open3d as o3d
import time
from renderer import render_mode


object_path = "Cellphone\\D00542.obj"
original_mesh_path = "Data\\OriginalShapeDatabase"
new_path = 'Data\\NormalizedShapeDatabase'
show = True


start = time.time()
config.initialize(skip_renderer=not show)
config.lg.set_to_print()
config.lg.log("Starting one normalization")
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings
sn = shapeNormalizerPyMeshLab()

original_mesh = config.ml.load_mesh(original_mesh_path + '\\' + object_path, pyMeshLab=True)
split = object_path.split("\\")
clas = split[-2]
name = split[-1]
sn.run_one_mesh(original_mesh, [original_mesh_path, clas, name], new_path)

end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")

if (show):
    # Load mesh
    mesh1 = config.ml.load_mesh(new_path + '\\' + object_path, open3d=True)
    #mesh2 = config.ml.load_mesh(mesh_path_2)

    # Render mesh
    config.rd.set_render_mode(render_mode.MIXED)
    config.rd.set_background([1,1,1])
    config.rd.set_mesh_color([1,0,0])
    config.rd.add_mesh(mesh1, new_path + '\\' + object_path)
    #config.rd.add_mesh(mesh2, mesh_path_2)
    config.rd.add_world_axis()
    #config.rd.take_screenshot("I\\Want\\Way\\Too\\Many\\Files\\test.png")
    config.rd.launch_renderer()