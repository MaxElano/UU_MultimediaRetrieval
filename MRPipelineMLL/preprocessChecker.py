import open3d as o3d
import numpy as np
import os
import config
import time
from matplotlib import pyplot as plt
import utility as util

#gejoinked
class normalizerMeshValues():
    def __init__(self, mesh):
        self.vertices = np.asarray(mesh.vertices)
        self.face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        self.surface_area =  np.sum(self.face_areas) # Can also be done with mesh.get_surface_area() but this should be more consistent with other values used
        self.triangles = np.asarray(mesh.triangles)
        self.face_centres = np.average(np.asarray(mesh.vertices)[self.triangles], axis=1)
        self.face_areas_reshaped = np.reshape(np.repeat(self.face_areas,3), (self.face_areas.size, 3))
        self.weighted_face_centres = self.face_areas_reshaped * self.face_centres

class preprocessChecker():
    def __init__(self):
        pass
    
    def compute_all_checks(self, 
                           processed_data_path = "Data\\NormalizedShapeDatabase",
                           output_folder = "Data\\DataAnalysis\\NormalizedDataStatistics", 
                           show_update_every = 0):
        #show_update_every = 0 equals no updates
        config.lg.log("Starting normalization check")
        start = time.time()
        
        all_files = util.get_all_files(processed_data_path)
        util.create_folder(output_folder)
        
        number_of_files = len(all_files)
        config.lg.log(f"{number_of_files} objects found")

        bc_data = []
        pa_data = []
        scale_data = []
        remesh_data = []
        for i in range(number_of_files):
            mesh = config.ml.load_mesh(util.get_path(all_files[i]))
            bc_error, pca_error, scale_error, remesh_error = self.check_mesh(mesh)
            bc_data.append(bc_error)
            pa_data.append(pca_error)
            scale_data.append(scale_error)
            remesh_data.append(remesh_error)
            if (i > 0):
                if (i % show_update_every == 0):
                    config.lg.log(f"{i} of {number_of_files} objects checked: {int((i / number_of_files) * 100)}%")


        self.plot_histogram(bc_data, "Barycenter Error", "Distance of barycenter from the origin", 
                            output_folder + "\\barycenter_error_histogram.png", 
                            median=np.median(bc_data), average=np.average(bc_data))
        self.plot_histogram(pa_data, "Principal Axes Error", "Distance from correct principal axes", 
                            output_folder + "\\principal_axes_histogram.png", 
                            median=np.median(pa_data), average = np.average(pa_data))
        self.plot_histogram(scale_data, "Scale Error", "Distance from unit scale", 
                            output_folder + "\\scale_error_histogram.png", 
                            median=np.median(scale_data), average=np.average(scale_data))
        self.plot_histogram(remesh_data, "Vertex Count Error", "Distance from ideal vertex count", 
                            output_folder + "\\vertex_count_error_histogram.png", 
                            median = np.median(remesh_data), average = np.average(remesh_data))
    
        with open(output_folder + "\\error_statistics.txt", "w") as file:
                    file.write("DATABASE ERROR STATISTICS\n")
                    file.write((f"\nMaximum barycenter error: {np.max(bc_data)}" f"(shape: {util.get_path(all_files[np.argmax(bc_data)])})"))
                    file.write(f"\n Average Barycentric error: {np.average(bc_data)}")
                    file.write(f"\n Median Barycentric error: {np.median(bc_data)}")
                    file.write((f"\n Maximum principal axes error: {np.max(pa_data)}" f"(shape: {util.get_path(all_files[np.argmax(pa_data)])})"))
                    file.write(f"\n Average principal axes error: {np.average(pa_data)}")
                    file.write(f"\n Median principal axes error: {np.median(pa_data)}")
                    file.write((f"\n Maximum scale error: {np.max(scale_data)}" f"(shape: {util.get_path(all_files[np.argmax(scale_data)])})"))
                    file.write(f"\n Average scale error: {np.average(scale_data)}")
                    file.write(f"\n Median scale error: {np.median(scale_data)}")
                    file.write((f"\n Maximum vertex count error: {np.max(remesh_data)}" f"(shape: {util.get_path(all_files[np.argmax(remesh_data)])})"))
                    file.write(f"\n Average vertex count error: {np.average(remesh_data)}")
                    file.write(f"\n Median vertex count error: {np.median(remesh_data)}")

        end = time.time()
        duration = end-start
        config.lg.log(f"Finished checking all {number_of_files} objects in {round(duration / 60, 2) } minutes")
    
    def plot_histogram(self,
                       data,
                       title,
                       xlabel,
                       save_path,
                       average=None,
                       median=None):
        """
        plots a visualisation for a given variable
        data: array data to plot
        title: str, plot title
        xlabel: str, x-axis label
        """
        data = np.asarray(data, dtype=np.float64).flatten()

        plt.figure(figsize=(8,5))

        # Choose the number of bins based on amt of data
        no_bins = int(round(np.sqrt(len(data))))

        plt.hist(data, bins=no_bins, edgecolor='black')

        if average is not None:
            plt.axvline(average, color='red', linestyle='--', label='Mean')
        if median is not None:
            plt.axvline(median, color='blue', linestyle=':', label='Median')

        plt.xlabel(xlabel)
        plt.ylabel("Number of shapes")
        plt.title(title)

        if average is not None or median is not None:
            plt.legend()

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def check_mesh(self, mesh):
        mesh_values = normalizerMeshValues(mesh)
        bc_error = self.check_barycenter(mesh_values)
        pa_error = self.check_principal_axes(mesh_values)
        scale_error = self.check_scaling(mesh_values)
        remesh_error = self.check_remeshing(mesh_values)
        return(bc_error, pa_error, scale_error, remesh_error)

    # Check translation of barycenter to origin
    # if not 0 0 0 wrong -> COMPUTE distance to 000
    def check_barycenter(self, mesh_values):        
        numerator = np.sum(mesh_values.weighted_face_centres, axis=0)
        barycenter = numerator / mesh_values.surface_area
        distance = np.linalg.norm(barycenter)
        return distance 

    #TODO: not functional yet: need to unnormalize face areas + get shit together
    # Check computation of principal axes (no ri)
    # Check alignment with coordinate frame
    # Check flip based on moment test
    # After normalization, recompute the PCA
    # | e1' * x | = 0 and the same for all coordinates
    # give the sum (distance from 0)
    def check_principal_axes(self, mesh_values): 
        #gejoinked thx max
        xx = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 0, mesh_values.surface_area)
        xy = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 1, mesh_values.surface_area)
        xz = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 0, 2, mesh_values.surface_area)
        yy = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 1, 1, mesh_values.surface_area)
        yz = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 1, 2, mesh_values.surface_area)
        zz = self.calculate_covariance(mesh_values.face_centres, mesh_values.weighted_face_centres, 2, 2, mesh_values.surface_area)
        covariance_matrix = np.asarray([[xx, xy, xz]
                                       ,[xy, yy, yz]
                                       ,[xz, yz, zz]])
        eigen_values, eigen_vectors = np.linalg.eig(covariance_matrix)
        
        order = np.argsort(eigen_values)[::-1]
        eigen_vectors = eigen_vectors[:, order]


        # define upstairs~!
        # deze functie is episch
        world_axes = np.eye(3)

        alignment_error = np.sqrt(
            (1 - abs(np.dot(eigen_vectors[:,0], world_axes[0])))**2 +
            (1 - abs(np.dot(eigen_vectors[:,1], world_axes[1])))**2 +
            (1 - abs(np.dot(eigen_vectors[:,2], world_axes[2])))**2
        )
        #alignment = np.array([
        #    abs(np.dot(eigen_vectors[0], x)),
        #    abs(np.dot(eigen_vectors[1], y)),
        #    abs(np.dot(eigen_vectors[2], z))
        #])
        # alignment_error = np.sum(1-alignment)

        return alignment_error

    # Compute distance from 1, which is the maximal perfect normalization (0...1)\
    # So: P(D) = || 1 - (min bounding box, max bounding box) || on every axis
    def check_scaling(self, mesh_values):
        max_bounds = np.max(mesh_values.vertices, axis=0)
        min_bounds = np.min(mesh_values.vertices, axis=0)
        max_diff = np.max(max_bounds - min_bounds)
        scale_error = abs(max_diff - 1)
        return scale_error

    # Maybe nice as percentage? maybe not?
    # Computes the distance from the target amt of vertices: 10.000
    # |v' - Vtarget (10.000)| = distance. Approaching 0 is good
    def check_remeshing(self, mesh_values):
        # define upstairs!!
        ideal_vertices = 10000
        vertex_error = abs(len(mesh_values.vertices) - ideal_vertices)
        return vertex_error
    
    # ==== UTIL ====
        
    def calculate_covariance(self, coords, weighted_face_centres, axis_idx_1, axis_idx_2, surface_area): 
        weighted_total = np.sum(coords[:, axis_idx_1 : axis_idx_1 + 1] * weighted_face_centres[:, axis_idx_2 : axis_idx_2 + 1]) # Use one weighted to only include face weight once
        total = weighted_total / surface_area
        variance = total / (coords.shape[0] - 1)
        return variance

# config.initialize(skip_renderer=True)

# ppc = preprocessChecker()
# ppc.compute_all_checks(show_update_every=500, processed_data_path="Data\\NormalizedDatabase\\")    