import open3d as o3d
import numpy as np
import os
import config
import time
from resampler import resampler_pymeshlab
import utility as util
import pymeshlab as pml
from imageGenerator import imageGenerator 

# responsible for fixing holes and remeshing using pymeshlab
class preNormalizer():
    ig = imageGenerator()
    
    meshes_changed_by_holes = 0
    same_edges = 0
    crash = 0
    def __init__(self):
        self.resampler = resampler_pymeshlab()

    def process_all_meshes(self, path_to_database="Data\\OriginalShapeDatabase", path_to_new_database="Data\\PreprocessedShapeDatabase"):
        config.lg.log(f"Start fixing holes at location {path_to_database}")
        start = time.time()
        
        all_files = util.get_all_files(path_to_database)
        util.create_folder(path_to_new_database)
        pc = util.progress_printer(len(all_files), 500, "holes filled")

        for path in all_files:
            meshset = config.ml.load_mesh(util.get_path(path), pyMeshLab=True)
            self.run_one_mesh(meshset, path, path_to_new_database)
            pc.increment()

        end = time.time()
        duration = end-start
        config.lg.log(f"Remeshing done. Changed holes in {self.meshes_changed_by_holes}/{len(all_files)} objects. Did nothing in {self.same_edges}/{len(all_files)} objects. Crashed in {self.crash}/{len(all_files)} objects. Run time: {round(duration / 60, 2) } minutes")
     

    def run_one_mesh(self, meshset, path, new_path):
        location = f"Data\\Screenshots\\AllMeshes\\{path[1]}\\{path[2].split(".")[0]}"
        self.ig.generateFromArrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "00_original") 
        self.fill_holes(meshset)
        self.ig.generateFromArrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "01_holes_filled") 
        self.resampler.resample_one_mesh(meshset) 
        self.ig.generateFromArrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "02_resampled") 
        self.save_mesh(meshset, path, new_path)  

    def fill_holes(self, meshset):
        #meshset.meshing_repair_non_manifold_edges(method='Remove Faces') COULD STILL BE AN OPTION AT SOME POINT
        meshset.meshing_repair_non_manifold_vertices()
        
        # Mesh must have edge manifoldness
        prevcount = meshset.current_mesh().edge_number() 
        try:
            meshset.meshing_close_holes(maxholesize=100, newfaceselected=False, refinehole=False) #Maybe change parameter values?
        except:
            self.crash += 1
        aftercount = meshset.current_mesh().edge_number() 
        
        if (prevcount != aftercount):
            self.meshes_changed_by_holes += 1
        if (prevcount == aftercount):
            self.same_edges += 1


    def save_mesh(self, meshset, object_entry, path_to_new_database):
        total_path = path_to_new_database + '\\' + '\\'.join(object_entry[1:])
        config.ml.save_mesh_numpy(total_path, mesh_vertices=meshset.current_mesh().vertex_matrix(), mesh_triangles=meshset.current_mesh().face_matrix())

class normalizerMeshValues():
    def __init__(self, mesh):
        self.vertices = np.asarray(mesh.vertices)
        self.face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        self.surface_area =  np.sum(self.face_areas) # Can also be done with mesh.get_surface_area() but this should be more consistent with other values used
        self.triangles = np.asarray(mesh.triangles)
        self.face_centres = np.average(np.asarray(mesh.vertices)[self.triangles], axis=1)
        self.face_areas_reshaped = np.reshape(np.repeat(self.face_areas,3), (self.face_areas.size, 3))
        self.weighted_face_centres = self.face_areas_reshaped * self.face_centres


