import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import Utility.config as config
import numpy as np
import scipy.spatial as sp



class ANN_matcher():
    def __init__(self, feature_database):
        #get rid of first column containing the index, build kd tree       
        self.feature_db = np.delete(feature_database, np.s_[0], axis=1) 
        self.kdtree = sp.KDTree(self.feature_db)
        config.lg.log("Finished building KDTree")
        
    #returns the approximate k nearest neighbors from the kd tree
    def k_nearest_neighbors(self, point, k):
        knn_distances, knn_indices = self.kdtree.query(point, k=k)
        return knn_distances, knn_indices

    # returns all neighbors within the distance r from a point
    def r_nearest_neighbors(self, point, r):
        rnn= self.kdtree.query_ball_point(point, r)
        return rnn

