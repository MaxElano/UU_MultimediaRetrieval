rd = None
ml = None
lg = None

random_mesh_default_folder = "Data\\OriginalShapeDatabase"

def initialize(skip_renderer = False):
    import renderer
    import meshLoader
    import logger
    global rd
    global ml
    global lg
    if (not skip_renderer):
        rd = renderer.renderer()
    ml = meshLoader.meshLoader()
    lg = logger.logger()        

