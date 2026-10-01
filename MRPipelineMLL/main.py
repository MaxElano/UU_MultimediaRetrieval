from renderer import render_mode
import config
import numpy as np

config.initialize()

mesh_path_1 = "Data\\NormalizedShapeDatabase\\Starship\\m1355.obj"
mesh_path_2 = "Data\\NormalizedShapeDatabase\\Bed\\D00031.obj"


# Load mesh
mesh1 = config.ml.load_mesh(mesh_path_1)
mesh2 = config.ml.load_mesh(mesh_path_2)

# Render mesh
config.rd.set_render_mode(render_mode.NORMAL)
config.rd.show_world_axis(True)
config.rd.add_mesh(mesh1, mesh_path_1)
config.rd.add_mesh(mesh2, mesh_path_2)
config.rd.launch_renderer()