class shapeNormalizerOpen3D():
    ig = imageGenerator()
    
    def __init__(self):
        self.not_triangle_orientable = 0
        pass
    
    def normalize_all_meshes(self, path_to_database, path_to_new_database):
        #show_update_every = 0 equals no updates
        config.lg.log(f"Starting normalization process at location {path_to_database}")
        start = time.time()
        
        all_files = util.get_all_files(path_to_database)
        util.create_folder(path_to_new_database)
        number_of_files = len(all_files)
        config.lg.log(f"{number_of_files} objects found")
        pc = util.progress_printer(number_of_files, 500, "objects normalized")

        for file in all_files:
            mesh = config.ml.load_mesh(util.get_path(file), open3d=True)
            self.run_one_mesh(mesh, file, path_to_new_database)
            pc.increment()
                
        end = time.time()
        duration = end-start
        config.lg.log(f"{number_of_files - self.not_triangle_orientable} of objects were triangle orientable")
        config.lg.log(f"Finished normalization of all {number_of_files} objects in {round(duration / 60, 2) } minutes")
        
    def run_one_mesh(self, mesh, object_entry, path_to_new_database):
        location = f"Data\\Screenshots\\AllMeshes\\{object_entry[1]}\\{object_entry[2].split(".")[0]}"
        #mesh = self.general_cleanup(mesh)
        self.ig.generateFromArrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "03_cleaned_up", show_face_normals=True) 
        
        self.orient_triangles(mesh, object_entry)
        self.ig.generateFromArrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "04_oriented_faces", True) 
        
        mesh = self.translate_to_barycenter_mesh(mesh)
        self.ig.generateFromArrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "05_translated") 
        
        mesh_values = normalizerMeshValues(mesh)
        eigen_vectors, _ = self.compute_principal_axes_simpler(mesh_values)
        self.align_to_world_frame(mesh_values, eigen_vectors)
        self.ig.generateFromArrays(mesh_values.vertices, mesh_values.triangles, location, "06_aligned_world_axis") 
        
        self.flip_test(mesh_values)
        self.ig.generateFromArrays(mesh_values.vertices, mesh_values.triangles, location, "07_flipped")
        
        self.scale_to_unit(mesh_values)
        self.ig.generateFromArrays(mesh_values.vertices, mesh_values.triangles, location, "08_scaled")
        
        self.save_mesh(mesh_values, object_entry, path_to_new_database)

    def general_cleanup(self, mesh):
        mesh = mesh.remove_duplicated_triangles()
        mesh = mesh.remove_degenerate_triangles()
        mesh = mesh.remove_duplicated_vertices()
        mesh = mesh.remove_non_manifold_edges()
        mesh = mesh.remove_unreferenced_vertices()
        return mesh

    def orient_triangles(self, mesh, path):
        #try:
        if not mesh.orient_triangles():
            self.not_triangle_orientable += 1
        #except:
        #    config.lg.log(f"Not Orientable {'\\'.join(path[1:])} - Orientable: {mesh.is_orientable()} - Watertight: {mesh.is_watertight()} - Self intersect: {mesh.is_self_intersecting()} - Edge manifold: {mesh.is_edge_manifold()} - Vertex manifold: {mesh.is_vertex_manifold()}")

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
        
        mesh_values.vertices = np.array([[np.dot(v,eigen_vectors[0]), np.dot(v,eigen_vectors[1]), np.dot(v,eigen_vectors[2])] for v in mesh_values.vertices])
        mesh_values.face_centres = np.array([[np.dot(v,eigen_vectors[0]), np.dot(v,eigen_vectors[1]), np.dot(v,eigen_vectors[2])] for v in mesh_values.face_centres])
        mesh_values.weighted_face_centres = np.array([[np.dot(v,eigen_vectors[0]), np.dot(v,eigen_vectors[1]), np.dot(v,eigen_vectors[2])] for v in mesh_values.weighted_face_centres])

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
        config.ml.save_mesh_numpy(total_path, mesh_vertices=mesh_values.vertices, mesh_triangles=mesh_values.triangles)

og_path = "Data\\OriginalShapeDatabase"
middle_path = "Data\\PreprocessedShapeDatabase"
new_path = "Data\\NormalizedShapeDatabase"

config.initialize(skip_renderer=False)
config.lg.set_to_write()

#pn = preNormalizer()
#pn.process_all_meshes(og_path, middle_path)

sn = shapeNormalizerOpen3D()
sn.normalize_all_meshes(middle_path, new_path)