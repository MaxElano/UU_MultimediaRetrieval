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
from FeatureExtraction.featureTester import ElemFeature, DistFeature
import matplotlib.pyplot as plt

# note: first time you run it will create ALL display icons so it will take a while
class ShowFeatureExtraction:
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

        self.meta_db, self.global_features, self.distribution_features = self.get_feature_tables("Data\\DataAnalysis\\featureDatabases.npz", "Data\\DataAnalysis\\distributionDatabases.npz")

        # setting the scene ----------------------------------------------------
        self.w = gui.Application.instance.create_window("Shape Comparison", 1280, 720)

        self.main_layout = gui.Horiz(8, gui.Margins(10, 10, 10, 10))

        # LEFT SIDE TOP: controls and the 3d display -------------------------------

        # top buttons
        self.top_buttons = gui.Horiz(5, gui.Margins(2,2,2,2))
        
        self.choose_button = gui.Button("Choose")
        self.choose_button.set_on_clicked(self._on_choose_mesh)
        self.top_buttons.add_child(self.choose_button)

        self.import_button = gui.Button("Import")
        self.import_button.set_on_clicked(self._on_import_mesh)
        self.top_buttons.add_child(self.import_button)

        # Compare button 
        self.extract_button = gui.Button("Extract")
        self.extract_button.set_on_clicked(self._on_extract)
        self.top_buttons.add_child(self.extract_button)
    
        self.top_container = gui.Vert()
        self.top_container.add_child(self.top_buttons)
        self.w.add_child(self.top_container)

        self.right_side = gui.Vert(5, gui.Margins(2,2,2,2))

        self.features = gui.Label("Choose or import a query mesh.")
        self.right_side.add_child(self.features)


        self.histogram_widget = gui.ImageWidget()
        self.right_side.add_child(self.histogram_widget)

        self.w.add_child(self.right_side)

        # 3D scene
        # Als je de renderer toevoegd aan een subgroep dan gooit hij zieke fucking fittie
        # dus: dat doe ik nu seperately
        self.renderer = GUIRenderer(self.w)
        self.w.add_child(self.renderer.scene_widget)

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

        self.right_side.frame =  gui.Rect(rect.x + left_width, rect.y + top_height,right_width,scene_height)


    # should be able to 'import' a mesh
    # save this mesh to a set location in our structure
    # It displays this mesh and sets it as query mesh + location
    def _on_import_mesh(self):
        dialog = gui.FileDialog(gui.FileDialog.OPEN, "Import a mesh", self.w.theme)

        dialog.add_filter(".obj", "3D meshes")
        dialog.set_on_cancel(self._on_cancel)
        dialog.set_on_done(self._on_done)
        self.w.show_dialog(dialog)

    def _on_cancel(self):
        self.w.close_dialog()

    def _on_done(self, path):
        self.w.close_dialog()
        self.query_path = path
        self.norm_path = path.replace("\\OriginalShapeDatabase\\", "\\NormalizedShapeDatabase\\").rsplit(".", 1)[0] + ".npz"
        self.query_mesh = o3d.io.read_triangle_mesh(path)
        self.norm_mesh = config.ml.load_mesh(self.norm_path)
        self.renderer.display_mesh(self.query_mesh)
        
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
    
    def _on_extract(self):
        mesh_name = os.path.basename(self.norm_path)
        row = np.where(self.meta_db[:,1] == mesh_name)[0][0]
        index = int(self.meta_db[row, 0])

        feature_row = self.global_features[self.global_features[:,0] == index][0]

        output = f"Mesh: {mesh_name}\n\nElement Features:\n"
        for feature in ElemFeature:
                value = feature_row[feature.value[0]]
                output += f"{feature.value[1]}: {value:.4f}\n"
        self.display_histograms(index)
        
        self.features.text = output

    def display_histograms(self, index):
        fig, axes = plt.subplots(5, 1, figsize=(7, 9))

        for ax, feature in zip(axes, DistFeature):
            table = self.distribution_features[feature.name]

            match = table[table[:, 0] == index]

            if len(match) == 0:
                ax.set_title(f"{feature.value[1]} - Not found")
                continue

            histogram = match[0, 1:]

            ax.bar(range(len(histogram)), histogram, width=1.0)
            ax.set_title(feature.value[1])
            ax.set_ylabel("Frequency")
            ax.set_xlim(0, len(histogram))

        plt.tight_layout()

        fig.canvas.draw()
        image = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()

        self.histogram_widget.update_image(o3d.geometry.Image(image))


    def get_feature_tables(self, location_global_features, location_distributions):
        feature_databases = util.load_numpy_file(location_global_features)
        meta_db = feature_databases['metadata']
        feature_db = feature_databases['features']
        dist_db = util.load_numpy_file(location_distributions)
        return meta_db, feature_db, dist_db

        
# run using:
ShowFeatureExtraction().run()

