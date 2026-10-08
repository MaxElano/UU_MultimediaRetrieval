import numpy as np
import os

import sys
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
import config
 
def getAllFiles(databse_location):
    all_files = []
    for root, dirs, files in os.walk(databse_location):
        for file in files:
            if file.endswith(".obj"):
                all_files.append(os.path.join(root[27:], file))
    
    return all_files

def testFaceAreas(databse_location):
    files = getAllFiles(databse_location)
    total_areas = []
    config.lg.log(f"Found {len(files)} files")
    
    for i in range(len(files)):
        mesh = config.ml.load_mesh(databse_location + '\\' + files[i])
        face_areas = np.linalg.norm(np.asarray(mesh.triangle_normals), axis=1) / 2
        if ((face_areas[face_areas<0]).size > 0):
            config.lg.log(f"Face areas are negative for mesh {files[i]}")
        total_areas.append(np.sum(face_areas))
        
    config.lg.log(np.average(total_areas))
      
config.initialize(skip_renderer=True)      
testFaceAreas('Data\\OriginalShapeDataBase')