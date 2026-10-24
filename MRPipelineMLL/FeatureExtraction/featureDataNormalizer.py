import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import Utility.config as config
from matplotlib import pyplot as plt
import Utility.utility as util
from enum import Enum
from FeatureExtraction.featureTester import ElemFeature

'''
Since different features may have different ranges (min..max values), you need to first bring these ranges 
to a common denominator, or normalize. Consider both min..max normalization and standardization 
(per feature: subtract average of values, for that feature, computed over the entire database, 
and divide result by standard deviation of that feature). 
'''

class FeatureDataNormalizer():
    def __init__(self):
        pass

    def standardize_all(self, old_path="Data\\DataAnalysis\\featureDatabases.npz", new_path="Data\\DataAnalysis\\featureDatabasesStandardized.npz"):
        feature_databases = util.load_numpy_file(old_path)
        
        meta_db = feature_databases['metadata.npy']         
        feature_db = feature_databases['features.npy']
        columns = np.transpose(feature_db)
        normalized = []
        normalized.append(columns[0])
                
        for feature in ElemFeature:
            feature_nr, _ = feature.value
            values = columns[feature_nr]
            normalized.append(self.standardization(values))


        new_feature_db = np.transpose(np.asarray(normalized))
        # saves meta and new feature databases as numpy arrays in a seperate file
        util.save_numpy_file(new_path, metadata=meta_db, features=new_feature_db)

    # normalization resulting in features always going from 0-1
    # already established to not be the best idea bc of outliers, but should be tested for completion i guess
    def min_max_normalization(self, feature_values):
        '''
        get range of values with min() and max()
        for feature values, subtract min, divide by length of range (max-min)
        '''
        pass

    def standardization(self, feature_values):
        '''
        get average
        get standard deviation
        for feature values, subtract average, divide by standard deviation
        '''
        return feature_values


