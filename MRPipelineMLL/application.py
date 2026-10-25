import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
from renderer import GUIRenderer, RenderMode #surely ill need it and I will adapt it to work surely
import Utility.config as config
import Utility.utility as util
import open3d as o3d
import open3d.visualization.gui as gui


class MainApplication:
    def __init__(self):
        self.app = gui.Application.instance
        self.app.initialize()

        # setting query info ---------------------------------------------------
        self.db_shapes = util.get_all_files("Data\\OriginalShapeDatabase")

        #current query
        self.query_path = None
        self.query_mesh = None

        # setting the scene ----------------------------------------------------
        self.w = gui.Application.instance.create_window("Test GUI", 1080, 720)

        self.main_layout = gui.Vert(5, gui.Margins(10, 10, 10, 10))

        # top buttons
        self.top_buttons = gui.Horiz(5, gui.Margins(0,0,0,0))
        
        self.choose_button = gui.Button("Choose")
        self.choose_button.set_on_clicked(self.choose_mesh)
        self.top_buttons.add_child(self.choose_button)

        self.import_button = gui.Button("Import")
        self.import_button.set_on_clicked(self.import_mesh)
        self.top_buttons.add_child(self.import_button)

        self.main_layout.add_child(self.top_buttons)

        # 3D scene
        self.renderer = GUIRenderer(self.w)
        self.main_layout.add_child(self.renderer.scene_widget)

        # Status
        self.status = gui.Label("Choose or import a query mesh.")
        self.main_layout.add_child(self.status)

        # Compare button 
        self.compare_button = gui.Button("Compare")
        self.compare_button.set_on_clicked(self.compare)
        self.main_layout.add_child(self.compare_button)

        self.w.add_child(self.main_layout)

    def run(self):
         self.app.run()

    def choose_mesh(self):
        pass

    def import_mesh(self):
        pass

    def compare(self):
        pass

MainApplication().run()