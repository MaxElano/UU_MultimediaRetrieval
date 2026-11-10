import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import Utility.config as config
from enum import Enum

'''
File with functions that are used very often, 
preferably use these above implementing them every time
'''
class CustomDistFeature(Enum): #Circular dependancy so had to extract these, I know bad code hibijibisch but lack of time to create pretty solution (outisde class)
    A3 = (1, "A3")
    D1 = (2, "D1")
    D2 = (3, "D2")
    D3 = (4, "D3")
    D4 = (5, "D4")

def get_all_files(database_path):
    # Returns list of all objects with (Path to database, class name, file name)
    all_files = []
    for root, dirs, files in os.walk(database_path):
        for file in files:
            if file.endswith(".obj") or file.endswith(".npz"):
                class_name = root.split('\\')[-1]
                all_files.append((database_path, class_name, file))
    return np.asarray(all_files)

def create_folder(folder_path):
    steps = folder_path.split('\\')
    for i in range(len(steps)):
        path = '\\'.join(steps[:i + 1])
        if not os.path.exists(path):
            os.makedirs(path)

def get_path(obj_entry):
    return '\\'.join(obj_entry)

def empty_file(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            file.write("")
    else:
        with open(file_path, "w") as file:
            file.seek(0)
            file.truncate()

def save_numpy_file(total_path, **kwargs):
    deepest_folder = '\\'.join(total_path.split('\\')[:-1])
    total_path = '.'.join(total_path.split('.')[:-1])
    create_folder(deepest_folder)
    np.savez(total_path, **kwargs)

# Acces specific arrays using returned file
# file["example_array_name"]
def load_numpy_file(total_path):
    return np.load(total_path)

# Takes default global features table
# Distribution features have to be all, recentely read from numpy
def combine_feature_vectors(global_features, distribution_features, use_dist_names = True):
    total_features = []

    if use_dist_names:
        total_features = global_features[:,1:]
        for feature in CustomDistFeature:
            _, name = feature.value
            current_dist = distribution_features[name]
            total_features = np.concatenate((total_features, current_dist[:,1:]), axis=1)
    else:
        total_features = global_features[1:]
        for idx, feature_database in enumerate(distribution_features):
            if idx == distribution_features.shape[0] - 1:
                continue #SKIP THE WEIGHTS

            total_features = np.concatenate((total_features, feature_database[1:]), axis=0)

    return total_features

# Taken from https://stackoverflow.com/questions/53699012/performant-cartesian-product-cross-join-with-pandas
# Credits to @senderle
def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)  

class ProgressCounter():
    def __init__(self, total, update_every, custom_text = ''):
        self.total = total
        self.update_every = update_every
        if (len(custom_text) > 0):
            self.custom_text = " " + custom_text
        else:   
            self.custom_text = custom_text
        self.index = 0
    
    def increment(self):
        self.index += 1
        self.check_show()
        
    def decrement(self):
        self.index -= 1
        self.check_show()
    
    def reset(self):
        self.index = 0
        
    def check_show(self):
         if (self.index > 0):
            if (self.index % self.update_every == 0): #Can't be combined cuz python sucks
                percentage = int((self.index / self.total) * 100)
                config.lg.custom_print(f"{self.index} of {self.total}{self.custom_text}: {percentage}%")