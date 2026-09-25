import open3d as o3d
import numpy as np
from renderer import render_mode
import config

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

    # refines a mesh so that its number of faces is higher than a given number
    def refine(self, mesh, minFaceCount):
        refinedmesh = mesh.subdivide_loop(number_of_iterations=1)
        if len(refinedmesh.triangles) >= minFaceCount: 
            return refinedmesh
        else:
            return self.refine(refinedmesh, minFaceCount)

    def simplify():
        pass



#code pasted to keep everything in this file for now
config.initialize()
mesh_path_1 = "Data\\OriginalShapeDatabase\\Computer\\m1769.obj"
rs = resampler()

# Load mesh
mesh1 = config.ml.load_mesh(mesh_path_1)
mesh2 = rs.refine(mesh1, 1000)

# Render mesh
config.rd.set_render_mode(render_mode.NORMAL)
config.rd.show_world_axis(True)
config.rd.add_mesh(mesh1)
config.rd.add_mesh(mesh2.translate((1, 0, 0)))
config.rd.launch_renderer()