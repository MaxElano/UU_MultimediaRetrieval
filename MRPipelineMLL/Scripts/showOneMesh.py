import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import Utility.config as config
import open3d as o3d
import time
from renderer import RenderMode

# Setup
start = time.time()
config.initialize()
config.lg.set_to_print()
config.lg.log("Showing one mesh")
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error) # Disables enjoying warnings


# Actual code
mesh_path_1 = "Data\\NormalizedShapeDatabase\\Cellphone\\D00542.npz"
#mesh_path_1 = "Data\\OriginalShapeDatabase\\Cellphone\\D00542.obj"

# Load mesh
mesh1 = config.ml.load_mesh(mesh_path_1)
#mesh2 = config.ml.load_mesh(mesh_path_2)

# Render mesh
config.rd.set_render_mode(RenderMode.MIXED)
config.rd.set_background([1,1,1])
config.rd.set_mesh_color([0.4,0.4,0.4])
config.rd.add_mesh(mesh1, mesh_path_1)
config.rd.add_world_axis()
config.rd.launch_renderer()

# Finish
end = time.time()
duration = end-start
config.lg.log(f"All done in {int(duration / 60)} minutes!!!")