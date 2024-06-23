import numpy as np
from ..lib.fc_model import FCModel

def main():

    fc_path_input = '/home/artem/Projects/IFZ/LimeCore/model5_rec_fix_bc_n.fc'

    fc = FCModel()
    fc.read(fc_path_input)

    pass
    # stream = fc.stream_fragments(2,2)

    # print(stream)


if __name__ == '__main__':
    main()


