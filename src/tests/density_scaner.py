
import json

import numpy as np
from lib.fc_model import FCModel
from lib.fc_reader import FCReader


def main():

    # fc_path_input = '/home/artem/ProveDesign/soil/test.fc'
    fc_path_input = '/home/artem/ProveDesign/soil/data/model19_mini_material.fc'
    fc = FCModel()
    fc.read(fc_path_input)

    # Для каждого элемента вычисляем его глубину. 

    nodes_coord = fc.mesh['nodes']['coord']
    nodes_ids = fc.mesh['nodes']['id']

    nodes_column_lexsort = np.lexsort((nodes_coord[:,2],nodes_coord[:,1],nodes_coord[:,0]))

    nodes_coord_sorted = nodes_coord[nodes_column_lexsort]

    nodes_ids_sorted = nodes_ids[nodes_column_lexsort]

    index_map = {el: i
        for i, el in enumerate(nodes_ids_sorted)
    }

    Ro = fc.materials[0]["properties"]["common"][0]["constants"]

    l = int((Ro.shape[0]/149)**0.5)

    Ro = Ro.reshape(149,l,l)
    print(Ro.shape)

    import matplotlib.pyplot as plt
    
    for i in range(len(Ro)):
        print('z',i)
        plt.imshow(Ro[i], cmap="plasma", vmin=1500, vmax=2200)
        plt.savefig(f'./RoZ/{i}.png', pad_inches=0, dpi=120)
        plt.close()

    Ro = Ro.transpose([1,0,2]) 

    for i in range(len(Ro)):
        print('y',i)
        plt.imshow(Ro[i], cmap="plasma", vmin=1500, vmax=2200)
        plt.savefig(f'./RoY/{i}.png', pad_inches=0)
        plt.close()


    Ro = Ro.transpose([2,1,0]) 

    for i in range(len(Ro)):
        print('x',i)
        plt.imshow(Ro[i], cmap="plasma", vmin=1500, vmax=2200)
        plt.savefig(f'./RoX/{i}.png', pad_inches=0)



    return

    for i in range(fc.mesh['elems']['count']):

        # elem_id = fc.mesh['elems']['id'][i]

        node_id = fc.mesh['elems']['nodes'][i][0]

        # coord = nodes_coord_sorted[index_map[node_id]]

        order = index_map[node_id]%150+1

        print(order)

        # fc.mesh['elems']["parent_id"][i] = layer['id']
        # fc.mesh['elems']["block"][i]     = layer['id']


    # print(positive_counter, negative_counter)

    # print(E_min_max_new)
    # print(E_min_max_old)



    # pass

    # fc.write(fc_path_output)







if __name__ == '__main__':
    main()


