from renderer import renderer, render_mode
from meshLoader import meshLoader
from logger import logger
import numpy as np

mesh_path_1 = "Data\\OriginalShapeDatabase\\Starship\\m1355.obj"
mesh_path_2 = "Data\\OriginalShapeDatabase\\Bed\\D00031.obj"


# Initialize all objects
r = renderer(background_color=[1,1,1])
ml = meshLoader()
lg = logger()

# Load mesh
mesh1 = ml.load_mesh(mesh_path_1)
mesh2 = ml.load_mesh(mesh_path_2)

# Render mesh
r.set_render_mode(render_mode.NORMAL)
r.show_world_axis(True)
r.add_mesh(mesh1)
r.add_mesh(mesh2)
r.launch_renderer()