rd = None
ml = None
lg = None

random_mesh_default_folder = "Data\\NormalizedShapeDatabase"

def initialize(skip_renderer = False, renderer_height = 720, renderer_width = 1080):
    import renderer
    import meshLoader
    import logger
    global rd
    global ml
    global lg
    if (not skip_renderer):
        rd = renderer.renderer(height=renderer_height, width=renderer_width)
    ml = meshLoader.meshLoader()
    lg = logger.logger()        

