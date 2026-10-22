rd = None
ml = None
lg = None

random_mesh_default_folder = "Data\\NormalizedShapeDatabase"

def initialize(skip_renderer = False, renderer_height = 720, renderer_width = 1080):
    import sys
    import os
    sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
    from renderer import Renderer
    from Utility.meshLoader import MeshLoader
    import Utility.logger as logger
    global rd
    global ml
    global lg
    if (not skip_renderer):
        rd = Renderer(height=renderer_height, width=renderer_width)
    ml = MeshLoader()
    lg = logger.Logger()        

