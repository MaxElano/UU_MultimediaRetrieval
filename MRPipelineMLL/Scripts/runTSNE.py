import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
from Statistics.tsne import CustomTSNE

#customTSNE = CustomTSNE("Data\\DataAnalysis\\featureDatabasesStandardized.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")
customTSNE = CustomTSNE("Data\\DataAnalysis\\featureDatabases.npz", "Data\\DataAnalysis\\distributionDatabasesNorm.npz")
customTSNE.show_tsne()