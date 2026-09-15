import open3d as o3d

class meshLoader():
    def __init__(self):
        pass

    #   Load the mesh with open3d
    def load_mesh(self, mesh_path):
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        mesh.compute_vertex_normals()
        return mesh