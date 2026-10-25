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

    def normalize_all_histograms(self, old_path="Data\\DataAnalysis\\distributionDatabases.npz", new_path="Data\\DataAnalysis\\distributionDatabasesNorm.npz"):
        dstr_databases = util.load_numpy_file(old_path)

        a3 = self.normalize_distributions(dstr_databases['A3.npy'])
        d1 = self.normalize_distributions(dstr_databases['D1.npy'])
        d2 = self.normalize_distributions(dstr_databases['D2.npy'])
        d3 = self.normalize_distributions(dstr_databases['D3.npy'])
        d4 = self.normalize_distributions(dstr_databases['D4.npy'])

                # save all distributions in one file
        util.save_numpy_file(new_path, 
                             A3=a3, D1=d1, D2=d2, D3=d3, D4=d4)



    # not most optimized with indices being apart of the db, might be changed later
    def normalize_distributions(self, distribution_db):
        norm_db = []
        for row in distribution_db:
            index = row[0]
            hist_area = np.sum(row) - index
            norm = row/hist_area
            norm[0] = index
            norm_db.append(norm)

        return np.asarray(norm_db)



    # normalization resulting in features always going from 0-1
    # already established to not be the best idea bc of outliers, but should be tested for completion i guess
    def min_max_normalization(self, feature_values):
        min_val  = min(feature_values)
        range = max(feature_values) - min_val
        new_values = (feature_values - min_val) / range
        return new_values

    def standardization(self, feature_values):
        avg = np.mean(feature_values)
        std = np.std(feature_values)
        new_values = (feature_values - avg) / std
        return new_values