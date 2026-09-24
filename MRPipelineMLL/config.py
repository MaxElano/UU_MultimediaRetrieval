rd = None
ml = None
lg = None

random_mesh_default_folder = "Data\\OriginalShapeDatabase"

def initialize():
    import renderer
    import meshLoader
    import logger
    global rd
    global ml
    global lg
    rd = renderer.renderer()
    ml = meshLoader.meshLoader()
    lg = logger.logger()        


