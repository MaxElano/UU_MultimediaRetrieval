import open3d as o3d
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

class resampler_open3d():
    def __init__(self):
        pass

    # resamples all outliers of a given database (which should be a copy of the og) to be fairly uniform
    def resample_all(self, min = 3000, max = 10000, folder = "Data\\NormalizedShapeDatabase"):
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
                if len(mesh_before.vertices) <= min:
                    mesh_after = self.refine(mesh_before, min)
                    o3d.io.write_triangle_mesh(file_path, mesh_after)
                    refined_count += 1
                elif len(mesh_before.vertices) >= max:
                    mesh_after = self.simplify_by_decimation(mesh_before, max, max*2)
                    o3d.io.write_triangle_mesh(file_path, mesh_after)
                    simplified_count +=1
        print(f"Resampling done. Refined {refined_count} shapes. Simplified {simplified_count} shapes.")    

    def resample_one_mesh(self, mesh, min = 3000, max = 10000):
        if len(mesh.vertices) <= min:
            return self.refine(mesh, min)
        elif len(mesh.vertices) >= max:
            return self.simplify_by_decimation(mesh, max, max*2)  
        return mesh

    # refines a mesh so that its number of faces is higher than a given number
    def refine(self, mesh, min_vertices):
        # checks if the mesh is refined enough- non-manifold meshes sometimes lead to high nr of triangles while vertices stay low, so an extra check is done
        if len(mesh.vertices) >= min_vertices or len(mesh.triangles) >= 100000: 
            return mesh

        # if the vertices have already be refined somewhat, loop algorithms is applied
        if len(mesh.vertices) >= min_vertices/2:
            return self.refine(mesh.subdivide_loop(number_of_iterations=1), min_vertices)
        else: 
            return self.refine(mesh.subdivide_midpoint(number_of_iterations=1), min_vertices)

    # simplify a mesh to have a certain amount of faces
    def simplify_by_decimation(self, mesh, max_vertices, target_triangles, iterations=0):
        # checks if mesh is in the target area, or recursion has gone for too long (in which case the operation is probably not possible due to a broken mesh)
        if len(mesh.vertices) <= max_vertices or iterations > 5: 
            return mesh
        
        simplifiedmesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
        # iterates with smaller triangle target until vertices are the correct amount
        return self.simplify_by_decimation(simplifiedmesh, max_vertices, int(target_triangles*0.8), iterations+1)


    # function to showcase resampled models
    def render_before_after(self, meshpath, min = 3000, max = 10000):
        config.initialize()
        mesh_before = config.ml.load_mesh(meshpath)
        print(mesh_before)        

        if len(mesh_before.vertices) <= min:
            mesh_after = self.refine(mesh_before, min)
        elif len(mesh_before.vertices) >= max:
            mesh_after = self.simplify_by_decimation(mesh_before, max, max*2)  
        else:
            mesh_after = mesh_before

        print(mesh_after)
        # Render mesh
        config.rd.set_render_mode(render_mode.NORMAL)
        config.rd.show_world_axis(True)
        config.rd.add_mesh(mesh_before)
        config.rd.add_mesh(mesh_after.translate((1, 0, 0)))
        config.rd.launch_renderer()


class resampler_pymeshlab():
    def __init__(self):
        pass

    def resample_one_mesh(self, mesh, min = 5000, max = 10000):
        vertex_count = mesh.current_mesh().vertex_number()
        if vertex_count <= min:
            return self.refine_copied(mesh)
        elif vertex_count >= max:
            return self.decimate_copied(mesh)  
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
        while mesh.current_mesh().vertex_number() > max_vertices:
            # still needs to be tested if this is the best function for it
            mesh.meshing_isotropic_explicit_remeshing(iterations=1)
        return mesh

    def refine_copied(self, mesh_lowpoly, target_edge_length = 0.02, itrs = 3):
        mesh_lowpoly.meshing_isotropic_explicit_remeshing(
            targetlen=pml.PureValue(target_edge_length), iterations=itrs)


    def decimate_copied(self, mesh_highpoly, target_edge_length = 0.02, itrs = 3):
        mesh_highpoly.meshing_isotropic_explicit_remeshing(
            targetlen=pml.PureValue(target_edge_length), iterations=itrs)



#rs = resampler()
#rs.resample_all(3000, 10000)

