import open3d as o3d
import numpy as np
import os
import config
import utility as util

'''
A tool that checks all shapes in a database and infers their:
Class, number of faces and vertices, type of faces, axis-aligned 3D bounding box
# saves them to a csv file
'''

class shapeAnalyser():
    def __init__(self):
        pass

    def analyse_shape(self,
                      mesh,
                      file_path):
        # takes a shape and analysis its class, num of faces, num of vertices, type of faces, axis-aligned 3D bounding box
        
        num_vertices = len(mesh.vertices)
        num_faces = len(mesh.triangles)

        # 3d axis-aligned bounding box retrieval
        b_box = mesh.get_axis_aligned_bounding_box()
        min_bound = b_box.min_bound
        max_bound = b_box.max_bound

        bounds = {
            "min": [min_bound[0], min_bound[1], min_bound[2]],
            "max": [max_bound[0], max_bound[1], max_bound[2]]
        }


        row = [
            num_vertices,
            num_faces,
            bounds
        ]

        return row
        
    def analyse_shapes(self,
                       folder = "Data\\OriginalShapeDatabase"):
        # takes a folder name and analysis all shapes in that folder
        rows = []

        all_files = util.get_all_files(folder)

        for path in all_files:
            _, shape_class, file_name = path
            file_path = util.get_path(path)
            mesh = config.ml.load_mesh(file_path, open3d=True)
            row = self.analyse_shape(mesh, file_path)
            rows.append([file_name, shape_class] + row)

        return rows 

    def save_analysis(self,
                      rows,
                      file_name = 'data_info.csv'):
        # Overwrites if there is already an analysis
        file_path = "Data\\DataAnalysis\\" + file_name
        np.savetxt(file_path, rows, delimiter=",", fmt='%s')


sa = shapeAnalyser()
config.initialize()

# norm_rows = sa.analyse_shapes(folder="Data\\NormalizedShapeDatabase")
# sa.save_analysis(norm_rows, file_name = "normalized_data_info.csv")

# rows = sa.analyse_shapes()
# sa.save_analysis(rows)
