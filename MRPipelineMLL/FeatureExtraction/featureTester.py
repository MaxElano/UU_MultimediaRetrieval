import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import open3d as o3d # for generating sphere and rectangle
from matplotlib import pyplot as plt
import Utility.utility as util
from enum import Enum
from FeatureExtraction.featureExtractor import FeatureExtractor
from Utility.imageGenerator import ImageGenerator, CameraAngle

class Extremity(Enum):
    MAX = 1
    MIN = 2

# holds the column the feature can be found at as well as the name of the feature
# just elementary features (for now? perchance)
class ElemFeature(Enum):
    SURF = (1, "Surface Area")
    SPH = (2, "Sphericity")
    RECT = (3, "Rectangularity")
    DM = (4, "Diameter")
    CONV = (5, "Convexity")
    ECC = (6, "Eccentricity")

class DistFeature(Enum):
    A3 = (1, "A3")
    D1 = (2, "D1")
    D2 = (3, "D2")
    D3 = (4, "D3")
    D4 = (5, "D4")

# Main check function
class FeatureTester():
    def __init__(self):
        # when implemented
        #config.lg.set_to_write()
        self.ig = ImageGenerator()

        feature_databases = util.load_numpy_file("Data\\DataAnalysis\\featureDatabases.npz")
        
        self.meta_db = feature_databases['metadata.npy']
        self.feature_db = feature_databases['features.npy']
        
        self.dist_databases = util.load_numpy_file("Data\\DataAnalysis\\distributionDatabases.npz")

        self.log_save_folder = "Data\\DataAnalysis\\FeatureChecker"
        self.log_location = self.log_save_folder + "\\FeatureValueLogs"
        self.ss_save_folder = "Features"

    def test_feature_extraction(self):
        util.create_folder(self.log_save_folder)
        util.empty_file(self.log_location)

        for feature in ElemFeature:
            # Elementary features
            index_min, value_min = self.get_extreme_feature(feature, Extremity.MIN)
            index_max, value_max = self.get_extreme_feature(feature, Extremity.MAX)
            self.save_elementary_feature(value_min, feature, index_min, "Minimum")
            self.save_elementary_feature(value_max, feature, index_max, "Maximum")

        title, mesh, sphericity, eccentricity = self.compare_sphere()
        self.save_elementary_feature_from_mesh(sphericity, ElemFeature.SPH, mesh, title)
        self.save_elementary_feature_from_mesh(eccentricity, ElemFeature.ECC, mesh, title)

        title, mesh, feature_value = self.compare_rectangle()
        self.save_elementary_feature_from_mesh(feature_value, ElemFeature.RECT, mesh, title)

        # generate distribution features
        #for feature in DistFeature:
        #    self.plot_per_category(feature)

    # works for elementary features
    def get_extreme_feature(self, 
                            feature : ElemFeature, # includes the column and ft name
                            Extremity : Extremity # max/min
                            ):
        """
        find the mesh with the highest/lowest value for a given feature.
        returns the mesh index, and value 
        """
        column, _ = feature.value

        values = self.feature_db[:, column].astype(float)
        if Extremity == Extremity.MAX:
            index = np.argmax(values)
        else:
            index = np.argmin(values)
        extreme_value = values[index]

        return index, extreme_value

    def save_elementary_feature_from_mesh(self,
                                          feature_value : float,
                                          feature : ElemFeature,
                                          mesh,
                                          mesh_title,
                                          description = "Value of the "
                                          ):
        _, feature_name = feature.value

        title = feature_name + "_" + mesh_title

        self.ig.generate_from_mesh([mesh], self.ss_save_folder, title)

        with open(self.log_location, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Mesh name: {mesh_title}\n")

    def save_elementary_feature(self,
                                feature_value : float,
                                feature : ElemFeature,
                                index = None,
                                description = "Value of the ",
                                from_database = "Data\\NormalizedShapeDatabase\\"
                                ):
        _, feature_name = feature.value

        mesh_name = self.meta_db[index, 1]
        mesh_category = self.meta_db[index, 2]

        title = feature_name + "_" + mesh_name

        mesh_location = from_database + mesh_category + "\\" + mesh_name

        self.ig.generate_from_path([mesh_location], self.ss_save_folder, title)

        with open(self.log_location, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Index: {index}\n")
            f.write(f"Mesh name: {mesh_name}\n")
            f.write(f"Mesh Category: {mesh_category}\n")

    # For the given distribution feature, for all categories, show a histogram with ALL lines <3
    def plot_per_category(self,
                          feature : DistFeature
                          ):
        _, feature_name = feature.value
        categories = np.unique(self.meta_db[:, 2])
        for category in categories:
            indices = self.meta_db[self.meta_db[:,2] == category][:,0]
            _, ax = plt.subplots(figsize=(10,5))

            for index in indices:
                ax.plot(self.dist_databases[feature_name][int(index)], alpha = 0.3, linewidth = 1)

            plt.xlabel("Bins")
            plt.ylabel(f"Distribution variable")
            plt.title(f"{feature_name} distribution of {category}")
            plt.tight_layout()
            plt.savefig(self.log_save_folder + "\\" + feature_name + "_" + category + ".png", dpi=300)
            plt.close()

    # Sphericity
    def compare_sphere(self):
        # Generate sphere mesh
        #TODO: give more vertices?
        sphere_mesh = o3d.geometry.TriangleMesh.create_sphere(radius = 0.5)
        vertices = np.asarray(sphere_mesh.vertices)
        triangles = np.asarray(sphere_mesh.triangles)
        volume = FeatureExtractor.volume(FeatureExtractor, vertices, triangles)
        surface = FeatureExtractor.surface_area(FeatureExtractor, sphere_mesh)
        compactness = FeatureExtractor.compactness(FeatureExtractor, surface, volume)
        sphericity = FeatureExtractor.sphericity(FeatureExtractor, compactness)

        convex_hull, _ = sphere_mesh.compute_convex_hull()
        obb = convex_hull.get_axis_aligned_bounding_box() #we can use axis aligned here bc of normalization step
        eigenvalues = obb.get_extent()
        eccentricity =  np.max(eigenvalues)/np.min(eigenvalues)

        return "sphere", sphere_mesh, sphericity, eccentricity

    # Rectangularity -> generate rectangle tc
    def compare_rectangle(self):
        # Generate rectangle mesh
        #TODO: give more vertices?
        rectangle_mesh = o3d.geometry.TriangleMesh.create_box(width = 1.0, height = 1.0, depth = 1.0)
        rectangle_mesh.translate([-0.5, -0.5, -0.5])
        # get features
        vertices = np.asarray(rectangle_mesh.vertices)
        triangles = np.asarray(rectangle_mesh.triangles)
        convex_hull, _ = rectangle_mesh.compute_convex_hull()
        obb = convex_hull.get_axis_aligned_bounding_box() #we can use axis aligned here bc of normalization step
        volume = FeatureExtractor.volume(FeatureExtractor, vertices, triangles)
        rectangularity = FeatureExtractor.rectangularity(FeatureExtractor, volume, obb)

        return "rectangle", rectangle_mesh, rectangularity


    # given a list of objects, it prints the mesh screenshots and gives the distributions
    # can be used for : comparing 2 similar (same category) and one very different shape
    def compare_distribution(self,
                             feature : DistFeature,
                             objects, # give 3 objects, first two being of the same category and similar, and the third one being very different
                             from_database = "Data\\NormalizedShapeDatabase\\"
                             ):
        _, feature_name = feature.value
        # take 2 shapes from the same category and 1 from a very different one!
        for obj in objects:
            row = np.where(self.meta_db[:,1] == obj)[0][0]
            index = int(self.meta_db[row, 0])

            mesh_name = self.meta_db[index, 1]
            mesh_category = self.meta_db[index, 2]
            title = feature_name + "_" + mesh_name
            mesh_location = from_database + mesh_category + "\\" + mesh_name

            self.ig.generateFromPath([mesh_location], self.ss_save_folder, title)
            self.ig.generate_from_path([mesh_location], self.ss_save_folder, title)
            _, ax = plt.subplots(figsize=(10, 5))

            ax.plot(self.dist_databases[feature_name][int(index)], alpha = 0.3, linewidth = 1)

            plt.xlabel("Bins")
            plt.ylabel(f"Distribution variable")
            plt.tight_layout()
            plt.savefig(self.log_save_folder + "\\" + feature_name + "_" + mesh_category + ".png", dpi=300)
            plt.savefig(self.log_save_folder + "\\" + feature_name + "_" + mesh_category + "_" + mesh_name + ".png", dpi=300)
            plt.close()


#ft = FeatureTester()
#ft.compare_distribution(DistFeature.D4, ["D00013.npz", "D00487.npz", "m722.npz"])
# ft.test_feature_extraction()