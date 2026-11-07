import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import Utility.config as config
from matplotlib import pyplot as plt
import Utility.utility as util
from enum import Enum
from FeatureExtraction.featureExtractor import FeatureExtractor
from FeatureExtraction.featureDataNormalizer import FeatureDataNormalizer


config.initialize(skip_renderer=True)    

#fe = FeatureExtractor()
#fe.extract_features_from_database()

fn = FeatureDataNormalizer()
fn.standardize_all(new_path="Data\\DataAnalysis\\featureDatabasesStandardized.npz")
fn.normalize_all_histograms()
