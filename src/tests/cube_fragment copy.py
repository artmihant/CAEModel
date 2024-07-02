import numpy as np
from src.cae_model.fc import FCModel

def main():

    fc_path_input = '/home/artem/Projects/CAEModel/data/model_segy_10_2.fc'
    fc_path_output = '/home/artem/Projects/CAEModel/data/model_segy_10_3.fc'


    fc = FCModel()
    fc.read(fc_path_input)


    # nodes = [
    #    [-90,0,-1],
    #    [-75,0,-1],
    #    [-60,0,-1],
    #    [-45,0,-1],
    #    [-30,0,-1],
    #    [-15,0,-1],
    #    [0,0,-1],
    #    [15,0,-1],
    #    [30,0,-1],
    #    [45,0,-1],
    #    [60,0,-1],
    #    [75,0,-1],
    #    [90,0,-1],
    # ]

    # node_index = fc.mesh['nodes']['id'].max()
    # element_index = fc.mesh['elems']['id'].max()

    # nodes_id = []
    # nodes_coord = []

    # elems_block = []
    # elems_order = []
    # elems_parent_id = []
    # elems_type = []
    # elems_id = []
    # elems_nodes = []
    
    # for node in nodes:
    #     node_index += 1
    #     element_index += 1

    #     nodes_id.append(node_index)
    #     nodes_coord.append(node)

    #     elems_block.append(2)
    #     elems_order.append(1)
    #     elems_parent_id.append(2)
    #     elems_type.append(101)
    #     elems_id.append(element_index)
    #     elems_nodes.append(np.array([node_index], dtype=np.int32))


    # fc.mesh['nodes']['id'] = np.concatenate((fc.mesh['nodes']['id'], nodes_id), dtype=np.int32) 
    # fc.mesh['nodes']['coord'] = np.concatenate((fc.mesh['nodes']['coord'], nodes_coord), dtype=np.float64) 

    # fc.mesh['elems']['block'] = np.concatenate((fc.mesh['elems']['block'], elems_block), dtype=np.int32)
    # fc.mesh['elems']['order'] = np.concatenate((fc.mesh['elems']['order'], elems_order), dtype=np.int32)
    # fc.mesh['elems']['parent_id'] = np.concatenate((fc.mesh['elems']['parent_id'], elems_parent_id), dtype=np.int32)
    # fc.mesh['elems']['type'] = np.concatenate((fc.mesh['elems']['type'], elems_type), dtype=np.int8)
    # fc.mesh['elems']['id'] = np.concatenate((fc.mesh['elems']['id'], elems_id), dtype=np.int32)
    # fc.mesh['elems']['nodes'].extend(elems_nodes)



    # # pass
    # # def selector(coord):
    # #     return abs(coord[0]) < 101 and abs(coord[1]) < 101 and -41 < coord[2] < 1e-10

    # # fc.cut(selector)

    # fc.compress()

    fc.write(fc_path_output)

    pass


if __name__ == '__main__':
    main()


