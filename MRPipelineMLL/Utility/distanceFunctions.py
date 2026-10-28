import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np


# MY BELOVED EARTH MOVERS DISTANCE,
# THIS IS MY BABY!
# Earth Movers Distances is like the warm sun shining in the ever cold winter,
# It will always be there whenever you need it most,
# For it will never judge you,
# Wherever you are, emd is there, waiting by your side.
# def earth_movers_distance(histogram_array_1, histogram_array_2):
#     diff = histogram_array_2 - histogram_array_1
#     work = 0
#     moving_array = diff
#     for i in range(moving_array.shape[0]):
#         work += abs(moving_array[i])
#         if i+1 < moving_array.shape[0]:
#             moving_array[i+1] += moving_array[i]
#     return work

def get_earth_movers_distance(histogram_array_1, histogram_array_2):
    weight1 = np.sum(histogram_array_1)
    weight2 = np.sum(histogram_array_2)
    histogram_array_1 = histogram_array_1 
    histogram_array_2 = histogram_array_2 * (weight1/weight2)
    moving_array = np.asarray(np.zeros_like(histogram_array_2))
    for i in range(moving_array.shape[0]):
        if i+1 < moving_array.shape[0]:
            moving_array[i + 1] = histogram_array_1[i] - histogram_array_2[i] + moving_array[i] 
    return np.sum(np.absolute(moving_array))

''' Assumes all values to be standardized and only for single value features'''
def get_manhatten_distance(feature_vector_1, feature_vector_2, weights = None):
    if weights:
        feature_vector_1 *= weights
        feature_vector_2 *= weights
    
    diff = np.absolute(feature_vector_1 - feature_vector_2)
    dist = np.sum(diff)
    return dist

''' Assumes all values to be standardized and only for single value features'''
def get_euclidean_distance(feature_vector_1, feature_vector_2, weights = None):
    if weights:
        feature_vector_1 *= weights
        feature_vector_2 *= weights
    diff = np.power(np.absolute(feature_vector_1 - feature_vector_2), 2)
    dist = np.power(np.sum(diff), 1/2)
    return dist