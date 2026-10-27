import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from Normalizer.normalizer import PreNormalizer, ShapeNormalizerOpen3D
from FeatureExtraction.featureExtractor import FeatureExtractor
import Utility.config as config
import Utility.utility as util
import Utility.distanceFunctions as distFunc
import numpy as np

# Wish this matcher could match me a date(/rope)
class Matcher():    
    
    def __init__(self):
        self.weights = [1,1,]
        pass
    
    def find_closests_matches(self):
        nm_global_features, nm_distribution_features = self.get_input_features()
        meta_db, global_features, distribution_features = self.get_all_feature_vectors("Data\\DataAnalysis\\featureDatabases.npz", "Data\\DataAnalysis\\distributionDatabases.npz")
        distances = np.zeros(global_features.shape[0])
        for mesh in meta_db:
            distances[mesh[0]] = distFunc.get_manhatten_distance(global_features[global_features[:1] == mesh[0]], nm_global_features) 
            + distFunc.get_earth_movers_distance(distribution_features["A3"][distribution_features["A3"][:1] == mesh[0]], nm_distribution_features)
        
    def get_input_features(self):
        input_location = "Data\\TempFiles"
        file_name = "Temp"
        full_path = input_location + "\\" + file_name
        object_entry = [input_location, "New", file_name]
        meshset = config.ml.load_mesh(full_path, pyMeshLab=True)
        
        pn = PreNormalizer()
        pre_norm_save_loc = input_location + "\\PreNormalized"
        pn.run_one_mesh(meshset, object_entry, pre_norm_save_loc)
        
        mesh = config.ml.load_mesh(pre_norm_save_loc, open3d=True)
        sn = ShapeNormalizerOpen3D()
        norm_save_loc = input_location + "\\Normalized"
        sn.run_one_mesh(mesh, object_entry, norm_save_loc)
        
        fe = FeatureExtractor()
        new_mesh = config.ml.load_mesh(norm_save_loc, open3d=True)
        new_mesh_global_features = fe.extract_global_features(new_mesh, -1)
        new_mesh_distribution_features = fe.extract_distribution_features(new_mesh, -1)
        return new_mesh_global_features, new_mesh_distribution_features
    
    def get_feature_tables(self, location_global_features, location_distributions):
        feature_databases = util.load_numpy_file(location_global_features)
        meta_db = feature_databases['metadata.npy']
        feature_db = feature_databases['features.npy']
        dist_databases = util.load_numpy_file(location_distributions)
        return meta_db, feature_databases, dist_databases
