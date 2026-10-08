import open3d as o3d
import numpy as np
import os
import config
import time
from resampler import resampler
import utility as util

class normalizerMeshValues():
    def __init__(self, mesh):
        self.vertices = np.asarray(mesh.vertices)
        self.face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        self.surface_area =  np.sum(self.face_areas) # Can also be done with mesh.get_surface_area() but this should be more consistent with other values used
        self.triangles = np.asarray(mesh.triangles)
        self.face_centres = np.average(np.asarray(mesh.vertices)[self.triangles], axis=1)
        self.face_areas_reshaped = np.reshape(np.repeat(self.face_areas,3), (self.face_areas.size, 3))
        self.weighted_face_centres = self.face_areas_reshaped * self.face_centres

# The best order is translate -> pca -> re-align -> flip -> scale -> remesh
class shapeNormalizer():
    def __init__(self):
        self.resampler = resampler()
    
    def normalize_all_meshes(self, path_to_database, path_to_new_database, show_update_every = 0):
        #show_update_every = 0 equals no updates
        config.lg.log(f"Starting normalization process at location {path_to_database}")
        start = time.time()
        
        all_files = util.get_all_obj_files(path_to_database)
        util.create_folder(path_to_new_database)
        number_of_files = len(all_files)
        config.lg.log(f"{number_of_files} objects found")
        pc = util.progress_printer(number_of_files, show_update_every, "objects normalized")

        for i in range(number_of_files):
            mesh = config.ml.load_mesh(util.get_path(all_files[i]))
            self.run_one_mesh(mesh, all_files[i], path_to_new_database)
            pc.increment()
                
        end = time.time()
        duration = end-start
        config.lg.log(f"Finished normalization of all {number_of_files} objects in {round(duration / 60, 2) } minutes")
        
    def run_one_mesh(self, mesh, object_entry, path_to_new_database):
        #mesh_values = normalizerMeshValues(mesh)
        #self.translate_to_barycenter(mesh_values) Changed to mesh variant for easy fit with resampler
        mesh = self.translate_to_barycenter_mesh(mesh)
        mesh = self.resampler.resample_one_mesh(mesh)
        mesh_values = normalizerMeshValues(mesh)
        #eigen_vectors = self.compute_principal_axes(mesh_values)
        eigen_vectors, _ = self.compute_principal_axes_simpler(mesh_values)
        self.align_to_world_frame(mesh_values, eigen_vectors)
        self.flip_test(mesh_values)
        self.scale_to_unit(mesh_values)
        self.save_mesh(mesh_values, object_entry, path_to_new_database)

    def translate_to_barycenter_mesh(self, mesh):
        face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        face_centres = np.average(np.asarray(mesh.vertices)[mesh.triangles], axis=1)
        face_areas_reshaped = np.reshape(np.repeat(face_areas,3), (face_areas.size, 3))
        weighted_face_centres = face_areas_reshaped * face_centres
        numerator = np.sum(weighted_face_centres, axis=0)
        
        surface_area =  np.sum(face_areas)
        barycenter = numerator / surface_area

        mesh = mesh.translate(-barycenter)
        return mesh
    
    def compute_principal_axes_simpler(self, mesh_values):
        # Code from example on Teams
        cov = np.cov(mesh_values.weighted_face_centres.transpose())

        # Compute eigen vectors and eigen values of covariance matrix
        # The eigen vectors are the columns of the returned 2d-array
        eigenvalues, eigenvectors = np.linalg.eig(cov)

        # Order the eigenvectors according to the magnitude of their corresponding eigen value
        # (from largest to smallest)
        eigencombined = [(eigenvalues[i], eigenvectors[:, i]) for i in range(3)]
        eigencombined.sort(key=lambda x:x[0], reverse=True)
        eigenvectors = [item[1] for item in eigencombined]
        eigenvalues = [item[0] for item in eigencombined]

        # Replace the minor eigen vector with cross product of major and medium (to enforce right-handed reference frame)
        eigenvectors.pop(2)
        eigenvectors.append(np.cross(eigenvectors[0], eigenvectors[1]))

        return eigenvectors, eigenvalues
    
    def align_to_world_frame(self, mesh_values, eigen_vectors):
        # https://en.wikipedia.org/wiki/Dot_product
        
        mesh_values.vertices = np.dot(mesh_values.vertices, eigen_vectors)
        mesh_values.face_centres = np.dot(mesh_values.face_centres, eigen_vectors)
        mesh_values.weighted_face_centres = np.dot(mesh_values.weighted_face_centres, eigen_vectors)
        #Stop updating other mesh values, as we do not need them anymore (save some performance)

    # Use both weighted and unweighted, otherwise the weights might explode the value
    def flip_test(self, mesh_values):                
        x = np.sum(np.sign(mesh_values.face_centres[:,0:1]) * (mesh_values.weighted_face_centres[:,0:1] * mesh_values.face_centres[:,0:1]), axis=0)
        y = np.sum(np.sign(mesh_values.face_centres[:,1:2]) * (mesh_values.weighted_face_centres[:,1:2] * mesh_values.face_centres[:,1:2]), axis=0)
        z = np.sum(np.sign(mesh_values.face_centres[:,2:3]) * (mesh_values.weighted_face_centres[:,2:3] * mesh_values.face_centres[:,2:3]), axis=0)

        if (np.sign(x) == 0 or np.sign(y) == 0 or np.sign(z) == 0):
            config.lg.log("This motherFUCKER actually returns 0 in flip test")
            
        xs = np.sign(x) if np.sign(x) != 0 else 1
        ys = np.sign(y) if np.sign(y) != 0 else 1
        zs = np.sign(z) if np.sign(z) != 0 else 1

        mesh_values.vertices[:,0:1] *= np.sign(x)
        mesh_values.vertices[:,1:2] *= np.sign(y)
        mesh_values.vertices[:,2:3] *= np.sign(z)
        
    def scale_to_unit(self, mesh_values):
        max_bounds = np.max(mesh_values.vertices, axis=0)
        min_bounds = np.min(mesh_values.vertices, axis=0)
        max_diff = np.max(max_bounds - min_bounds)
        mesh_values.vertices *= (1/max_diff)
    
    def save_mesh(self, mesh_values, object_entry, path_to_new_database):
        total_path = path_to_new_database + '\\' + '\\'.join(object_entry[1:])
        class_path = path_to_new_database + '\\' + object_entry[1]
        util.create_folder(class_path)
        total_path = total_path.removesuffix(".obj")
        util.empty_file(total_path)
        np.savez(total_path, vertices=mesh_values.vertices, triangles=mesh_values.triangles)
        # new_mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(mesh_values.vertices), o3d.utility.Vector3iVector(mesh_values.triangles))
        # new_mesh.triangle_normals = o3d.utility.Vector3dVector([])
        # new_mesh.compute_vertex_normals() #This line solves the duplicate vertices issue, without this loading new mesh has less vertices
        # o3d.io.write_triangle_mesh(total_path, new_mesh)
    
    
    # ==== UTIL ====
        
    def calculate_covariance(coords, weighted_face_centres, axis_idx_1, axis_idx_2, surface_area): 
        weighted_total = np.sum(coords[:, axis_idx_1 : axis_idx_1 + 1] * weighted_face_centres[:, axis_idx_2 : axis_idx_2 + 1]) # Use one weighted to only include face weight once
        total = weighted_total / surface_area
        variance = total / (coords.shape[0] - 1)
        return variance
    
# config.initialize(skip_renderer=True)
# sn = shapeNormalizer()
# original_path = 'Data\\OriginalShapeDataBase'
# new_path = 'Data\\NormalizedShapeDatabase'
# sn.normalize_all_meshes(original_path, new_path, show_update_every=100)