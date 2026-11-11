import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
from renderer import GUIRenderer, RenderMode #surely ill need it and I will adapt it to work surely
import Utility.config as config
import Utility.utility as util
from Utility.imageGenerator import ImageGenerator
import open3d as o3d
import numpy as np #fah
import open3d.visualization.gui as gui
from Matching.matcher import Matcher

# note: first time you run it will create ALL display icons so it will take a while
class ShowNormalization:
    def __init__(self, db_original = "Data\\OriginalShapeDatabase", db_normalized = "Data\\NormalizedShapeDatabase"): 
        #config.initialize(skip_renderer=True)
        self.app = gui.Application.instance
        self.app.initialize()

        # setting query info ---------------------------------------------------
        self.db_original = db_original
        self.db_normalized = db_normalized
        self.db_shapes = util.get_all_files(db_original)
        self.db_norm_shapes = util.get_all_files(db_normalized)

        #current query
        self.query_path = None
        self.norm_path = None
        self.query_mesh = None
        self.norm_mesh = None

        # setting the scene ----------------------------------------------------
        self.w = gui.Application.instance.create_window("Shape Comparison", 1280, 720)

        self.main_layout = gui.Horiz(8, gui.Margins(10, 10, 10, 10))

        # LEFT SIDE TOP: controls and the 3d display -------------------------------

        # top buttons
        self.top_buttons = gui.Horiz(5, gui.Margins(2,2,2,2))
        
        self.choose_button = gui.Button("Choose")
        self.choose_button.set_on_clicked(self._on_choose_mesh)
        self.top_buttons.add_child(self.choose_button)

        # Compare button 
        self.normalize_button = gui.Button("Normalize")
        self.normalize_button.set_on_clicked(self._on_normalize)
        self.top_buttons.add_child(self.normalize_button)
    
        self.top_container = gui.Vert()
        self.top_container.add_child(self.top_buttons)
        self.w.add_child(self.top_container)

        # 3D scene
        # Als je de renderer toevoegd aan een subgroep dan gooit hij zieke fucking fittie
        # dus: dat doe ik nu seperately
        self.renderer = GUIRenderer(self.w)
        self.w.add_child(self.renderer.scene_widget)

        self.norm_renderer = GUIRenderer(self.w)
        self.w.add_child(self.norm_renderer.scene_widget)

        self.w.set_on_layout(self.on_layout)

    def run(self):
         self.app.run()

    def on_layout(self, layout):
        rect = self.w.content_rect
        left_width = int(rect.width * 0.50)
        right_width = rect.width - left_width

        top_height = int(rect.height * 0.11)

        scene_height = rect.height - top_height

        self.top_container.frame = gui.Rect(rect.x, rect.y, rect.width, top_height)

        self.renderer.scene_widget.frame = gui.Rect(rect.x, rect.y + top_height,left_width,scene_height)

        self.norm_renderer.scene_widget.frame =  gui.Rect(rect.x + left_width, rect.y + top_height,right_width,scene_height)

    def _on_cancel(self):
        self.w.close_dialog()

    def _on_done(self, path):
        self.w.close_dialog()
        self.query_path = path
        self.norm_path = path.replace("\\OriginalShapeDatabase\\", "\\NormalizedShapeDatabase\\").rsplit(".", 1)[0] + ".npz"
        print(self.norm_path)
        self.query_mesh = o3d.io.read_triangle_mesh(path)
        self.norm_mesh = config.ml.load_mesh(self.norm_path)
        self.renderer.display_mesh(self.query_mesh)
        self.renderer.add_world_axis()
        
    # should be able to 'choose' a mesh from the database
    # save this mesh to a set location in our structure
    # It displays this mesh and sets it as query mesh + location
    def _on_choose_mesh(self):
        dialog = gui.Dialog("Pick a mesh any mesh")

        em = self.w.theme.font_size
        layout = gui.Vert(2*em, gui.Margins(em, em, em, em))

        self.class_widget = gui.Combobox()
        classes = sorted(set(str(entry[1]) for entry in self.db_shapes))
        for category in classes:
            self.class_widget.add_item(category)

        self.class_widget.set_on_selection_changed(self._on_class_changed)
        layout.add_child(self.class_widget)

        self.mesh_widget = gui.ListView()
        layout.add_child(self.mesh_widget)

        # first time around its the first class
        mesh_list = [str(entry[2]) for entry in self.db_shapes 
                if entry[1] == classes[0]]
        self.mesh_widget.set_items(mesh_list)

        buttons = gui.Horiz(8, gui.Margins(2,2,2,2))
        cancel_button = gui.Button("Cancel")
        cancel_button.set_on_clicked(self._on_cancel)
        buttons.add_child(cancel_button)

        choice_button = gui.Button("Open")
        choice_button.set_on_clicked(self._on_choice)
        buttons.add_child(choice_button)

        layout.add_child(buttons)
        dialog.add_child(layout)

        self.w.show_dialog(dialog)

    def _on_class_changed(self, selected_class, *args): # capture all
        mesh_list = [str(entry[2]) for entry in self.db_shapes 
                     if entry[1] == selected_class]
        self.mesh_widget.set_items(mesh_list)

    def _on_choice(self):
        category = self.class_widget.selected_text
        shape = self.mesh_widget.selected_value
        path = os.path.abspath(os.path.join(self.db_original, category, shape))
        self._on_done(path)
    
    def _on_normalize(self):
        self.norm_renderer.display_mesh(self.norm_mesh)
        self.norm_renderer.add_world_axis()

        
# run using:
ShowNormalization().run()

