import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from renderer import RenderMode
import Utility.config as config
from enum import Enum
import open3d as o3d
import numpy as np
'''
Use this class to generate screenshots for the report. 
Max suggestion is to leave all the previous code in, so we can easily generate enormous new list of images when big changes happen.
If more renderer settings are needed, at them in renderer class.
Works with multiple meshes at once, but will be inside each other.
# Some tips:
 * The screenshot location can be a folder that is not created yet, it will be created for you! (OH how lucky I am to have such a LUXURIOUS Image Generator)
 * Screenshot name cannot include "." in final file name, because it will remove the dot and behind to insert ".png", so this is not necessary to do yourself

'''

# Template
# config.initialize(renderer_height=720, renderer_width=720)

# #necessary meshes
# mesh_path_1 = "Data\\NormalizedShapeDatabase\\Starship\\m1355.obj"
# mesh_path_2 = "Data\\NormalizedShapeDatabase\\Bed\\D00031.obj"

# # Load mesh
# mesh1 = config.ml.load_mesh(mesh_path_1)
# mesh2 = config.ml.load_mesh(mesh_path_2)

# # Render mesh
# config.rd.set_render_mode(render_mode.MIXED)
# config.rd.set_background([1,1,1])
# config.rd.set_mesh_color([1,0,0])
# config.rd.add_mesh(mesh1, mesh_path_1)
# config.rd.add_mesh(mesh2, mesh_path_2)
# config.rd.add_world_axis()
# config.rd.take_screenshot("I\\Want\\Way\\Too\\Many\\Files\\test.png")
# #config.rd.launch_renderer()

class CameraAngle(Enum): # gives an angle name and position
    FRONT = (0, 0, 0)
    BACK = (0, 0, 180)
    LEFT = (0, 0, 90)
    RIGHT = (0, 0, -90)
    TOP = (-90, 0, 0)
    BOTTOM = (90, 0, 0)

class ImageGenerator():
    def __init__(self):
        # Initialize image settings (the same for all images)
        config.initialize(renderer_height=1024, renderer_width=1024)

        config.rd.set_render_mode(RenderMode.MIXED)
        config.rd.set_background([1,1,1])
        config.rd.set_mesh_color([0,0.4,0.6])

    def generate_from_path(self,
                      paths,  # array where you give the paths
                      location = "Data\\Screenshots\\LostFiles", # where to save the screenshot to
                      title = "screenshot", #title of the screenshot
                      camera_angle = CameraAngle.FRONT
                      ):
        for path in paths:
            mesh = config.ml.load_mesh(path)
            config.rd.add_mesh(mesh, path)

        self.generate_screenshot(camera_angle, location, title)

    def generate_from_mesh(self,
                      meshes,  # array where you give the meshes
                      location = "Data\\Screenshots\\LostFiles", # where to save the screenshot to
                      title = "screenshot", #title of the screenshot
                      camera_angle = CameraAngle.FRONT,
                      show_face_normals = False
                      ):
        for mesh in meshes:
            if show_face_normals:
                # pcd = o3d.geometry.PointCloud()
                # pcd.points = o3d.utility.Vector3dVector(np.asarray(mesh.vertices))
                # pcd.estimate_normals()
                pass
                
        self.generate_screenshot(camera_angle, location, title)
    
    def generate_from_arrays(self,
                          vertices,  # array where you give the meshes
                          faces,
                          location = "Data\\Screenshots\\LostFiles", # where to save the screenshot to
                          title = "screenshot", #title of the screenshot
                          camera_angle = CameraAngle.FRONT,
                          show_face_normals = False
                          ):
        mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(vertices), o3d.utility.Vector3iVector(faces))
        self.generate_from_mesh([mesh], location, title, camera_angle, show_face_normals=show_face_normals)
    
    # rotation only rotates the meshes, it doesn't rotate everything!!!!!
    def generate_screenshot(self,
                           camera_angle,
                           location,
                           title):
        config.rd.add_world_axis()
        x, y, z = camera_angle.value
        #config.rd.set_camera_position(camera_angle.value)
        #config.rd.set_camera_target([0, 0, 0])
        #config.rd.zoom_camera()
        #config.rd.rotate_meshes(x, y, z)
        config.rd.take_screenshot(location + "\\" + title)        
        # Clear renderer
        config.rd.remove_all_meshes()

    def generate_images(self):
        # Necessary meshes
        mesh_path_1 = "Data\\NormalizedShapeDatabase\\Starship\\m1355.obj"
        mesh_path_2 = "Data\\NormalizedShapeDatabase\\Bed\\D00031.obj"
        # Load mesh
        mesh1 = config.ml.load_mesh(mesh_path_1)
        mesh2 = config.ml.load_mesh(mesh_path_2)
        # Render mesh
        config.rd.add_mesh(mesh1, mesh_path_1)
        config.rd.add_mesh(mesh2, mesh_path_2)
        config.rd.add_world_axis()

        config.rd.take_screenshot("ExampleTestScreenshot") 
        # Clear renderer
        config.rd.remove_all_meshes()

        # <-- Example image 2 -->
        # Necessary meshes
        mesh_path_1 = "Data\\NormalizedShapeDatabase\\Starship\\m1355.obj"
        # Load mesh
        mesh1 = config.ml.load_mesh(mesh_path_1)
        # Render mesh
        config.rd.add_mesh(mesh1, mesh_path_1)
        config.rd.add_world_axis()
        config.rd.take_screenshot("ExampleFolder\\ExampleTestScreenshot_2.jpg") 
        # Clear renderer
        config.rd.remove_all_meshes()


#mesh_path_1 = "Data\\NormalizedShapeDatabase\\Quadruped\\m94.npz"
#mesh_path_2 = "Data\\NormalizedShapeDatabase\\Bed\\D00031.obj"

#ig = imageGenerator()
#ig.generateFromPath([mesh_path_1])