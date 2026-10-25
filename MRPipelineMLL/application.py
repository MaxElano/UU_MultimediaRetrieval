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
        self.similar_amt = 0

        # setting the scene ----------------------------------------------------
        self.w = gui.Application.instance.create_window("Test GUI", 1080, 720)

        self.main_layout = gui.Horiz(8, gui.Margins(10, 10, 10, 10))

        # LEFT SIDE TOP: controls and the 3d display -------------------------------
        #self.left_panel = gui.Vert(8, gui.Margins(0,0,0,0))

        # top buttons
        self.top_buttons = gui.Horiz(5, gui.Margins(0,0,0,0))
        
        self.choose_button = gui.Button("Choose")
        self.choose_button.set_on_clicked(self.choose_mesh)
        self.top_buttons.add_child(self.choose_button)

        self.import_button = gui.Button("Import")
        self.import_button.set_on_clicked(self.import_mesh)
        self.top_buttons.add_child(self.import_button)

        #self.w.add_child(self.top_buttons)
        self.top_container = gui.Vert()
        self.top_container.add_child(self.top_buttons)
        self.w.add_child(self.top_container)

        # LEFT SIDE BOTTOM: status and comparison button ---------------------------
        # Status
        self.bottom = gui.Vert(5, gui.Margins(0,0,0,0))

        self.status = gui.Label("Choose or import a query mesh.")
        #self.left_panel.add_child(self.status)
        self.bottom.add_child(self.status)

        # Compare button 
        self.compare_button = gui.Button("Compare")
        self.compare_button.set_on_clicked(self.compare)
        #self.left_panel.add_child(self.compare_button)
        self.bottom.add_child(self.compare_button)
        
        self.bottom_container = gui.Vert()
        self.bottom_container.add_child(self.bottom)
        self.w.add_child(self.bottom_container)

        #self.w.add_child(self.bottom)
        #self.w.add_child(self.left_panel)
        #self.main_layout.add_child(self.left_panel)

        # RIGHT SIDE: results -----------------------------------------------
        self.right_panel = gui.Vert(8, gui.Margins(0,0,0,0))

        self.similarity_label = gui.Label(f"{self.similar_amt} most similar shapes")
        self.right_panel.add_child(self.similarity_label)
        self.results_scroll = gui.ScrollableVert(8, gui.Margins(2,2,2,2))
        self.results_content = gui.Vert(8, gui.Margins(2,2,2,2))
        self.results_scroll.add_child(self.results_content)
        self.right_panel.add_child(self.results_scroll)

        self.w.add_child(self.right_panel)
        #self.main_layout.add_child(self.right_panel)
        #self.w.add_child(self.main_layout)

        # 3D scene
        # Als je de renderer toevoegd aan een subgroep dan gooit hij zieke fucking fittie
        # dus: dat doe ik nu seperately
        self.renderer = GUIRenderer(self.w)
        self.w.add_child(self.renderer.scene_widget)

        self.w.set_on_layout(self.on_layout)

        self.dummy_display()

    def run(self):
         self.app.run()

    def on_layout(self, layout):
        rect = self.w.content_rect
        left_width = int(rect.width * 0.50)
        right_width = rect.width - left_width

        top_height = int(rect.height * 0.1)
        bottom_height = int(rect.height*0.2)

        scene_height = rect.height - top_height - bottom_height

        self.top_container.frame = gui.Rect(rect.x, rect.y, left_width, top_height)

        self.renderer.scene_widget.frame = gui.Rect(rect.x, rect.y + top_height,left_width,scene_height)

        self.bottom_container.frame = gui.Rect(rect.x, rect.y + top_height + scene_height, left_width, bottom_height)
        
        self.right_panel.frame = gui.Rect(rect.x + left_width, rect.y, right_width, rect.height)
        
    def dummy_display(self):
        # dummy test scroll wheel
        for i in range(50):
            self.results_content.add_child(gui.Label(f"imagine a shape {i + 1}  |  Similarity: {1.0 / (i + 1):.4f}"))
        # dummy test drawing a mesh AAAAAAAA
        mesh = self.db_shapes[0]
        self.renderer.display_mesh_from_entry(mesh)

    # should use the database from which you can choose 1 mesh
    # It displays this mesh and sets it as query mesh + location
    def choose_mesh(self):
        pass

    # should be able to 'import' a mesh
    # save this mesh to a set location in our structure
    # It displays this mesh and sets it as query mesh + location
    def import_mesh(self):
        pass

    # only works if there is a query mesh
    # takes the query mesh location and computes a similarity score for EVERY mesh
    # returns either the K or the ones under a certain threshold (implement diffeerent options)
    # shows these in the right panel as : image + similarity score
    def compare(self):
        pass

MainApplication().run()
