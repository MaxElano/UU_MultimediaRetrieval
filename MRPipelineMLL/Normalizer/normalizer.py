import numpy as np
import Utility.config as config
import time
from Normalizer.resampler import ResamplerPyMeshLab
import Utility.utility as util
from Utility.imageGenerator import ImageGenerator 
import queue as q

# responsible for fixing holes and remeshing using pymeshlab
class PreNormalizer():
    ig = ImageGenerator()
    
    meshes_changed_by_holes = 0
    same_edges = 0
    crash = 0
    def __init__(self):
        self.resampler = ResamplerPyMeshLab()

    def process_all_meshes(self, path_to_database="Data\\OriginalShapeDatabase", path_to_new_database="Data\\PreprocessedShapeDatabase"):
        config.lg.log(f"Start fixing holes at location {path_to_database}")
        start = time.time()
        
        all_files = util.get_all_files(path_to_database)
        util.create_folder(path_to_new_database)
        pc = util.ProgressCounter(len(all_files), 500, "holes filled")

        for path in all_files:
            meshset = config.ml.load_mesh(util.get_path(path), pyMeshLab=True)
            self.run_one_mesh(meshset, path, path_to_new_database)
            pc.increment()

        end = time.time()
        duration = end-start
        config.lg.log(f"Remeshing done. Changed holes in {self.meshes_changed_by_holes}/{len(all_files)} objects. Did nothing in {self.same_edges}/{len(all_files)} objects. Crashed in {self.crash}/{len(all_files)} objects. Run time: {round(duration / 60, 2) } minutes")
     

    def run_one_mesh(self, meshset, path, new_path):
        location = f"Data\\Screenshots\\AllMeshes\\{path[1]}\\{path[2].split(".")[0]}"
        self.ig.generate_from_arrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "00_original") 
        self.fill_holes(meshset)
        self.ig.generate_from_arrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "01_holes_filled") 
        self.resampler.resample_one_mesh(meshset) 
        self.ig.generate_from_arrays(meshset.current_mesh().vertex_matrix(), meshset.current_mesh().face_matrix(), location, "02_resampled") 
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

class NormalizerMeshValues():
    def __init__(self, mesh):
        self.vertices = np.asarray(mesh.vertices)
        self.face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        self.surface_area =  np.sum(self.face_areas) # Can also be done with mesh.get_surface_area() but this should be more consistent with other values used
        self.triangles = np.asarray(mesh.triangles)
        self.face_centres = np.average(np.asarray(mesh.vertices)[self.triangles], axis=1)
        self.face_areas_reshaped = np.reshape(np.repeat(self.face_areas,3), (self.face_areas.size, 3))
        self.weighted_face_centres = self.face_areas_reshaped * self.face_centres


class ShapeNormalizerOpen3D():
    ig = ImageGenerator()
    
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
        pc = util.ProgressCounter(number_of_files, 500, "objects normalized")

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
        self.ig.generate_from_arrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "03_cleaned_up", show_face_normals=False) 
        
        self.orient_triangles(mesh, object_entry)
        self.ig.generate_from_arrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "04_oriented_faces", True) 
        
        mesh = self.translate_to_barycenter_mesh(mesh)
        self.ig.generate_from_arrays(np.asarray(mesh.vertices), np.asarray(mesh.triangles), location, "05_translated") 
        
        mesh_values = NormalizerMeshValues(mesh)
        eigen_vectors, _ = self.compute_principal_axes_simpler(mesh_values)
        self.align_to_world_frame(mesh_values, eigen_vectors)
        self.ig.generate_from_arrays(mesh_values.vertices, mesh_values.triangles, location, "06_aligned_world_axis") 
        
        self.flip_test(mesh_values)
        self.ig.generate_from_arrays(mesh_values.vertices, mesh_values.triangles, location, "07_flipped")
        
        self.scale_to_unit(mesh_values)
        self.ig.generate_from_arrays(mesh_values.vertices, mesh_values.triangles, location, "08_scaled")
        
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

        mesh_values.vertices[:,0:1] *= np.sign(xs)
        mesh_values.vertices[:,1:2] *= np.sign(ys)
        mesh_values.vertices[:,2:3] *= np.sign(zs)
        
    def scale_to_unit(self, mesh_values):
        max_bounds = np.max(mesh_values.vertices, axis=0)
        min_bounds = np.min(mesh_values.vertices, axis=0)
        max_diff = np.max(max_bounds - min_bounds)
        mesh_values.vertices *= (1/max_diff)
    
    def save_mesh(self, mesh_values, object_entry, path_to_new_database):
        total_path = path_to_new_database + '\\' + '\\'.join(object_entry[1:])
        config.ml.save_mesh_numpy(total_path, mesh_vertices=mesh_values.vertices, mesh_triangles=mesh_values.triangles)

