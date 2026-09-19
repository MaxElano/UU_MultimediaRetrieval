import open3d as o3d
import numpy as np
from enum import Enum

class render_mode(Enum):
    BLACK_BACKGROUND = 0
    SMOOTHSHADE = 1
    WIREFRAME = 2
    WIREFRAME_ON_SHADED = 3

class renderer():
    all_meshes = []
    all_wireframes = []
    
    def __init__(self, width=1280, height=720, background_color = [0, 0, 0]):
        self.world_axis_mesh = renderer.create_world_axis()

        self.width = width
        self.height = height

        self.visualizer = o3d.visualization.Visualizer()
        self.visualizer.create_window(width=width, height=height)

        self.render_options = self.visualizer.get_render_option()
        self.render_options.background_color = background_color 

    def launch_renderer(self):
        self.visualizer.run()
        self.visualizer.destroy_window()

    def add_mesh(self, 
                 mesh: o3d.geometry.Geometry, 
    ):
        self.all_meshes.append(mesh)
        self.all_wireframes.append(renderer.generate_wireframe(mesh))
        self.visualizer.add_geometry([mesh])
    
    def add_meshes(self, 
                   meshes: list[o3d.geometry.Geometry], 
    ):
        np.vectorize(self.add_mesh)(meshes)        
        return
        
        if (show_world_axis):
            world_axis = self.create_world_axis()
            meshes = np.append(meshes, world_axis)
        
        match visual_option:
            case render_mode.SMOOTHSHADE:
                o3d.visualization.draw_geometries(meshes, width=self.width, height=self.height)
            case render_mode.WIREFRAME_ON_SHADED:
                o3d.visualization.draw_geometries(meshes, width=self.width, height=self.height, mesh_show_wireframe=True)
            case render_mode.WIREFRAME:
                # We first need to obtain a lineset of the wireframe if we don't want to render the mesh itself
                if (show_world_axis):
                    wireframes = np.vectorize(o3d.geometry.LineSet.create_from_triangle_mesh)(meshes[:-1])
                    wireframes = np.append(wireframes, meshes[-1])
                else:
                    wireframes = np.vectorize(o3d.geometry.LineSet.create_from_triangle_mesh)(meshes)
                o3d.visualization.draw_geometries(wireframes, width=self.width, height=self.height)
 
    def create_world_axis(cls) -> o3d.geometry.LineSet:
        line_endpoints = [
            [0, 0, 0],
            [1, 0, 0], # x
            [0, 1, 0], # y UP
            [0, 0, 1]  # z
        ]
        line_indices = [[0, 1], [0, 2], [0, 3]]
        
        world_axis = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(line_endpoints),
            lines=o3d.utility.Vector2iVector(line_indices),
        )
        world_axis.colors = o3d.utility.Vector3dVector(np.asarray(line_endpoints)[1:]) 
        
        return world_axis

    # Generate wireframe of SINGLE mesh
    def generate_wireframe(mesh):
        wireframe =o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
        return wireframe
    
    def show_world_axis(show):
        pass

    def set_render_mode(visual_option):
        pass
        # match visual_option:
        #     case render_mode.SMOOTHSHADE:
        #         self.render_options.
        #     case render_mode.WIREFRAME_ON_SHADED:

        #     case render_mode.WIREFRAME:
                