import numpy as np
from src.cae_model.fc import FCModel


def main():

    fc_path_input = '/home/artem/Projects/MSU270/SEM3D/data/src/model5_rec_fix_bc_0.fc'
    fc_path_outpath = '/home/artem/Projects/MSU270/SEM3D/data/src/model5_rec_fix_bc_cut.fc'

    fc = FCModel()
    fc.read(fc_path_input)

    fc.mesh['nodes']['coord'] = fc.mesh['nodes']['coord'] - fc.mesh['nodes']['coord'][0]

    center = [439021.25,7839164.0,20.447618]

    def selector(coord):
        return abs(coord[0] - center[0]) < 5500 and abs(coord[1] - center[1]) < 5500

    fc.cut(selector)

    fc.write(fc_path_outpath)

    pass


if __name__ == '__main__':
    main()


