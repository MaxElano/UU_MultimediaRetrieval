import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from renderer import RenderMode
import Utility.config as config
import open3d as o3d
from application import MainApplication

config.initialize(skip_renderer=True)
# note: first time you run it will create ALL display icons so it will take a while
MainApplication().run()

