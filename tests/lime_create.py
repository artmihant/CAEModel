
import json
import pandas as pd

import numpy as np
from ..build.lib.fc import FCModel


def main():

    fc_path_input = '/home/artem/Projects/IFZ/LimeCore/model0.fc'

    fc = FCModel()
    fc.read(fc_path_input)

    df = pd.read_csv('/home/artem/Projects/IFZ/LimeCore/map.csv')

    fc.materials[0]['properties']['elasticity'][0]['const_dep'] = np.array()
    fc.materials[0]['properties']['elasticity'][0]['constants'] = np.array()

    # Для каждого элемента по индексу
    # - определить, какому месту (блоку) он принадлежит
    # - 

    pass

    # Для каждого элемента вычисляем его глубину и координаты. В соответствии с неё модифицируем блок элемента. 


if __name__ == '__main__':
    main()


