import open3d as o3d
import numpy as np
import os

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

        # calculate triangle/quad/other count (doesn;t work <3)
        triangle_count = 0
        quad_count = 0
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith("f "):
                    num_vertices_in_face = len(line.split()) - 1
                    if num_vertices_in_face == 3:
                        triangle_count += 1
                    elif num_vertices_in_face == 4:
                        quad_count += 1
        
        face_type = "mistake"
        if triangle_count > 0 and quad_count == 0:
            face_type = "triangles"
        elif quad_count > 0 and triangle_count == 0:
            face_type = "quads"
        elif triangle_count > 0 and quad_count > 0:
            face_type = "mixed"
        else:
            face_type = "other"

        row = [
            num_vertices,
            num_faces,
            min_bound[0],
            min_bound[1],
            min_bound[2],
            max_bound[0],
            max_bound[1],
            max_bound[2],
            face_type
        ]

        return row
        
    def analyse_shapes(self,
                       folder = "Data\\OriginalShapeDatabase"):
        # takes a folder name and analysis all shapes in that folder
        rows = []
        for shape_class in os.listdir(folder):
            class_folder = os.path.join(folder, shape_class)

            if not os.path.isdir(class_folder):
                continue

            # add a row for current object, its class, and the analysis results
            for file_name in os.listdir(class_folder):
                if not file_name.lower().endswith(".obj"):
                    continue

                file_path = os.path.join(class_folder, file_name)
                mesh = o3d.io.read_triangle_mesh(file_path)
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

rows = sa.analyse_shapes()
sa.save_analysis(rows)
