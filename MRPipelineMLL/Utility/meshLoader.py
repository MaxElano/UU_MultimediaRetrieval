import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import open3d as o3d
import numpy as np
import Utility.config as config
import random
import Utility.utility as util
import pymeshlab as pml

'''
    The meshLoader will convert all path strings to actual meshes and return these
'''

class MeshLoader():
    def __init__(self):
        pass

    def load_meshes(self, mesh_paths: list[str]) -> list[o3d.geometry.Geometry]:
        mesh_list = np.vectorize(self.load_mesh)(mesh_paths)
        return mesh_list

    def load_mesh(self, mesh_path: str, open3d=False, pyMeshLab=False) -> o3d.geometry.Geometry:
        if (mesh_path.endswith(".obj")):
            if (open3d):
                return self.load_open3d(mesh_path)
            elif (pyMeshLab):
                return self.load_pymeshlab(mesh_path)
        elif (mesh_path.endswith(".npz")):
            return self.load_numpy(mesh_path)
        
        config.lg.log("Invalid file format to load")
        return
    
    def load_open3d(self, mesh_path):
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals(normalized=False) # mind NOT normalized, to calculate face area
        return mesh

    def load_pymeshlab(self, mesh_path):
        meshset = pml.MeshSet()
        meshset.load_new_mesh(mesh_path)
        meshset.compute_scalar_by_aspect_ratio_per_face(metric='Area')
        meshset.compute_new_custom_point_attribute_per_face(name='center', x_expr='(x0+x1+x2)/3', y_expr='(y0+y1+y2)/3', z_expr='(z0+z1+z2)/3')
        meshset.compute_new_custom_point_attribute_per_face(name='weighted_center', x_expr='center_x*fq', y_expr='center_y*fq', z_expr='center_z*fq')        
        return meshset

    def load_numpy(self, mesh_path):
        vertices = []
        triangles = []
        file = util.load_numpy_file(mesh_path)
        vertices = file["vertices"]
        triangles = file["triangles"]
        new_mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(vertices), o3d.utility.Vector3iVector(triangles))
        new_mesh.compute_vertex_normals() #This line solves the duplicate vertices issue, without this loading new mesh has less vertices
        new_mesh.compute_triangle_normals(normalized=False) # mind NOT normalized, to calculate face area
        return new_mesh

    def load_random_mesh(self) -> o3d.geometry.Geometry:
        files = util.get_all_files(config.random_mesh_default_folder)
        random_file=random.choice(files)
        mesh = config.ml.load_mesh(util.get_path(random_file))
        return mesh, util.get_path(random_file)

    def save_mesh_numpy(self, total_path, mesh_vertices, mesh_triangles):
        util.save_numpy_file(total_path, vertices=mesh_vertices, triangles=mesh_triangles)