import open3d as o3d
import numpy as np
from renderer import render_mode
import config
import os

'''
    resample outliers with poorly-sampled shapes

    too small shapes (having under 100 vertices and/or faces): refine (split large faces into smaller ones).
    too large shapes (shapes with hundreds of thousands of vertices and/or faces): simplify (group small faces into larger ones). 

    For both refining and simplification you can use various tools such as MeshLab, PMP, OFF mesh, PyMesh, 
    or any of the tools listed on the Additional material course page. T
    hat page also contains bare-bones, simple, C++ code that implements both mesh refinement and simplification).

    Carefully experiment with refinement options so that you obtain meshes which are 
    (a) correct and looking close to the original ones
    (b) not too small or too large
    A rough estimate of a good sample (vertex) count is around 5K..10K. 
'''

class resampler():
    def __init__(self):
        pass

    # resamples all outliers of a given database (which should be a copy of the og) to be fairly uniform
    def resample_all(self, min, max, folder = "Data\\NormalizedShapeDatabase"):
        simplified_count = 0
        refined_count = 0
        # takes a folder name and analyses all shapes in that folder
        for shape_class in os.listdir(folder):
            class_folder = os.path.join(folder, shape_class)
            if not os.path.isdir(class_folder):
                continue

            # 
            for file_name in os.listdir(class_folder):
                if not file_name.lower().endswith(".obj"):
                    continue
                
                file_path = os.path.join(class_folder, file_name)
                mesh_before = o3d.io.read_triangle_mesh(file_path)

                #determines if mesh needs to be simplified
                if len(mesh_before.triangles) <= min:
                    mesh_after = self.refine(mesh_before, min)
                    o3d.io.write_triangle_mesh(file_path, mesh_after)
                    simplified_count += 1
                elif len(mesh_before.vertices) >= max:
                    mesh_after = self.simplify_by_decimation(mesh_before, max)
                    o3d.io.write_triangle_mesh(file_path, mesh_after)
                    refined_count +=1
        print(f"Resampling done. Refined {refined_count} shapes. Simplified {simplified_count} shapes.")    
        

    # refines a mesh so that its number of faces is higher than a given number
    def refine(self, mesh, minFaceCount):
        refinedmesh = mesh.subdivide_loop(number_of_iterations=1)
        if len(refinedmesh.triangles) >= minFaceCount: 
            return refinedmesh
        else:
            return self.refine(refinedmesh, minFaceCount)

    def simplify_by_decimation(self, mesh, maxFaceCount):
        simplifiedmesh = mesh.simplify_quadric_decimation(target_number_of_triangles=maxFaceCount)
        return simplifiedmesh

    def simplify_by_vertex_clustering(self, mesh, maxFaceCount):
        # in case we wanna use this option
        pass

    # function to showcase resampled models
    def render_before_after(self, meshpath, min, max):
        config.initialize()
        mesh_before = config.ml.load_mesh(meshpath)

        if len(mesh_before.triangles) <= min:
            mesh_after = self.refine(mesh_before, min)
        elif len(mesh_before.vertices) >= max:
            mesh_after = self.simplify_by_decimation(mesh_before, max)
        else:
            mesh_after = mesh_before

        # Render mesh
        config.rd.set_render_mode(render_mode.NORMAL)
        config.rd.show_world_axis(True)
        config.rd.add_mesh(mesh_before)
        config.rd.add_mesh(mesh_after.translate((1, 0, 0)))
        config.rd.launch_renderer()


rs = resampler()
rs.resample_all(100, 10000)
