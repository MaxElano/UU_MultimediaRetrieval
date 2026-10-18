import numpy as np
import open3d as o3d # for generating sphere and rectangle
import config
from renderer import render_mode # for testing purposes!
from matplotlib import pyplot as plt
import utility as util
from enum import Enum
from featureExtractor import feature_Extractor
from imageGenerator import imageGenerator
from imageGenerator import cameraAngle

class extremity(Enum):
    MAX = 1
    MIN = 2

# holds the column the feature can be found at as well as the name of the feature
# just elementary features (for now? perchance)
class elemFeature(Enum):
    SURF = (1, "Surface Area")
    SPH = (2, "Sphericity")
    RECT = (3, "Rectangularity")
    DM = (4, "Diameter")
    CONV = (5, "Convexity")
    ECC = (6, "Eccentricity")

class distFeature(Enum):
    A3 = (1, "A3")
    D1 = (2, "D1")
    D2 = (3, "D2")
    D3 = (4, "D3")
    D4 = (5, "D4")

# Main check function
class featureTester():
    def __init__(self):
        # when implemented
        #config.lg.set_to_write()
        self.ig = imageGenerator()

        feature_databases = util.load_numpy_file("Data\\DataAnalysis\\featureDatabases.npz")
        
        self.meta_db = feature_databases['metadata.npy']
        self.feature_db = feature_databases['features.npy']
        
        self.dist_databases = util.load_numpy_file("Data\\DataAnalysis\\distributionDatabases.npz")

        self.log_save_folder = "Data\\DataAnalysis\\FeatureChecker"
        self.log_location = self.log_save_folder + "\\FeatureValueLogs"
        self.ss_save_folder = "Features"

    def testFeatureExtraction(self):
        util.create_folder(self.log_save_folder)
        util.empty_file(self.log_location)

        for feature in elemFeature:
            # Elementary features
            index_min, value_min = self.get_extreme_feature(feature, extremity.MIN)
            index_max, value_max = self.get_extreme_feature(feature, extremity.MAX)
            self.save_elementary_feature(value_min, feature, index_min, "Minimum")
            self.save_elementary_feature(value_max, feature, index_max, "Maximum")

        title, mesh, feature_value = self.compare_sphere()
        self.save_elementary_feature_from_mesh(feature_value, elemFeature.SPH, mesh, title)
        title, mesh, feature_value = self.compare_rectangle()
        self.save_elementary_feature_from_mesh(feature_value, elemFeature.RECT, mesh, title)

        # generate distribution features
        for feature in distFeature:
            self.plot_per_category(feature)

    # works for elementary features
    def get_extreme_feature(self, 
                            feature : elemFeature, # includes the column and ft name
                            extremity : extremity # max/min
                            ):
        """
        find the mesh with the highest/lowest value for a given feature.
        returns the mesh index, and value 
        """
        column, feature_name = feature.value

        values = self.feature_db[:, column].astype(float)
        if extremity == extremity.MAX:
            index = np.argmax(values)
        else:
            index = np.argmin(values)
        extreme_value = values[index]

        return index, extreme_value

    def save_elementary_feature_from_mesh(self,
                                          feature_value : float,
                                          feature : elemFeature,
                                          mesh,
                                          mesh_title,
                                          description = "Value of the "
                                          ):
        column, feature_name = feature.value

        title = feature_name + "_" + mesh_title

        self.ig.generateFromMesh([mesh], self.ss_save_folder, title)

        with open(self.log_location, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Mesh name: {mesh_title}\n")

    def save_elementary_feature(self,
                                feature_value : float,
                                feature : elemFeature,
                                index = None,
                                description = "Value of the ",
                                from_database = "Data\\NormalizedShapeDatabase\\"
                                ):
        column, feature_name = feature.value

        mesh_name = self.meta_db[index, 1]
        mesh_category = self.meta_db[index, 2]

        title = feature_name + "_" + mesh_name

        mesh_location = from_database + mesh_category + "\\" + mesh_name

        self.ig.generateFromPath([mesh_location], self.ss_save_folder, title)

        with open(self.log_location, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Index: {index}\n")
            f.write(f"Mesh name: {mesh_name}\n")
            f.write(f"Mesh Category: {mesh_category}\n")

    # For the given distribution feature, for all categories, show a histogram with ALL lines <3
    def plot_per_category(self,
                          feature : distFeature
                          ):
        column, feature_name = feature.value
        categories = np.unique(self.meta_db[:, 2])
        for category in categories:
            indices = self.meta_db[self.meta_db[:,2] == category][:,0]
            fig, ax = plt.subplots(figsize=(10,5))

            for index in indices:
                ax.plot(self.dist_databases[feature_name][int(index)], alpha = 0.3, linewidth = 1)

            plt.xlabel("Bins")
            plt.ylabel(f"Distribution variable")
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
        volume = feature_Extractor.volume(feature_Extractor, vertices, triangles)
        surface = feature_Extractor.surface_area(feature_Extractor, sphere_mesh)
        compactness = feature_Extractor.compactness(feature_Extractor, surface, volume)
        sphericity = feature_Extractor.sphericity(feature_Extractor, compactness)

        return "sphere", sphere_mesh, sphericity

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
        volume = feature_Extractor.volume(feature_Extractor, vertices, triangles)
        rectangularity = feature_Extractor.rectangularity(feature_Extractor, volume, obb)

        return "rectangle", rectangle_mesh, rectangularity


    # given a list of objects, it prints the mesh screenshots and gives the distributions
    # can be used for : comparing 2 similar (same category) and one very different shape
    def compare_distribution(self,
                             feature : distFeature,
                             objects, # give 3 objects, first two being of the same category and similar, and the third one being very different
                             from_database = "Data\\NormalizedShapeDatabase\\"
                             ):
        column, feature_name = feature.value
        # take 2 shapes from the same category and 1 from a very different one!
        for obj in objects:
            row = np.where(self.meta_db[:.1] == obj)[0][0]
            index = int(self.meta_db[row, 0])

            mesh_name = self.meta_db[index, 1]
            mesh_category = self.meta_db[index, 2]
            title = feature_name + "_" + mesh_name
            mesh_location = from_database + mesh_category + "\\" + mesh_name

            self.ig.generateFromPath([mesh_location], self.ss_save_folder, title)
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(self.dist_databases[feature_name][int(index)], alpha = 0.3, linewidth = 1)

            plt.xlabel("Bins")
            plt.ylabel(f"Distribution variable")
            plt.tight_layout()
            plt.savefig(self.log_save_folder + "\\" + feature_name + "_" + mesh_category + ".png", dpi=300)
            plt.close()


ft = featureTester()
ft.testFeatureExtraction()