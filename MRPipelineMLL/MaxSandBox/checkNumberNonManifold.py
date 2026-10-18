import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from shapeNormalizer import shapeNormalizerPyMeshLab
import config
import open3d as o3d
import time
from renderer import render_mode
import utility as util

original_mesh_path = "Data\\OriginalShapeDatabase"
number_of_fucked = 0


config.initialize(skip_renderer=True)
config.lg.log(f"Starting counting number of non manifold meshes {original_mesh_path}")
start = time.time()

all_files = util.get_all_files(original_mesh_path)
number_of_files = len(all_files)
config.lg.log(f"{number_of_files} objects found")
pc = util.progress_printer(number_of_files, 250, "objects checked")

for i in range(number_of_files):
    meshset = config.ml.load_mesh(util.get_path(all_files[i]), pyMeshLab=True)
    meshset.compute_selection_by_non_manifold_edges_per_face()
    number = meshset.current_mesh().selected_vertex_number()
    if (number > 0):
        number_of_fucked += 1
    pc.increment()
        
end = time.time()
duration = end-start
config.lg.log(f"{number_of_fucked} meshes are fucked from the total {number_of_files} objects. Calculated in {round(duration / 60, 2) } minutes")