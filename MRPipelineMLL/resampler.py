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

    # resamples all outliers of a given database to be fairly uniform
    def resample_all(database, min, max):
        '''
        foreach shape in db
            if avg size: continue
            if too small:
                newmesh = refine(shape)
            if too big:
                newmesh = refine(shape)
            overwrite .obj file 
        '''
        pass

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






#code pasted to keep everything in this file for now
config.initialize()
mesh_path = "Data\\NormalizedShapeDatabase\\Biplane\\m1120.obj"
rs = resampler()
rs.render_before_after(mesh_path, 100, 10000)



'''# Load mesh
mesh1 = config.ml.load_mesh(mesh_path_1)
mesh2 = rs.refine(mesh1, 1000)
o3d.t.io.write_triangle_mesh(os.path(mesh_path_1), mesh2)
'''