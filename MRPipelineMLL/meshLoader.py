import open3d as o3d
import numpy as np
import config
import os
import random

'''
    The meshLoader will convert all path strings to actual meshes and return these
'''

class meshLoader():
    def __init__(self):
        pass

    def load_meshes(self, mesh_paths: list[str]) -> list[o3d.geometry.Geometry]:
        mesh_list = np.vectorize(self.load_mesh)(mesh_paths)
        return mesh_list

    def load_mesh(self, mesh_path: str) -> o3d.geometry.Geometry:
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals(normalized=False) # mind NOT normalized, to calculate face area
        return mesh

    def load_random_mesh(self) -> o3d.geometry.Geometry:
        all_files = []
        
        for root, dirs, files in os.walk(config.random_mesh_default_folder):
            for file in files:
                if file.endswith(".obj"):
                    all_files.append(os.path.join(root, file))
        
        files = [f for f in all_files if f.endswith(".obj")]
        random_file=random.choice(files)
        mesh = config.ml.load_mesh(random_file)
        return mesh, random_file
