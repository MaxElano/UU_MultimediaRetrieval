import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from Normalizer.normalizer import PreNormalizer, ShapeNormalizerOpen3D
from FeatureExtraction.featureExtractor import FeatureExtractor
import Utility.config as config
import Utility.utility as util
import Utility.distanceFunctions as distFunc
import numpy as np
from FeatureExtraction.featureTester import ElemFeature, DistFeature
from FeatureExtraction.featureDataNormalizer import FeatureDataNormalizer
from Matching.nearestNeighbors import ANN_matcher

# Wish this matcher could match me a date(/rope)
class Matcher():    
    def __init__(self):
        self.meta_db, self.global_features, self.distribution_features = self.get_feature_tables("Data\\DataAnalysis\\featureDatabasesStandardized.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")
        self.glob_weights, self.dist_weights = self.get_weights("Data\\DataAnalysis\\featureDatabasesStandardized.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")
        self.ann = ANN_matcher(util.combine_feature_vectors(self.global_features, self.distribution_features))

    # <--- Methods for application or inbetween --->
    def get_meta_sorted_by_distance(self, path_to_mesh, use_ann = False, k = 100, e = 0.001):
        if use_ann:
            sorted_indices, sorted_distances = self.get_indices_sorted_by_distance_ann(path_to_mesh, k=k, e=e)
        else:
            sorted_indices, sorted_distances = self.get_indices_sorted_by_distance_custom_pipeline(path_to_mesh)

        return self.meta_db[sorted_indices], sorted_distances

    def get_indices_sorted_by_distance_custom_pipeline(self, path_to_mesh):
        nm_global_features, nm_distribution_features = self.get_input_features(path_to_mesh)
        
        distances = np.zeros(self.meta_db.shape[0])
        for idx, name, _ in self.meta_db:
            if np.all(self.global_features[:,0] != float(idx)):
                config.lg.log(f"index {idx} missing in global feature database")
                continue
            if np.all(self.distribution_features['A3'][:,0] != float(idx)):
                config.lg.log(f"index {idx} missing in distribution feature database")
                continue

            current_global_features = self.global_features[self.global_features[:,0] == float(idx)]
            dist = distFunc.get_euclidean_distance(current_global_features[0,1:], nm_global_features[1:], self.glob_weights) 

            distances[int(idx)] += dist

            for feature in DistFeature:
                column, name = feature.value
                dist_table = self.distribution_features[name]
                current_dist_features = dist_table[dist_table[:,0] == float(idx)]
                dist2 = self.dist_weights[column - 1] * distFunc.get_earth_movers_distance(current_dist_features[0,1:], nm_distribution_features[column - 1][1:]) 
                distances[int(idx)] += dist2

        sorted_indices = np.argsort(distances)
        return sorted_indices, distances[sorted_indices]


    def get_indices_sorted_by_distance_ann(self, path_to_mesh, k, e):
        nm_global_features, nm_distribution_features = self.get_input_features(path_to_mesh)

        # keeping the distances knn returns for future comparisons, perhaps
        knn_dist, pre_selected = self.ann.k_nearest_neighbors(util.combine_feature_vectors(nm_global_features, nm_distribution_features, use_dist_names = False), k=k, e=e) 

        #TODO convert this

        # distances = np.zeros(len(pre_selected))
        # for i in range(len(pre_selected)):
        #     val_index = pre_selected[i]
        #     current_global_features = self.global_features[self.global_features[:,0] == float(val_index)]
        #     dist = distFunc.get_euclidean_distance(current_global_features[0,1:], nm_global_features[1:]) 
        #     distances[i] += dist

        #     for feature in DistFeature:
        #         column, name = feature.value
        #         dist_table = self.distribution_features[name]
        #         current_dist_features = dist_table[dist_table[:,0] == float(val_index)]
        #         dist2 = distFunc.get_earth_movers_distance(current_dist_features[0,1:], nm_distribution_features[column - 1][1:]) 
        #         distances[i] += dist2
        
        return pre_selected, knn_dist

    # <--- Util Functions --->
    def get_input_features(self, path_to_mesh):
        config.lg.log("Get features for inputted mesh")
        input_location = "Data\\TempFiles"
        full_path = path_to_mesh
        path_to_mesh = path_to_mesh.replace("/","\\")
        file_name = path_to_mesh.split("\\")[-1]
        object_entry = [input_location, "New", file_name]

        #Normalize
        config.lg.log("\\_Start pre normalize")
        meshset = config.ml.load_mesh(full_path, pyMeshLab=True)
        pn = PreNormalizer()
        pre_norm_save_loc = input_location + "\\PreNormalized"
        pn.run_one_mesh(meshset, object_entry, pre_norm_save_loc)
        file_name = file_name.split(".")[0] + '.npz'

        config.lg.log("\\_Start normalize")
        mesh = config.ml.load_mesh(util.get_path([pre_norm_save_loc,"New", file_name]), open3d=True)
        sn = ShapeNormalizerOpen3D()
        norm_save_loc = input_location + "\\Normalized"
        sn.run_one_mesh(mesh, object_entry, norm_save_loc)

        #Get Features
        config.lg.log(f"\\_Start feature extractor with {norm_save_loc}, {file_name}")

        fe = FeatureExtractor()
        new_mesh = config.ml.load_mesh(util.get_path([norm_save_loc,"New", file_name]), open3d=True)
        new_mesh_global_features = fe.extract_global_features(new_mesh, -1)
        new_mesh_distribution_features = fe.extract_distribution_features(new_mesh, -1)

        config.lg.log(f"\\_Start feature normalizer {new_mesh_global_features}")
        fn = FeatureDataNormalizer()
        config.lg.log(f"  \\_Feature normalizer created")
        new_mesh_global_features = fn.standardize_one_shape(new_mesh_global_features, "Data\\DataAnalysis\\featureDatabasesStandardized.npz")
        config.lg.log(f"  \\_Standardized")
        new_mesh_distribution_features = fn.normalize_distributions(new_mesh_distribution_features)
        config.lg.log(f"  \\_Normalized")

        config.lg.log("\\_ Done collecting features")
        return new_mesh_global_features, new_mesh_distribution_features
    
    def get_feature_tables(self, location_global_features, location_distributions):
        feature_databases = util.load_numpy_file(location_global_features)
        meta_db = feature_databases['metadata']
        feature_db = feature_databases['features']
        dist_db = util.load_numpy_file(location_distributions)
        return meta_db, feature_db, dist_db

    def get_weights(self, location_global_features, location_distributions):
        print("Start getting weights")
        glob_weights = util.load_numpy_file(location_global_features)["weight_factors"]
        dist_weights = util.load_numpy_file(location_distributions)["weight_factors"]
        total = np.sum(glob_weights) + np.sum(dist_weights)
        print(glob_weights)
        print(dist_weights)
        print("Done getting weights")
        return glob_weights/total, dist_weights/total