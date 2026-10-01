import open3d as o3d
import numpy as np
import os
import config
import time

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
        pass
    
    def normalize_all_meshes(self, path_to_database, new_folder_path, show_update_every = 0):
        #show_update_every = 0 equals no updates
        config.lg.log(f"Starting normalization process at location {path_to_database}")
        start = time.time()
        
        all_files = []
        for root, dirs, files in os.walk(path_to_database):
            for file in files:
                if file.endswith(".obj"):
                    all_files.append(os.path.join(root[27:], file))
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        
        number_of_files = len(all_files)
        config.lg.log(f"{number_of_files} objects found")

        for i in range(number_of_files):
            mesh = config.ml.load_mesh(path_to_database + '\\' + all_files[i])
            self.run_one_mesh(mesh, all_files[i], new_folder_path)
            if (i > 0):
                if (i % show_update_every == 0): #Can't be combined cuz python sucks
                    config.lg.log(f"{i} of {number_of_files} objects normalized: {int((i / number_of_files) * 100)}%")
                
        end = time.time()
        duration = end-start
        config.lg.log(f"Finished normalization of all {number_of_files} objects in {round(duration / 60, 2) } minutes")
        
    def run_one_mesh(self, mesh, object_path, new_folder_path):
        mesh_values = normalizerMeshValues(mesh)
        self.translate_to_barycenter(mesh_values)
        eigen_vectors = self.compute_principal_axes(mesh_values)
        self.align_to_world_frame(mesh_values, eigen_vectors)
        self.flip_test(mesh_values)
        self.scale_to_unit(mesh_values)
        self.save_mesh(mesh_values, object_path, new_folder_path)
        
    # Take average of all face centers, with face size scaling
    # TODO add step in report, show image with open3d centre sphere to show this one is better
    def translate_to_barycenter(self, mesh_values):        
        numerator = np.sum(mesh_values.weighted_face_centres, axis=0)
        barycenter = numerator / mesh_values.surface_area
        
        mesh_values.vertices -= barycenter
        mesh_values.face_centres -= barycenter
        mesh_values.weighted_face_centres -= (mesh_values.face_areas_reshaped * barycenter)
        
    # Could maybe be done with get_oriented_bounding_box(), but uncertain about results cuz of other open3d function results/methods
    # Using weighted face coords, we think this will partly resolve the dense point issue
    def compute_principal_axes(self, mesh_values): 
        xx = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 0, mesh_values.surface_area)
        xy = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 1, mesh_values.surface_area)
        xz = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 2, mesh_values.surface_area)
        yy = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 1, 1, mesh_values.surface_area)
        yz = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 1, 2, mesh_values.surface_area)
        zz = shapeNormalizer.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 2, 2, mesh_values.surface_area)
        covariance_matrix = np.asarray([[xx, xy, xz]
                                       ,[xy, yy, yz]
                                       ,[xz, yz, zz]])
        eigen_values, eigen_vectors = np.linalg.eig(covariance_matrix)
        
        return eigen_vectors
    
    def align_to_world_frame(self, mesh_values, eigen_vectors):
        # length of a on axis b (ab) = ||a|| cos (theta)
        # -> ab = a dot b(unit)
        # eigenvectors are already normalized
        # https://en.wikipedia.org/wiki/Dot_product
        
        mesh_values.vertices = np.dot(mesh_values.vertices, eigen_vectors)
        mesh_values.face_centres = np.dot(mesh_values.face_centres, eigen_vectors)
        mesh_values.weighted_face_centres = np.dot(mesh_values.weighted_face_centres, eigen_vectors)
        #Stop updating other mesh values, as we do not need them anymore (save some performance)
        #From here on other coords are incorrect (except for vertices)
        
    # Use both weighted and unweighted, otherwise the weights might explode the value
    def flip_test(self, mesh_values):                
        x = np.sum(np.sign(mesh_values.face_centres[:,0:1]) * (mesh_values.weighted_face_centres[:,0:1] * mesh_values.face_centres[:,0:1]), axis=0)
        y = np.sum(np.sign(mesh_values.face_centres[:,1:2]) * (mesh_values.weighted_face_centres[:,1:2] * mesh_values.face_centres[:,1:2]), axis=0)
        z = np.sum(np.sign(mesh_values.face_centres[:,2:3]) * (mesh_values.weighted_face_centres[:,2:3] * mesh_values.face_centres[:,2:3]), axis=0)

        mesh_values.vertices[:,0:1] *= np.sign(x)
        mesh_values.vertices[:,1:2] *= np.sign(y)
        mesh_values.vertices[:,2:3] *= np.sign(z)
        
    def scale_to_unit(self, mesh_values):
        max_bounds = np.max(mesh_values.vertices, axis=0)
        min_bounds = np.min(mesh_values.vertices, axis=0)
        max_diff = np.max(max_bounds - min_bounds)
        mesh_values.vertices *= (1/max_diff)
    
    def save_mesh(self, mesh_values, object_path, new_folder_path):
        total_path = new_folder_path + '\\' + object_path
        if not os.path.exists(new_folder_path + '\\' + object_path.split('\\')[0]):
            os.makedirs(new_folder_path + '\\' + object_path.split('\\')[0])
        if not os.path.isfile(total_path):
            with open(total_path, "w") as file:
                file.write("")
        else:
            with open(total_path, "w") as file:
                file.seek(0)
                file.truncate()
                
        new_mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(mesh_values.vertices), o3d.utility.Vector3iVector(mesh_values.triangles))
        new_mesh.compute_vertex_normals()
        o3d.io.write_triangle_mesh(total_path, new_mesh)
    
    
    # ==== UTIL ====
        
    def calculate_covariance(coords, weighted_face_centres, axis_idx_1, axis_idx_2, surface_area): 
        weighted_total = np.sum(coords[:, axis_idx_1 : axis_idx_1 + 1] * weighted_face_centres[:, axis_idx_2 : axis_idx_2 + 1]) # Use one weighted to only include face weight once
        total = weighted_total / surface_area
        variance = total / (coords.shape[0] - 1)
        return variance
    
config.initialize(skip_renderer=True)
sn = shapeNormalizer()
original_path = 'Data\\OriginalShapeDataBase'
new_path = 'Data\\NormalizedDatabase'
sn.normalize_all_meshes(original_path, new_path, show_update_every=100)