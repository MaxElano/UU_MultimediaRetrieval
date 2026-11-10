import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from Normalizer.normalizer import PreNormalizer, ShapeNormalizerOpen3D
from Normalizer.normalizeChecker import NormalizeChecker
import Utility.config as config
import open3d as o3d
import time
import pymeshlab as pml


def save_meshset(meshset, name, path_to_new_database):
    total_path = path_to_new_database + '\\' + name + '.obj'
    meshset.save_current_mesh(total_path)

config.initialize(skip_renderer=True)

original_path = "Data\\OriginalShapeDatabase\\HumanHead\\D00072.obj"
original_mesh = config.ml.load_mesh(original_path, pyMeshLab=True)

preNormalizer = PreNormalizer()
preNormalizer.fill_holes(original_mesh)

save_meshset(original_mesh, "D00072_Filled", "Data\\TempFiles\\NormalizerSteps")


