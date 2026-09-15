import open3d as o3d
import numpy as np

class meshLoader():
    def __init__(self):
        pass

    def load_meshes(self, mesh_paths: list[str]) -> list[o3d.geometry.Geometry]:
        mesh_list = np.vectorize(self.load_mesh)(mesh_paths)
        return mesh_list

    def load_mesh(self, mesh_path: str) -> o3d.geometry.Geometry:
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        mesh.compute_vertex_normals()
        return mesh