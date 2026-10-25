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

class MainApplication:
    def __init__(self, db = "Data\\OriginalShapeDatabase"): 
        config.initialize(skip_renderer=True)

        self.app = gui.Application.instance
        self.app.initialize()

        # setting query info ---------------------------------------------------
        self.db = db
        self.db_shapes = util.get_all_files(db)

        #current query
        self.query_path = None
        self.query_mesh = None
        self.similar_amt = 0
        # has every shape in the database and their corresponding similarity
        self.similarity_shapes = []

        # setting the scene ----------------------------------------------------
        self.w = gui.Application.instance.create_window("Test GUI", 1080, 720)

        self.main_layout = gui.Horiz(8, gui.Margins(10, 10, 10, 10))

        # LEFT SIDE TOP: controls and the 3d display -------------------------------

        # top buttons
        self.top_buttons = gui.Horiz(5, gui.Margins(0,0,0,0))
        
        self.choose_button = gui.Button("Choose")
        self.choose_button.set_on_clicked(self._on_choose_mesh)
        self.top_buttons.add_child(self.choose_button)

        self.import_button = gui.Button("Import")
        self.import_button.set_on_clicked(self._on_import_mesh)
        self.top_buttons.add_child(self.import_button)

        self.top_container = gui.Vert()
        self.top_container.add_child(self.top_buttons)
        self.w.add_child(self.top_container)

        # LEFT SIDE BOTTOM: status and comparison button ---------------------------
        # Status
        self.bottom = gui.Vert(5, gui.Margins(0,0,0,0))

        self.status = gui.Label("Choose or import a query mesh.")
        self.bottom.add_child(self.status)

        # Compare button 
        self.compare_button = gui.Button("Compare")
        self.compare_button.set_on_clicked(self._on_comparison)
        self.bottom.add_child(self.compare_button)
        
        self.bottom_container = gui.Vert()
        self.bottom_container.add_child(self.bottom)
        self.w.add_child(self.bottom_container)

        # RIGHT SIDE: results -----------------------------------------------
        self.right_panel = gui.Vert(8, gui.Margins(0,0,0,0))

        self.similarity_label = gui.Label(f"{self.similar_amt} most similar shapes")
        self.right_panel.add_child(self.similarity_label)
        self.results_scroll = gui.ScrollableVert(8, gui.Margins(2,2,2,2))
        self.results_content = gui.Vert(8, gui.Margins(2,2,2,2))
        self.results_scroll.add_child(self.results_content)
        self.right_panel.add_child(self.results_scroll)

        self.w.add_child(self.right_panel)

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
        # dummy test scroll
        self.similar_amt = 50
        for i in range(50):
            #self.results_content.add_child(gui.Label(f"imagine a shape {i + 1}  |  Similarity: {1.0 / (i + 1):.4f}"))
            similarity = (1.0/(i+1))
            self.similarity_shapes.append(self.db_shapes[i])

            self.add_result(self.db_shapes[i], similarity)
        #self.display_results()
        # dummy test drawing a mesh AAAAAAAA
        mesh = self.db_shapes[0]
        self.renderer.display_mesh_from_entry(mesh)

    # should use the database from which you can choose 1 mesh
    # It displays this mesh and sets it as query mesh + location
    def _on_import_mesh(self):
        dialog = gui.FileDialog(gui.FileDialog.OPEN, "Choose a mesh", self.w.theme)

        dialog.add_filter(".obj", "3D meshes")
        dialog.set_on_cancel(self._on_cancel)
        dialog.set_on_done(self._on_done)
        self.w.show_dialog(dialog)

    def _on_cancel(self):
        self.w.close_dialog()

    def _on_done(self, path):
        self.w.close_dialog()
        self.query_path = path
        self.query_mesh = o3d.io.read_triangle_mesh(path)
        self.renderer.display_mesh(self.query_mesh)
        
        self.status.text = f"Loaded: {os.path.split(path)[1]}"

    # should be able to 'import' a mesh
    # save this mesh to a set location in our structure
    # It displays this mesh and sets it as query mesh + location
    def _on_choose_mesh(self):
        dialog = gui.Dialog("Pick a mesh any mesh")

        em = self.w.theme.font_size
        layout = gui.Vert(2*em, gui.Margins(em, em, em, em))

        cancel_button = gui.Button("X")
        cancel_button.set_on_clicked(self._on_cancel)
        layout.add_child(cancel_button)

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

        choice_button = gui.Button("Import")
        choice_button.set_on_clicked(self._on_choice)
        layout.add_child(choice_button)

        dialog.add_child(layout)

        self.w.show_dialog(dialog)

    def _on_class_changed(self, selected_class, *args):
        mesh_list = [str(entry[2]) for entry in self.db_shapes 
                     if entry[1] == selected_class]
        self.mesh_widget.set_items(mesh_list)

    def _on_choice(self):
        category = self.class_widget.selected_text
        shape = self.mesh_widget.selected_value
        path = os.path.join(self.db, category, shape)
        self._on_done(path)
    
    def _on_comparison(self):
        # extract features of the query shape

        # compute distances of query shape to all db shapes

        # sort distances from low to high

        # present similar shapes
        self.get_similars()
        self.display_similars()
    
    # only works if there is a query mesh
    # takes the query mesh location and computes a similarity score for EVERY mesh
    # returns either the K or the ones under a certain threshold (implement diffeerent options)


    # present the K best-matching shapes, plus their distances to the query, 
    # Alternative: set a distance threshold t and present all shapes in the 
    # database having a distance to the query lower than t. 
    def get_similars(self, t = None, K = None):
        pass

    # takes a list of shapes and their similarity scores
    # assuming an ordered list with similarity scores ranked high -> low
    # [index, sim_score]
    #TODO: DEPENDS ON OUTPUT FROM SIMILARITY COMPUTATION!!!
    def display_similars(self):
        if self.similarity_shapes is None:
            return
            # update text with: 0 shapes found, something went wrong
        for shape in self.similarity_shapes:
            pass
            #index, sim_score = shape
            #TODO: call add_result for every shape
        #TODO: Change status to give the x amt of similar shapes


    # takes the thingy from get_all_files
    # which is: ['database location', 'category', 'object name']
    def add_result(self, file, similarity, display_db = "Data\\Screenshots\\Displayimages", img_size = 150):
        if not os.path.isdir(display_db):
            ig = ImageGenerator()
            ig.generate_display_images()
        _, shape_class, file_name = file
        img_name = os.path.splitext(file_name)[0] + ".png"
        img_path = os.path.join(display_db, shape_class, img_name)

        if os.path.isfile(img_path):
            img = o3d.io.read_image(img_path)
            img = self.resize_image(img, img_size)
        else:
            img = o3d.geometry.Image(np.full((img_size,img_size,3), 255, dtype=np.uint8))
        img_widget = gui.ImageWidget(img)
        img_layout = gui.Horiz()
        img_layout.add_child(img_widget)

        sim_info = gui.Vert()
        sim_info.add_child(gui.Label(file_name))
        sim_info.add_child(gui.Label(f"Similarity: {similarity:.5f}"))

        row = gui.Vert()
        row.add_child(img_layout)
        row.add_child(sim_info)

        self.results_content.add_child(row)

    # Helper function <3 -------------------------------------------------------------------
    # resize an image using numpy :O
    def resize_image(self, img, size=100):
        arr = np.asarray(img)
        height, width = arr.shape[:2]
        x,y = np.linspace(0,width-1,size).astype(int), np.linspace(0,height-1,size).astype(int)

        resized = arr[y[:,None], x[None,:]]
        return o3d.geometry.Image(np.ascontiguousarray(resized))

MainApplication().run()
#ma = MainApplication()
#ma.generate_display_images()
