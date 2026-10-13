from renderer import render_mode
import config
import numpy as np
import open3d as o3d

config.initialize()

mesh_path_1 = "Data\\NormalizedShapeDatabase\\Quadruped\\m94.npz"
#mesh_path_2 = "Data\\NormalizedShapeDatabase\\Bed\\D00031.obj"

# Load mesh
#mesh1 = config.ml.load_mesh(mesh_path_1, open3d=True)
mesh1 = o3d.io.read_triangle_mesh(o3d.data.ArmadilloMesh().path)
#mesh2 = config.ml.load_mesh(mesh_path_2)

# Render mesh
config.rd.set_render_mode(render_mode.MIXED)
config.rd.set_background([1,1,1])
config.rd.set_mesh_color([1,0,0])
config.rd.add_mesh(mesh1, mesh_path_1)
#config.rd.add_mesh(mesh2, mesh_path_2)
config.rd.add_world_axis()
#config.rd.take_screenshot("I\\Want\\Way\\Too\\Many\\Files\\test.png")
config.rd.launch_renderer()