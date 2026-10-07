import open3d as o3d
import numpy as np
from enum import Enum
import config
import utility as util

class render_mode(Enum):
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

class renderer():
    all_meshes = []
    all_wireframes = []
    current_render_mode = render_mode.NORMAL
    is_animating = False    
    
    visualizer = o3d.visualization.VisualizerWithKeyCallback()
    mesh_color = [1,1,1]
    
    def __init__(self, width=1280, height=720, background_color = [0.8, 0.8, 0.8]):    
            self.width = width
            self.height = height
            
            self.visualizer.create_window(width=self.width, height=self.height)
            
            self.render_options = self.visualizer.get_render_option()
            self.render_options.background_color = background_color 

            self.visualizer.register_key_callback(ord("A"), renderer.show_animation)
            self.visualizer.register_key_callback(ord("M"), renderer.next_render_mode)
            self.visualizer.register_key_callback(ord("Y"), renderer.import_random_mesh)
            self.visualizer.register_key_callback(ord("U"), renderer.delete_all_meshes)

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
        for i in range(len(steps) - 1):
            util.create_folder('\\'.join(steps[:i + 1]))
            
        steps[-1] = steps[-1].split(".")[0] + ".png"
        
        self.visualizer.capture_screen_image(util.get_path(steps),do_render=True)
    
    def add_mesh(self, 
                 mesh,
                 label
    ):
        config.lg.log(label)
        
        mesh.paint_uniform_color(self.mesh_color)
        self.all_meshes.append(mesh)
        wf = renderer.generate_wireframe(mesh, label)
        self.all_wireframes.append(wf)
        match self.current_render_mode:
            case render_mode.NORMAL:
                self.visualizer.add_geometry(mesh, reset_bounding_box=True)
            case render_mode.WIREFRAME_ONLY:
                self.visualizer.add_geometry(wf, reset_bounding_box=True)
            case render_mode.MIXED:
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
            case render_mode.EMPTY:
                pass
            case render_mode.NORMAL:
                if(len(self.all_meshes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_meshes)
            case render_mode.WIREFRAME_ONLY:
                if(len(self.all_wireframes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_wireframes)
            case render_mode.MIXED:
                visualizer.get_render_option().mesh_show_wireframe = True
                if(len(self.all_meshes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_meshes)
        visualizer.set_view_status(view_status)


    # ==== Animation Functions ====
    # Used with keybind
    def show_animation(vis):
        if (config.rd.is_animating):
            vis.register_animation_callback(None)
        else:
            vis.register_animation_callback(renderer.animation)
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
