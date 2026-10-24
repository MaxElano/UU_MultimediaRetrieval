import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from Normalizer.normalizer import PreNormalizer, ShapeNormalizerOpen3D
from FeatureExtraction.featureExtractor import FeatureExtractor
import Utility.config as config
import Utility.utility as util

# Wish this matcher could match me a date(/rope)
class Matcher():    
    
    def __init__(self):
        self.weights = [1,1,]
        pass
    
    def find_closests_matches(self):
        nm_global_features, nm_distribution_features = self.get_input_features()
        
        
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