import open3d as o3d
import numpy as np
from enum import Enum
import config

class render_mode(Enum):
    #
    EMPTY = 0
    NORMAL = 1
    WIREFRAME_ONLY = 2
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

    def add_mesh(self, 
                 mesh: o3d.geometry.Geometry, 
                 label: str,
    ):
        config.lg.log(label)
        
        self.all_meshes.append(mesh)
        wf = renderer.generate_wireframe(mesh)
        self.all_wireframes.append(wf)
        match self.current_render_mode:
            case render_mode.NORMAL:
                self.visualizer.add_geometry(mesh)
            case render_mode.WIREFRAME_ONLY:
                self.visualizer.add_geometry(wf)
        
    def add_meshes(self, 
                   meshes: list[o3d.geometry.Geometry], 
                   labels: list[str],
    ):
        np.vectorize(self.add_mesh)(meshes,labels)        

    # Generate wireframe of SINGLE mesh
    def generate_wireframe(mesh):
        wireframe = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
        return wireframe
    
    def show_world_axis(self, show):
        self.render_options.show_coordinate_frame = show



    # ==== Render Mode Functions ====
    
    # Function when setting render mode in code
    def set_render_mode(self, visual_option):
        config.rd.set_render_mode_button(visualizer=self.visualizer, visual_option=visual_option)

    # Function used in with keybinds
    def next_render_mode(vis):
        config.rd.set_render_mode_button(vis, config.rd.current_render_mode.next)

    def set_render_mode_button(self, visualizer, visual_option):
        self.current_render_mode = visual_option
        view_status = visualizer.get_view_status()
        match visual_option:
            case render_mode.EMPTY:
                visualizer.clear_geometries()
            case render_mode.NORMAL:
                visualizer.clear_geometries()
                if(len(self.all_meshes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_meshes)
            case render_mode.WIREFRAME_ONLY:
                visualizer.clear_geometries()
                if(len(self.all_wireframes) > 0):
                    np.vectorize(visualizer.add_geometry)(self.all_wireframes)
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
