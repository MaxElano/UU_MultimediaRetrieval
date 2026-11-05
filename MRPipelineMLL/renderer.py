import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import open3d as o3d
import numpy as np
from enum import Enum
import Utility.config as config
import Utility.utility as util

import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering


class RenderMode(Enum):
    #
    EMPTY = 0
    NORMAL = 1
    WIREFRAME_ONLY = 2
    MIXED = 3
    #
    def __init__(self, value):
        if len(self.__class__):
            # make links
            all = list(self.__class__)
            first, previous = all[0], all[-1]
            previous.next = self
            self.previous = previous
            self.next = first

class Renderer():
    all_meshes = []
    all_wireframes = []
    current_render_mode = RenderMode.NORMAL
    is_animating = False    
    
    visualizer = o3d.visualization.VisualizerWithKeyCallback()
    mesh_color = [1,1,1]
    
    def __init__(self, width=1280, height=720, background_color = [0.8, 0.8, 0.8]):    
            self.width = width
            self.height = height
            
            self.visualizer.create_window(width=self.width, height=self.height)
            
            self.render_options = self.visualizer.get_render_option()
            self.render_options.background_color = background_color 
            self.render_options.mesh_show_back_face = True

            self.visualizer.register_key_callback(ord("A"), Renderer.show_animation)
            self.visualizer.register_key_callback(ord("M"), Renderer.next_render_mode)
            self.visualizer.register_key_callback(ord("Y"), Renderer.import_random_mesh)
            self.visualizer.register_key_callback(ord("U"), Renderer.delete_all_meshes)

    def launch_renderer(self):
        self.visualizer.run()
        self.visualizer.destroy_window()

    def take_screenshot(self, file_path):
        steps = file_path.split('\\')
        if (steps[0] == "Data"):
            steps.pop(0)
        if (steps[0] == "Screenshots"):
            steps.pop(0)
        
        steps.insert(0, "Screenshots")
        steps.insert(0, "Data")
        folder_path = '\\'.join(steps[:-1])
        util.create_folder(folder_path)
            
        steps[-1] = steps[-1].split(".")[0] + ".png"
        
        self.visualizer.capture_screen_image(util.get_path(steps),do_render=True)
    
    def add_mesh(self, 
                 mesh,
                 label
    ):
        #config.lg.log(label)
        
        mesh.paint_uniform_color(self.mesh_color)
        self.all_meshes.append(mesh)
        wf = Renderer.generate_wireframe(mesh, label)
        self.all_wireframes.append(wf)
        match self.current_render_mode:
            case RenderMode.NORMAL:
                self.visualizer.add_geometry(mesh, reset_bounding_box=True)
            case RenderMode.WIREFRAME_ONLY:
                self.visualizer.add_geometry(wf, reset_bounding_box=True)
            case RenderMode.MIXED:
                self.visualizer.add_geometry(mesh, reset_bounding_box=True)
        
    def add_meshes(self, 
                   meshes: list[o3d.geometry.Geometry], 
                   labels: list[str],
    ):
        np.vectorize(self.add_mesh)(meshes,labels)        

    def remove_all_meshes(self):
        self.all_meshes = []
        self.all_wireframes = []
        self.visualizer.clear_geometries()
        self.visualizer.reset_view_point(reset_bounding_box = True)

    # Generate wireframe of SINGLE mesh
    def generate_wireframe(mesh, label):
        if (label == "World Axis"):
            return mesh
        
        wireframe = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
        return wireframe
    
    def add_world_axis(self):
        self.add_meshes(self.create_custom_world_axis(), ["World Axis","World Axis","World Axis"])
            
        #self.render_options.show_coordinate_frame = show

    def create_custom_world_axis(self):
        world_axis_meshes = []
        scale = 0.01
        mesh1 = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius= 1.0 * scale, cone_radius= 1.5 * scale, cylinder_height= 100.0 * scale, cone_height = 4.0 * scale)
        mesh1.paint_uniform_color(np.asarray([0,0,1]))
        world_axis_meshes.append(mesh1)
        mesh2 = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius= 1.0 * scale, cone_radius= 1.5 * scale, cylinder_height= 100.0 * scale, cone_height = 4.0 * scale)
        mesh2.paint_uniform_color(np.asarray([0,1,0]))
        r = mesh2.get_rotation_matrix_from_xyz((-np.pi / 2, 0, 0))
        mesh2.rotate(r, [0,0,0])
        world_axis_meshes.append(mesh2)
        mesh3 = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius= 1.0 * scale, cone_radius= 1.5 * scale, cylinder_height= 100.0 * scale, cone_height = 4.0 * scale)
        mesh3.paint_uniform_color(np.asarray([1,0,0]))
        r = mesh3.get_rotation_matrix_from_xyz((0, np.pi / 2, 0))
        mesh3.rotate(r, [0,0,0])
        world_axis_meshes.append(mesh3)

        return world_axis_meshes

    # ==== Render Mode Functions ====
    
    def set_mesh_color(self, color_array):
        self.mesh_color = color_array
        for mesh in self.all_meshes:
            mesh.paint_uniform_color(color_array)
    
    def set_background(self, color_array):
        self.render_options.background_color = color_array 
    
    # Function when setting render mode in code
    def set_render_mode(self, visual_option):
        config.rd.set_render_mode_button(visualizer=self.visualizer, visual_option=visual_option)

    # Function used in with keybinds
    def next_render_mode(vis):
        config.rd.set_render_mode_button(vis, config.rd.current_render_mode.next)

    def set_render_mode_button(self, visualizer, visual_option):
        self.current_render_mode = visual_option
        view_status = visualizer.get_view_status()
        visualizer.clear_geometries()
        visualizer.get_render_option().mesh_show_wireframe = False
        match visual_option:
            case RenderMode.EMPTY:
                pass
            case RenderMode.NORMAL:
                if(len(self.all_meshes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_meshes)
            case RenderMode.WIREFRAME_ONLY:
                if(len(self.all_wireframes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_wireframes)
            case RenderMode.MIXED:
                visualizer.get_render_option().mesh_show_wireframe = True
                if(len(self.all_meshes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_meshes)
        visualizer.set_view_status(view_status)

    def rotate_meshes(self, x=0, y=0, z=0):
        view_status = self.visualizer.get_view_status()
        for mesh in self.all_meshes:
            R = mesh.get_rotation_matrix_from_xyz((
                np.radians(x),
                np.radians(y),
                np.radians(z)
            )) 
            mesh.rotate(R, center=(0,0,0))
        self.visualizer.set_view_status(view_status)

    def zoom_camera(self, zoom=0.55):
        ctr = self.visualizer.get_view_control()
        ctr.set_zoom(zoom)

    # ==== Animation Functions ====
    # Used with keybind
    def show_animation(vis):
        if (config.rd.is_animating):
            vis.register_animation_callback(None)
        else:
            vis.register_animation_callback(Renderer.animation)
        config.rd.is_animating = not config.rd.is_animating
    
    # Used with animation callbacks
    def animation(vis):   
        ctr = vis.get_view_control()
        ctr.rotate(10.0,0.0)
        return False

  # ==== Fun Additions ====
    def import_random_mesh(vis):
        mesh, path = config.ml.load_random_mesh()
        config.rd.add_mesh(mesh=mesh, label=path)
        vis.reset_view_point(reset_bounding_box=True)
        
    def delete_all_meshes(vis):
        config.rd.all_meshes = []
        config.rd.all_wireframes = []
        vis.clear_geometries()

# GUI renderer; can be embedded into an existing window (i would hope)
# it can only render 1 mesh cause it should only ever render 1 mesh
class GUIRenderer:
    def __init__(self, window, background_color = [1,1,1]):
        self.window = window
        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)

        self.scene_widget.scene.set_background([*background_color, 1.0])

    def display_mesh_from_entry(self, entry):
        file_path = util.get_path(entry)
        mesh = o3d.io.read_triangle_mesh(file_path)
        self.display_mesh(mesh)

    def display_mesh(self, mesh):
        self.clear()
        mesh.compute_vertex_normals()

        material = rendering.MaterialRecord()
        material.shader = "defaultLit"

        self.scene_widget.scene.add_geometry("query_mesh", mesh, material)

        bounds = self.scene_widget.scene.bounding_box
        self.scene_widget.setup_camera(60.0, bounds, bounds.get_center())

    def clear(self):
        self.scene_widget.scene.clear_geometry()

