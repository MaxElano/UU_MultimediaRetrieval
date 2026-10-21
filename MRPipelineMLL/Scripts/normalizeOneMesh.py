import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

#from shapeNormalizer import shapeNormalizerPyMeshLab
from shapeNormalizer import preNormalizer
from shapeNormalizer import shapeNormalizerOpen3D
import config
import open3d as o3d
import time
from renderer import render_mode

object_path = "AquaticAnimal\\m57.obj"
new_object_path = "AquaticAnimal\\m57.npz"
original_mesh_path = "Data\\Small\\OriginalShapeDatabase"
middle_path = "Data\\Small\\PreprocessedShapeDatabase"
new_path = "Data\\Small\\NormalizedShapeDatabase"
show = True


start = time.time()
config.initialize(skip_renderer=not show)
config.lg.set_to_print()
config.lg.log("Starting one normalization")
#o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings
preNorm = preNormalizer()
norm = shapeNormalizerOpen3D()


# pre normalization steps
original_mesh = config.ml.load_mesh(original_mesh_path + '\\' + object_path, pyMeshLab=True)
config.lg.log(f"amount of vertices: {original_mesh.current_mesh().vertex_number()}")
split = object_path.split("\\")
clas = split[-2]
name = split[-1]
preNorm.run_one_mesh(original_mesh, [original_mesh_path, clas, name], middle_path)
config.lg.log(f"filling holes and remeshing done. new amount of vertices: {original_mesh.current_mesh().vertex_number()}")

# actual normalization
prenormalized_mesh = config.ml.load_mesh(middle_path + '\\' + new_object_path, open3d=True)
split = new_object_path.split("\\")
name = split[-1]
norm.run_one_mesh(prenormalized_mesh, [middle_path, clas, name], new_path)

end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")

if (show):
    # Load mesh
    mesh1 = config.ml.load_mesh(new_path + '\\' + new_object_path, open3d=True)
    mesh2 = config.ml.load_mesh(original_mesh_path + '\\' + object_path, open3d=True)

    # Render mesh
    config.rd.set_render_mode(render_mode.MIXED)
    config.rd.set_background([1,1,1])
    #config.rd.set_mesh_color([1,0,0])
    config.rd.add_mesh(mesh1, new_path + '\\' + new_object_path)
    config.rd.add_mesh(mesh2.translate((1, 0, 0)), original_mesh_path + '\\' + object_path)
    config.rd.add_world_axis()
    #config.rd.take_screenshot("I\\Want\\Way\\Too\\Many\\Files\\test.png")
    config.rd.launch_renderer()