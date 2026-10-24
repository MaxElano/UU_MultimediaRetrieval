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



#From teams
def get_emd(features_1, features_2):
    i, j = 0, 1
    flow = [[0 for _ in range(len(features_1))] for _ in range(len(features_1))]
    difference = [0] * len(features_1)
    row = [0] * len(features_1)

    # Initialize empty flow matrix
    for p in range(len(features_1)):
        flow[p] = row.copy()
        flow[p][p] = min(features_1[p], features_2[p])
        difference[p] = features_1[p] - features_2[p]

    # Fill out the flow matrix by spreading differences
    while i + j < 2 * (len(features_1) - 1):
        if difference[i] > 0 and difference[j] < 0:
            if difference[i] <= -difference[j]:
                flow[j][i] = difference[i]
                difference[j] += difference[i]
                difference[i] = 0
                i += 1
                j = i + 1
            else:
                flow[j][i] = -difference[j]
                difference[i] += difference[j]
                difference[j] = 0
                if j < (len(features_1) - 1):
                    j += 1
                else:
                    i += 1
                    j = i + 1
        elif difference[i] < 0 and difference[j] > 0:
            if -difference[i] < difference[j]:
                flow[j][i] = -difference[i]
                difference[j] += difference[i]
                difference[i] = 0
                i += 1
                j = i + 1
            else:
                flow[i][j] = difference[j]
                difference[i] += difference[j]
                difference[j] = 0
                if j < len(features_1) - 1:
                    j += 1
                else:
                    i += 1
                    j = i + 1
        elif difference[i] == difference[j]:
            i += 1
            j = i + 1
        else:
            if j < len(features_1) - 1:
                j += 1
            else:
                i += 1
                j = i + 1

    # Compute sum of distance times flow 
    work = 0
    for p in range(len(features_1)):
        for q in range(len(features_1)):
            work += abs(p - q) * flow[p][q]
    
    # 'Normalize' by dividing by total flow
    total_flow = 0
    for i in range(len(features_1)):
        for j in range(len(features_1)):
            total_flow += flow[i][j]
    print(f"Work {work}")
    emd = work / total_flow

    return emd

array1 = np.asarray([0,1,5,8,3,1,0])
array2 = np.asarray([1,2,6,6,1,2,0])
array3 = np.asarray([1,0,0,0,0,0,0])
array4 = np.asarray([0,0,0,0,0,0,1])
print(get_earth_movers_distance(array1, array2))
print(get_earth_movers_distance(array2, array1))
print(get_earth_movers_distance(array3, array4))
print(get_earth_movers_distance(array4, array3))
print(get_emd(array1, array2))
print(get_emd(array2, array1))
print(get_emd(array3, array4))
print(get_emd(array4, array3))