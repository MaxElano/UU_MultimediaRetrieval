from renderer import renderer, render_mode
from meshLoader import meshLoader
from logger import logger
import numpy as np

mesh_path = "Data\\OriginalShapeDatabase\\Starship\\m1355.obj"

# Initialize all objects
r = renderer()
ml = meshLoader()
lg = logger()

# Load mesh
mesh = ml.load_mesh(mesh_path)

# Render mesh
r.visualize_mesh(mesh, render_mode.WIREFRAME, show_world_axis=True)