#TODO WIP by Max in free-time
class CustomNormalizer():   
    nr_contains_holes = 0
    nr_holes_fully_fixed = 0
    nr_face_reoriented = 0
    nr_face_orient_impossible = 0
    nr_resampled = 0
    nr_flipped = 0 
    def __init__(self, capture_screenshots = False, screenshot_location = "Data\\Screenshots\\AllMeshes"):
        self.screenshot_location = screenshot_location
        self.capture_screenshots = capture_screenshots
        if capture_screenshots:
            self.image_generator = ImageGenerator()
    
    def normalize_all_meshes(self, source_database_path, target_database_path, progress_update_rate = 250):
        config.lg.log(f"Starting Custom Normalization process with database {source_database_path} to {target_database_path}. Progress update rate: {progress_update_rate}")
        start = time.time()
        
        all_files = util.get_all_files(source_database_path)
        util.create_folder(target_database_path)
        number_of_files = len(all_files)
        config.lg.log(f"{number_of_files} files found")
        pc = util.ProgressCounter(number_of_files, progress_update_rate, "objects normalized")

        for file_data in all_files:
            meshset = config.ml.load_mesh(util.get_path(file_data), pyMeshLab=True) #Done using library
            self.normalize_one_mesh(meshset, util.get_path(file_data), target_database_path)
            pc.increment()
                
        end = time.time()
        duration = end-start
        config.lg.log(f"{number_of_files - self.not_triangle_orientable} of objects were triangle orientable")
        config.lg.log(f"Finished normalization of all {number_of_files} objects in {round(duration / 60, 2) } minutes")
    
    # TODO implement this for neater normalizer
    def run_action_with_screenshot(self, action, vertices, triangles, location, title, show_face_normals = False):
        self.image_generator.generate_from_arrays(vertices, triangles, location, title, show_face_normals=show_face_normals) 
    
    def normalize_one_mesh(self, vertices, triangles, file_data, target_database_path):
        #Create custom class
        mesh_values = CustomMeshValues(vertices, triangles, file_data)
        if self.capture_screenshots:
            self.image_generator.generate_from_arrays(mesh_values.vertices, mesh_values.faces, self.screenshot_location + "\\" + util.get_path(mesh_values.file_data[1:]), "00_Start") 
        
        #Fill holes
        
        #Resample
        
        #Orient triangles
        
        
        #Translate to barycenter
        self.translate_to_barycenter(mesh_values)
        
        #Align to world axes
        self.align_to_world_axis(mesh_values)
        
        #Flip test
        self.flip_test(mesh_values)
        
        #Scale to unit
        self.scale_to_unit_cube(mesh_values)
        
        #Save
        self.save_mesh_values(mesh_values, target_database_path)
        
        pass
    
    def orient_faces(mesh_values):
        queue = q.Queue()
        
        pass
    
    def translate_to_barycenter(self, mesh_values):
        barycenter = np.sum(mesh_values.weighted_face_centres, axis=0) / mesh_values.surface_area
        mesh_values.vertices = mesh_values.vertices - barycenter
        
        #TODO translate all points or regenerate
        
        if self.capture_screenshots:
            self.image_generator.generate_from_arrays(mesh_values.vertices, mesh_values.faces, self.screenshot_location + "\\" + util.get_path(mesh_values.file_data[1:]), "05_Translated") 
    
    def align_to_world_axis(self, mesh_values):
        # Code from example on Teams
        cov = np.cov(mesh_values.weighted_face_centers.transpose())
        # The eigen vectors are the columns of the returned 2d-array
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        
        # Order the eigenvectors according to the magnitude of their corresponding eigen value (from largest to smallest)
        eigencombined = [(eigenvalues[i], eigenvectors[:, i]) for i in range(3)]
        eigencombined.sort(key=lambda x:x[0], reverse=True)
        eigenvectors = [item[1] for item in eigencombined]
        eigenvalues = [item[0] for item in eigencombined]
        
        # Replace the minor eigen vector with cross product of major and medium (to enforce right-handed reference frame)
        eigenvectors.pop(2)
        eigenvectors.append(np.cross(eigenvectors[0], eigenvectors[1]))

        # https://en.wikipedia.org/wiki/Dot_product
        mesh_values.vertices = np.array([[np.dot(v,eigenvectors[0]), np.dot(v,eigenvectors[1]), np.dot(v,eigenvectors[2])] for v in mesh_values.vertices])

        #TODO change all points and normals OR regenerate (for now regenerate)
        
        if self.capture_screenshots:
            self.image_generator.generate_from_arrays(mesh_values.vertices, mesh_values.faces, self.screenshot_location + "\\" + util.get_path(mesh_values.file_data[1:]), "06_Aligned") 
                             
    def flip_test(self, mesh_values):
        x = np.sum(np.sign(mesh_values.weighted_face_centers[:,0:1]) * (mesh_values.weighted_face_centers[:,0:1] * mesh_values.face_centers[:,0:1]), axis=0)
        y = np.sum(np.sign(mesh_values.weighted_face_centers[:,1:2]) * (mesh_values.weighted_face_centers[:,1:2] * mesh_values.face_centers[:,1:2]), axis=0)
        z = np.sum(np.sign(mesh_values.weighted_face_centers[:,2:3]) * (mesh_values.weighted_face_centers[:,2:3] * mesh_values.face_centers[:,2:3]), axis=0)

        if (np.sign(x) == 0 or np.sign(y) == 0 or np.sign(z) == 0):
            config.lg.log(f"This motherFUCKER ({util.get_path(mesh_values.file_data)}) actually returns 0 in flip test")
            
        xs = np.sign(x) if np.sign(x) != 0 else 1
        ys = np.sign(y) if np.sign(y) != 0 else 1
        zs = np.sign(z) if np.sign(z) != 0 else 1

        if xs == -1 or ys == -1 or zs == -1:
            self.nr_flipped += 1

        mesh_values.vertices = mesh_values.vertices * np.asarray([np.sign(xs), np.sign(ys), np.sign(zs)])
        #TODO flip all values points and normals or regenerate
        
        if self.capture_screenshots:
            self.image_generator.generate_from_arrays(mesh_values.vertices, mesh_values.faces, self.screenshot_location + "\\" + util.get_path(mesh_values.file_data[1:]), "07_Flipped") 
                      
    def scale_to_unit_cube(self, mesh_values):
        max_bounds = np.max(mesh_values.vertices, axis=0)
        min_bounds = np.min(mesh_values.vertices, axis=0)
        scaling = 1/np.max(max_bounds - min_bounds)
        mesh_values.vertices = mesh_values.vertices * scaling
        #TODO scale all points or regenerate
        
        if self.capture_screenshots:
            self.image_generator.generate_from_arrays(mesh_values.vertices, mesh_values.faces, self.screenshot_location + "\\" + util.get_path(mesh_values.file_data[1:]), "08_Scaled") 
              
    def save_mesh_values(self, mesh_values, target_database_path):
        total_path = target_database_path + '\\' + '\\'.join(mesh_values.file_data[1:])
        config.ml.save_mesh_numpy(total_path, mesh_vertices=mesh_values.vertices, mesh_triangles=mesh_values.triangles)
    
    
