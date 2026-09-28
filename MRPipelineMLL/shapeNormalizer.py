import open3d as o3d
import numpy as np

# The best order is translate -> pca -> re-align -> flip -> scale -> remesh
# Remeshing could be done at the start for big meshes, to simplify them first and send less data through pipeline
# And remesh at end for small meshes, to refine them at the end to have less data through pipeline
# Cleanest standard is remesh at end
# TODO: Can be optimized to pass along arrays like face areas and positions, as not to recalculate them each step
class shapeNormalizer():
    def __init__(self):
        pass
    
    def run_one_mesh(self, mesh, path):
        
        mesh = self.translate_to_barycenter(mesh)
        eigen_vectors = self.compute_principal_axes(mesh)
        mesh = self.align_to_world_frame(mesh, eigen_vectors)
        mesh = self.flip_test(mesh)
        mesh = self.scale_to_unit(mesh)
        return mesh #Temporary
        #self.save_mesh(mesh, path)
        
    # Take average of all face centers, with face size scaling
    # TODO add step in report, show image with open3d centre sphere to show this one is better
    def translate_to_barycenter(self, mesh):
        weighted_face_centres = shapeNormalizer.calculate_weighted_face_centres(mesh)
        
        numerator = np.sum(weighted_face_centres, axis=0)
        denominator = shapeNormalizer.calculate_custom_surface_area(mesh)
        barycenter = numerator / denominator
        
        mesh = mesh.translate(translation=-barycenter, relative=True)
        return mesh
    
    # Could maybe be done with get_oriented_bounding_box(), but uncertain about results cuz of other open3d function results/methods
    # Using weighted face coords, we think this will partly resolve the dense point issue
    def compute_principal_axes(self, mesh): 
        face_centers = shapeNormalizer.calculate_face_centres(mesh)
        face_weights = shapeNormalizer.calculate_face_areas(mesh)
        xx = shapeNormalizer.calculate_covariance(face_centers, face_weights, 0, 0)
        xy = shapeNormalizer.calculate_covariance(face_centers, face_weights, 0, 1)
        xz = shapeNormalizer.calculate_covariance(face_centers, face_weights, 0, 2)
        yy = shapeNormalizer.calculate_covariance(face_centers, face_weights, 1, 1)
        yz = shapeNormalizer.calculate_covariance(face_centers, face_weights, 1, 2)
        zz = shapeNormalizer.calculate_covariance(face_centers, face_weights, 2, 2)
        covariance_matrix = np.asarray([[xx, xy, xz]
                                       ,[xy, yy, yz]
                                       ,[xz, yz, zz]])
        eigen_values, eigen_vectors = np.linalg.eig(covariance_matrix)
        
        return eigen_vectors
    
    def align_to_world_frame(self, mesh, eigen_vectors):
        # length of a on axis b (ab) = ||a|| cos (theta)
        # -> ab = a dot b(unit)
        # eigenvectors are already normalized
        # https://en.wikipedia.org/wiki/Dot_product
        
        vertices = np.asarray(mesh.vertices)
        new_vertices = np.dot(vertices, eigen_vectors)
        mesh.vertices = new_vertices
        
        #TODO align the mesh to the correct world_frame using pca
        return mesh
    
    def flip_test(self, mesh):
        weighted_face_centres = shapeNormalizer.calculate_weighted_face_centres(mesh)
                
        x = np.sum(np.sign(weighted_face_centres[:,0:1]) * (weighted_face_centres[:,0:1] ** 2), axis=0)
        y = np.sum(np.sign(weighted_face_centres[:,1:2]) * (weighted_face_centres[:,1:2] ** 2), axis=0)
        z = np.sum(np.sign(weighted_face_centres[:,2:3]) * (weighted_face_centres[:,2:3] ** 2), axis=0)

        rotation_matrix = np.diagflat([np.sign(x),np.sign(y),np.sign(z)])
        mesh = mesh.rotate(rotation_matrix)
        
        return mesh
    
    def scale_to_unit(self, mesh):
        max_bounds = mesh.get_max_bound()
        min_bounds = mesh.get_min_bound()
        max_diff = np.max(max_bounds - min_bounds)
        mesh = mesh.scale(1/max_diff, [0,0,0])
        return mesh
    
    def save_mesh(self, mesh, path):
        #TODO Save new mash to correct path
        pass
    
    
    # ==== UTIL ====
        
    def precollect_variables(mesh):
        vertices = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.faces)
        
    
    def calculate_face_areas(mesh):
        return np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
    
    # Can also be done with mesh.get_surface_area() but this should be more consistent with other values used
    def calculate_custom_surface_area(mesh):
        face_areas = shapeNormalizer.calculate_face_areas(mesh)
        return np.sum(face_areas)

    def calculate_face_centres(mesh):
        vertex_indices = np.asarray(mesh.triangles)
        return np.average(np.asarray(mesh.vertices)[vertex_indices], axis=1)
    
    def calculate_weighted_face_centres(mesh):
        face_areas = shapeNormalizer.calculate_face_areas(mesh)
        face_areas_reshaped = np.reshape(np.repeat(face_areas,3), (face_areas.size, 3))
        face_centres = shapeNormalizer.calculate_face_centres(mesh)
        return face_areas_reshaped * face_centres
  
    def calculate_covariance(coords, weights, axis_idx_1, axis_idx_2):
        weighted_total = np.sum(coords[:, axis_idx_1 : axis_idx_1 + 1] * coords[:, axis_idx_2 : axis_idx_2 + 1] * weights)
        total = weighted_total / np.sum(weights)
        variance = total / (coords.shape[0] - 1)
        return variance
    
        
        
import config
from renderer import render_mode

config.initialize()
mesh_after, path = config.ml.load_random_mesh()  

sn = shapeNormalizer()
mesh_after = sn.run_one_mesh(mesh_after, '')

# Render mesh
config.rd.set_render_mode(render_mode.NORMAL)
config.rd.show_world_axis(True)
config.rd.add_mesh(mesh_after, path)
centre = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.01)
sphere.paint_uniform_color(np.asarray([0,0,1]))
config.rd.add_mesh(centre, "Axis")
config.rd.add_mesh(sphere, "Center")
config.rd.launch_renderer()

