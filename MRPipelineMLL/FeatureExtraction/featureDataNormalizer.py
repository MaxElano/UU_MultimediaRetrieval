import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import Utility.config as config
from matplotlib import pyplot as plt
import Utility.utility as util
import Utility.distanceFunctions as distFunc
from enum import Enum
from FeatureExtraction.featureTester import ElemFeature, DistFeature

'''
Since different features may have different ranges (min..max values), you need to first bring these ranges 
to a common denominator, or normalize. Consider both min..max normalization and standardization 
(per feature: subtract average of values, for that feature, computed over the entire database, 
and divide result by standard deviation of that feature). 
'''

class FeatureDataNormalizer():
    def __init__(self):
        self.global_features_path = "Data\\DataAnalysis\\featureDatabasesStandardized.npz"
        self.global_features = util.load_numpy_file(self.global_features_path)

    def standardize_all(self, old_path="Data\\DataAnalysis\\featureDatabases.npz", new_path="Data\\DataAnalysis\\featureDatabasesStandardized.npz"):
        config.lg.log(f"Starting global feature standardization from location {old_path} to {new_path}")

        feature_databases = util.load_numpy_file(old_path)
        
        meta_db = feature_databases['metadata.npy']         
        feature_db = feature_databases['features.npy']
        columns = np.transpose(feature_db)
        normalized = []
        normalized.append(columns[0])
        avgs = np.zeros(feature_db.shape[1])
        stds = np.zeros(feature_db.shape[1])
        
        pc = util.ProgressCounter(feature_db.shape[1] - 1, 1, "global features standardized")

        for feature in ElemFeature:
            feature_nr, _ = feature.value
            values = columns[feature_nr]
            normalized_values, avg, std = self.standardization(values)
            normalized.append(normalized_values)
            avgs[feature_nr] = avg
            stds[feature_nr] = std
            pc.increment()

        new_feature_db = np.transpose(np.asarray(normalized))
        weight_factors = np.ones(new_feature_db.shape[1] - 1)
        # saves meta and new feature databases as numpy arrays in a seperate file
        util.save_numpy_file(new_path, metadata=meta_db, features=new_feature_db, avgs=avgs, stds=stds, weight_factors=weight_factors)
        config.lg.log(f"Done standardizating")

    def normalize_all_histograms(self, old_path="Data\\DataAnalysis\\distributionDatabases.npz", new_path="Data\\DataAnalysis\\distributionDatabasesNorm.npz"):
        dstr_databases = util.load_numpy_file(old_path)

        pc = util.ProgressCounter(5, 1, "histograms normalized")

        a3 = self.normalize_distributions(dstr_databases['A3.npy'])
        pc.increment()
        d1 = self.normalize_distributions(dstr_databases['D1.npy'])
        pc.increment()
        d2 = self.normalize_distributions(dstr_databases['D2.npy'])
        pc.increment()
        d3 = self.normalize_distributions(dstr_databases['D3.npy'])
        pc.increment()
        d4 = self.normalize_distributions(dstr_databases['D4.npy'])
        pc.increment()

        weight_factors = [self.calculate_histogram_weight(x) for x in [a3,d1,d2,d3,d4]]

        # save all distributions in one file
        util.save_numpy_file(new_path, 
                             A3=a3, D1=d1, D2=d2, D3=d3, D4=d4, weight_factors=weight_factors)
        config.lg.log(f"Done normalizing")

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

    # Only pass one feature table, so for example all A3 features
    def calculate_histogram_weight(self, histo_database):
        # calculate all distances
        distances = []

        pc = util.ProgressCounter(histo_database.shape[0]*histo_database.shape[0], 2500000, "of combinations checked")
        # In theory this should be half table, but cannot gaurantee edm(a,b) = edm(b,a) so test all (thus slower)
        for i in range(histo_database.shape[0]):
            for j in range(histo_database.shape[0]):
                if i == j:
                    continue

                dist = distFunc.get_earth_movers_distance(histo_database[i,1:], histo_database[j,1:])
                distances.append(dist)
                pc.increment

        #calculate variance and weight
        std = np.std(distances)
        return 1/std

    # normalization resulting in features always going from 0-1
    # already established to not be the best idea bc of outliers, but should be tested for completion i guess
    def min_max_normalization(self, feature_values):
        min_val  = min(feature_values)
        range = max(feature_values) - min_val
        new_values = (feature_values - min_val) / range
        #Has to safe min max values for new shapes (querying)
        return new_values

    def standardization(self, feature_values, avg=None, std=None):
        if not avg:
            avg = np.mean(feature_values)
        if not std:
            std = np.std(feature_values)
        new_values = (feature_values - avg) / std
        #Has to save avg and std for new shapes (querying)
        return new_values, avg, std

    def standardize_one_shape(self, feature_values, global_features_path):
        normalized = []
        normalized.append(feature_values[0])
        avgs = self.global_features['avgs']
        stds = self.global_features['stds']
        for feature in ElemFeature:
            feature_nr, _ = feature.value
            values = feature_values[feature_nr]
            normalized_value, _, _ = self.standardization(values, avgs[feature_nr], stds[feature_nr])
            normalized.append(normalized_value)

        new_feature_db = np.transpose(np.asarray(normalized))
        return new_feature_db