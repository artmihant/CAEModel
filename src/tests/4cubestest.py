import numpy as np
import sys
from src.cae_model.fc import FCModel

fc_path_input = '/home/artem/Projects/CAEModel/data/4cubes.fc'

fc = FCModel()
fc.read(fc_path_input)

pass
