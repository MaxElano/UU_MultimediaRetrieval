from renderer import render_mode
import config
import os
import pymeshlab  as pml

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

    def resample_one_mesh(self, mesh, min = 5000, max = 10000):
        if len(mesh.vertices) <= min:
            return self.refine(mesh, min)
        elif len(mesh.vertices) >= max:
            return self.simplify_by_decimation(mesh, max, max*2)  
        return mesh

    # refines a mesh so that its number of faces is higher than a given number
    def refine(self, mesh, min_vertices):
        # checks if the mesh is refined enough- non-manifold meshes sometimes lead to high nr of triangles while vertices stay low, so an extra check is done
        while mesh.current_mesh().vertex_number() < min_vertices and mesh.current_mesh().face_number() < 100000:
            # still needs to be tested if this is the best function for it
            mesh.meshing_isotropic_explicit_remeshing(iterations=1)
        return mesh


    # simplify a mesh to have a certain amount of vertices
    def simplify_by_decimation(self, mesh, max_vertices):
        percentage = (max_vertices/mesh.current_mesh().vertex_number())
        mesh.meshing_decimation_quadric_edge_collapse(targetperc=percentage)
        return mesh
    

    # function to showcase resampled models
    def render_before_after(self, meshpath, min = 5000, max = 10000):
        config.initialize()
        mesh_before = config.ml.load_pymeshlab(meshpath)
        vertex_count = mesh_before.current_mesh().vertex_number()
        print(f"mesh with {vertex_count} vertices and {mesh_before.current_mesh().face_number()} faces")       
        
        if vertex_count <= min:
            mesh_after = self.refine(mesh_before, min)
        elif vertex_count >= max:
            mesh_after = self.simplify_by_decimation(mesh_before, max)  
        else:
            mesh_after = mesh_before

        print(f"mesh with {mesh_after.current_mesh().vertex_number()} vertices and {mesh_after.current_mesh().face_number()} faces")  
        '''  
        # Render mesh
        config.rd.set_render_mode(render_mode.NORMAL)
        config.rd.add_mesh(mesh_before, meshpath)
        config.rd.add_mesh(mesh_after.translate((1, 0, 0)), meshpath)
        config.rd.launch_renderer()
        '''


rs = resampler()
rs.render_before_after("Data\\OriginalShapeDatabase\\Bed\\D00735.obj")

