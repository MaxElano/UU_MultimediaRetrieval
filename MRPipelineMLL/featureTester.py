import numpy as np
import open3d as o3d # for generating sphere and rectangle
import config
from renderer import render_mode # for testing purposes!
from matplotlib import pyplot as plt
import utility as util
from enum import Enum
from featureExtractor import feature_Extractor
from imageGenerator import imageGenerator

class Extremity(Enum):
    MAX = 1
    MIN = 2

# holds the column the feature can be found at as well as the name of the feature
# just elementary features (for now? perchance)
class Feature(Enum):
    SURF = (1, "Surface Area")
    SPH = (2, "Sphericity")
    RECT = (3, "Rectangularity")
    DM = (4, "Diameter")
    CONV = (5, "Convexity")
    ECC = (6, "Eccentricity")

# Main check function
class featureTester():
    def __init__(self):
        # when implemented
        #config.lg.set_to_write()
        self.ig = imageGenerator()

        featureDatabases = util.load_numpy_file("Data\\DataAnalysis\\featureDatabases.npz")
        
        self.metaDatabase = featureDatabases['metadata.npy']
        self.featureDatabase = featureDatabases['features.npy']
        
        distributionDatabases = util.load_numpy_file("Data\\DataAnalysis\\distributionDatabases.npz")

        self.A3 = distributionDatabases["A3"]
        self.D1 = distributionDatabases["D1"]
        self.D2 = distributionDatabases["D2"]
        self.D3 = distributionDatabases["D3"]
        self.D4 = distributionDatabases["D4"]

        self.save_folder = "Data\\DataAnalysis\\FeatureChecker"
        self.logLocation = self.save_folder + "\\FeatureValueLogs"
        self.screenshot_save_folder = "Features"

    def testFeatureExtraction(self):
        util.create_folder(self.save_folder)
        util.empty_file(self.logLocation)

        for feature in Feature:
            # Elementary features
            index1, value1 = self.get_extreme_feature(feature, Extremity.MIN)
            index2, value2 = self.get_extreme_feature(feature, Extremity.MAX)
            self.save_elementary_feature(value1, feature, index1, "Minimum")
            self.save_elementary_feature(value2, feature, index2, "Maximum")

        title, mesh, feature_value = self.compare_sphere()
        self.save_elementary_feature_from_mesh(feature_value, Feature.SPH, mesh, title)
        title, mesh, feature_value = self.compare_rectangle()
        self.save_elementary_feature_from_mesh(feature_value, Feature.RECT, mesh, title)

        #self.plot_per_category("D4")

        # Distribution features
        
        # Add array to text file ?!

    # works for elementaary features
    def get_extreme_feature(self, 
                            feature : Feature, # includes the column and ft name
                            extremity : Extremity # max/min
                            ):
        """
        find the mesh with the highest/lowest value for a given feature.
        returns the mesh index, and value 
        """
        column, feature_name = feature.value

        values = self.featureDatabase[:, column].astype(float)
        if extremity == Extremity.MAX:
            index = np.argmax(values)
        else:
            index = np.argmin(values)
        extreme_value = values[index]

        return index, extreme_value

    def save_elementary_feature_from_mesh(self,
                                          feature_value : float,
                                          feature : Feature,
                                          mesh,
                                          mesh_title,
                                          description = "Value of the ",
                                          from_database = "Data\\NormalizedShapeDatabase\\"
                                          ):
        column, feature_name = feature.value

        title = feature_name + "_" + mesh_title

        self.ig.generateFromMesh([mesh], self.screenshot_save_folder, title)

        with open(self.logLocation, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Mesh name: {mesh_title}\n")

    def save_elementary_feature(self,
                                feature_value : float,
                                feature : Feature,
                                index = None,
                                description = "Value of the ",
                                from_database = "Data\\NormalizedShapeDatabase\\",
                                ):
        column, feature_name = feature.value

        mesh_name = self.metaDatabase[index, 1]
        mesh_category = self.metaDatabase[index, 2]

        title = feature_name + "_" + mesh_name

        mesh_location = from_database + mesh_category + "\\" + mesh_name

        self.ig.generateFromPath([mesh_location], self.screenshot_save_folder, title)

        with open(self.logLocation, "a", encoding="utf-8") as f:
            f.write(f"{description} {feature_name}: {feature_value}\n")
            f.write(f"Index: {index}\n")
            f.write(f"Mesh name: {mesh_name}\n")
            f.write(f"Mesh Category: {mesh_category}\n")

    # For the given distribution feature, for all categories, show a histogram with ALL lines <3
    def plot_per_category(self,
                          feature : str # mb i couldnt be arsed
                          # should be either A3, D1, D2, D3, D4
                          ):
        categories = np.unique(self.metaDatabase[:, 2])

        for category in categories:
            indices = self.metaDatabase[self.metaDatabase[:,2] == category][:,0]
            print(indices)
            fig, ax = plt.subplots(figsize=(10,5))
            for index in indices:
                if feature == "A3":
                    ax.plot(self.A3[int(index)], alpha=0.3, linewidth = 1)
                    plt.title(f"A3 Distributions within category: {category}")
                elif feature == "D1":
                    ax.plot(self.D1[int(index)], alpha=0.3, linewidth = 1)
                    plt.title(f"D1 Distributions within category: {category}")
                elif feature == "D2":
                    ax.plot(self.D2[int(index)], alpha=0.3, linewidth = 1)
                    plt.title(f"D2 Distributions within category: {category}")
                elif feature == "D3":
                    ax.plot(self.D3[int(index)], alpha=0.3, linewidth = 1)
                    plt.title(f"D3 Distributions within category: {category}")
                elif feature == "D4":
                    ax.plot(self.D4[int(index)], alpha=0.3, linewidth = 1)
                    plt.title(f"D4 Distributions within category: {category}")

            plt.xlabel("Bins")
            plt.ylabel(f"Distribution variable")
            plt.tight_layout()
            plt.show()

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


    def compare_distribution(self,
                             feature : str):
        # take 2 shapes from the same category and 1 from a very different one!

        # take distribution values from those

        # compute histograms + make screenshots
        return False
    
    # A3
        # pick 2 similar shapes

        # take index from metaDatabase
        # take A3 from distributionDatabases using index
        # compute histogram based on A3

        # print histogram to Screenshots

        # pick a very different shape

        # Within a catgory, plot all histograms on top of ach othr: 
        # To s how similar thy ar.
        # similar within a class: liklihood you will gt th rihgt catgory high
        # similarity btwn classs: liklihood that you will gt a diffrnt catgory highr
        # mak sur to hav nough bins
        # for all classs

ft = featureTester()
ft.testFeatureExtraction()