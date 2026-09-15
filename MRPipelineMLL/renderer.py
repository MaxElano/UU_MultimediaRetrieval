import open3d as o3d
import numpy as np
from enum import Enum

class render_mode(Enum):
    BLACK_BACKGROUND = 0
    SMOOTHSHADE = 1
    WIREFRAME = 2
    WIREFRAME_ON_SHADED = 3
    WORLD_AXES = 4

class renderer():
    def __init__(self):
        pass

    # Visualize a mesh
    def visualize_mesh(self, mesh, visual_option):
        match visual_option:
            case render_mode.SMOOTHSHADE:
                o3d.visualization.draw_geometries([mesh], width=1280, height=720)
            case render_mode.WIREFRAME_ON_SHADED:
                o3d.visualization.draw_geometries([mesh], width=1280, height=720, mesh_show_wireframe=True)
            case render_mode.WIREFRAME:
                # We first need to obtain a lineset of the wireframe if we don't want to render the mesh itself
                wireframe = o3d.geometry.LineSet.create_from_triangle_mesh(mesh) 
                o3d.visualization.draw_geometries([wireframe], width=1280, height=720)
            case render_mode.WORLD_AXES:
                # Display the mesh including a world axis system.

                # Create the endpoints of each line. Each line is unit-length.
                # For the world axes, the origin is shared by all lines. So we have 4 endpoints in total
                line_endpoints = [
                    [0, 0, 0],
                    [1, 0, 0],
                    [0, 1, 0],
                    [0, 0, 1]
                ]

                # List of indices into the 'line_endpoints' list, which describes which endpoints form which line
                line_indices = [[0, 1], [0, 2], [0, 3]]

                # Create a line set from the endpoints and indices
                world_axes = o3d.geometry.LineSet(
                    points=o3d.utility.Vector3dVector(line_endpoints),
                    lines=o3d.utility.Vector2iVector(line_indices),
                )

                # Render the line set and the mesh
                o3d.visualization.draw_geometries([mesh, world_axes], width=1280, height=720)
            case render_mode.BLACK_BACKGROUND:
                # Create visualizer
                vis = o3d.visualization.Visualizer()
                vis.create_window()
                vis.add_geometry(mesh)

                # Set render options (e.g. background color)
                opt = vis.get_render_option()
                opt.background_color = np.asarray([0, 0, 0])

                # Run the visualizer
                vis.run()
                vis.destroy_window()