class CustomMeshValues():
    def __init__(self, vertices, faces, file_data):
        self._vertices = vertices
        self._faces = faces
        self._file_data = file_data
    
    @property
    def file_data(self):
        return self._file_data
    
    @property
    def vertices(self):
        return self._vertices
    
    @vertices.setter
    def vertices(self, array):
        if not isinstance(array, np.ndarray):
            raise(ValueError, "Vertices must by of type np.ndarray")
        if len(array.shape) != 2:
            raise(ValueError, "Vertices array wrong dimensionality")
        if len(array.shape[1]) != 3:
            raise(ValueError, "Vertex must have 3 coordinates")
        self._vertices = array
    
    @property
    def edges(self):
        if not self._edges:
            self.generate_edges()
        return self._edges
            
    @property
    def faces(self):
        return self._faces

    @faces.setter
    def faces(self, array):
        if not isinstance(array, np.ndarray):
            raise(ValueError, "Faces must by of type np.ndarray")
        if len(array.shape) != 2:
            raise(ValueError, "Faces array wrong dimensionality")
        if len(array.shape[1]) != 3:
            raise(ValueError, "Face must have 3 vertex indices")
        self._faces = array
    
    @property
    def face_normals(self):
        if not self._face_normals:
            self.generate_face_normals()
        return self._face_normals()
    
    @property
    def face_normals_normalized(self):
        if not self._face_normals_normalized:
            self.generate_face_normals()
        return self._face_normals_normalized
    
    @property
    def face_areas(self):
        if not self._face_areas:
            self.generate_face_areas()
        return self._face_areas
    
    @property
    def face_centers(self):
        if not self._face_centers:
            self.generate_face_centers()
        return self._face_centres

    @property
    def weighted_face_centers(self):
        if not self._weighted_face_centers:
            self.generate_weighted_face_centers()
        return self._weighted_face_centers()
    
    @property
    def surface_area(self):
        if not self._surface_area:
            self.generate_surface_area()
        return self._surface_area
    
    def normalize_v3(self, arr):
        lens = np.sqrt(arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2 )
        arr[:,0] /= lens     
        arr[:,1] /= lens     
        arr[:,2] /= lens                     
        return arr
    
    def generate_edges(self):
        e1 = self._faces[:,:1]
        e2 = self._faces[:,1:3]
        e3 = self._faces[:]
        self._edges = self._faces
    
    def generate_face_normals(self):
        tris = self._vertices[self._faces]
        f = np.cross(tris[::,1 ] - tris[::,0], tris[::,2 ] - tris[::,0])
        self._face_normals = f
        self._face_normals_normalized = self.normalize_v3(f)
    
    def generate_face_areas(self):
        if not self._face_normals_normalized:
            self.generate_face_normals()
        self._face_areas = np.linalg.norm(self._face_normals_normalized, axis=1) / 2
    
    def generate_face_centers(self):
        self._face_centres = np.average(self._vertices[self._faces], axis=1)

    def generate_weighted_face_centers(self):
        if not self._face_areas:
            self.generate_face_areas()
        if not self._face_centres:
            self.generate_face_centers()
        face_areas_reshaped = np.reshape(np.repeat(self._face_areas,3), (self._face_areas.size, 3))
        self._weighted_face_centers = face_areas_reshaped * self._face_centres
    
    def generate_surface_area(self):
        if not self._face_areas:
            self.generate_face_areas()
        self._surface_area = np.sum(self._face_areas)