
import json

import numpy as np
from lib.fc_model import FCModel
from lib.vtu_reader import VTUReader


def main():

    vtu_path_input = '/home/artem/ProveDesign/soil/data/part22_st_pr.vtu'
    fc_path_input = '/home/artem/ProveDesign/soil/data/model22_part.fc'
    fc_path_output = '/home/artem/ProveDesign/soil/data/model22_part_material2.fc'


    vtu = VTUReader(vtu_path_input)

    fc = FCModel()
    fc.read(fc_path_input)
    
    """
    Вычислить значение следа в каждой ячейке
    Для каждого узла определить индекс ячейки, в которой тот расположен

    fc.mesh['elems']

    """

    tr_strains = np.zeros(fc.mesh['elems']['count'], dtype=np.float64)

    for i, cell in enumerate(vtu.cells['nodes']):
        strain = vtu.point_data['Strain']['data'][cell]

        tr_strain = 0

        for el in strain:
            tr_strain += el[0]+el[1]+el[2]

        tr_strain /= 8

        tr_strains[i] = tr_strain

    print(tr_strains.min(), tr_strains.max())

    tr_strains_min = tr_strains.min()
    tr_strains_max = tr_strains.max()

    fc.blocks = []

    for i in range(6):
        fc.blocks.append({'id': i+1, 'cs_id': 1, 'material_id': 1, 'property_id': -1})

    # Для каждого элемента вычисляем его глубину. 

    d = 90.49121856689453

    depth_layers = [
        {
            "id": 1,
            "min_value": 0+d,
            "max_value": 1.7+d,
            "max_order": 149,
            "min_order": 145,
            "a":  0.0128070,
            "b": -170190,
            "FANG": 9
        },
        {
            "id": 2,
            "min_value": 1.7+d,
            "max_value": 5.5+d,
            "max_order": 144,
            "min_order": 133,
            "a":  0.0072222,
            "b": 1272200,
            "FANG": 7
        },
        {
            "id": 3,
            "min_value": 5.5+d,
            "max_value": 15.4+d,
            "max_order": 132,
            "min_order": 103,
            "a": 0.0493910,
            "b": 1512600,
            "FANG": 8
        },
        {
            "id": 4,
            "min_value": 15.4+d,
            "max_value": 24.9+d,
            "max_order": 102,
            "min_order": 75,
            "a": 0.0493910,
            "b": 1512600,
            "FANG": 15
        },
        {
            "id": 5,
            "min_value": 24.9+d,
            "max_value": 41.25+d,
            "max_order": 74,
            "min_order": 25,
            "a": 0.2031231,
            "b": -26459670,
            "FANG": 17
        },
        {
            "id": 6,
            "min_value": 41.25+d,
            "max_value": 1000+d,
            "max_order": 24,
            "min_order": 1,
            "a":  0.2031231,
            "b": -26459670,
            "FANG": 22
        },
    ]

    nodes_coord = fc.mesh['nodes']['coord']
    nodes_ids = fc.mesh['nodes']['id']

    nodes_column_lexsort = np.lexsort((nodes_coord[:,2],nodes_coord[:,1],nodes_coord[:,0]))

    nodes_coord_sorted = nodes_coord[nodes_column_lexsort]

    nodes_ids_sorted = nodes_ids[nodes_column_lexsort]

    index_map = {el: i
        for i, el in enumerate(nodes_ids_sorted)
    }

    assert (fc.materials[0]["properties"]["elasticity"][0]["const_dep"] == fc.mesh["elems"]["id"]).all()
    assert (fc.materials[0]["properties"]["elasticity"][1]["const_dep"] == fc.mesh["elems"]["id"]).all()
    assert (fc.materials[0]["properties"]["common"][0]["const_dep"] == fc.mesh["elems"]["id"]).all()

    E = fc.materials[0]["properties"]["elasticity"][0]["constants"]
    Ro = fc.materials[0]["properties"]["common"][0]["constants"]


    fc.materials[0]["properties"]["plasticity"] = [
       { #когезия
        'const_dep': fc.materials[0]["properties"]["elasticity"][0]["const_dep"], 
        'const_dep_size': fc.mesh['elems']['count'], 
        'const_names': 7, 
        'const_types': 10, 
        'constants': np.zeros(fc.mesh['elems']['count'], dtype=np.float64), 
        'type': 1
    }, { #угол внутреннего трения
        'const_dep': fc.materials[0]["properties"]["elasticity"][0]["const_dep"], 
        'const_dep_size': fc.mesh['elems']['count'], 
        'const_names': 8, 
        'const_types': 10, 
        'constants': np.zeros(fc.mesh['elems']['count'], dtype=np.float64), 
        'type': 1
    }, { #угол дилатансии
        'const_dep': fc.materials[0]["properties"]["elasticity"][0]["const_dep"],
        'const_dep_size': fc.mesh['elems']['count'], 
        'const_names': 9, 
        'const_types': 10, 
        'constants': np.zeros(fc.mesh['elems']['count'], dtype=np.float64),  
        'type': 1
    }]

    fc.materials[0]["properties"]["geomechanic"] = [
       { # пористость
        'const_dep': fc.materials[0]["properties"]["elasticity"][0]["const_dep"], 
        'const_dep_size': fc.mesh['elems']['count'], 
        'const_names': 2, 
        'const_types': 10, 
        'constants': np.zeros(fc.mesh['elems']['count'], dtype=np.float64), 
        'type': 0
    }, { # проницаемость
        'const_dep': fc.materials[0]["properties"]["elasticity"][0]["const_dep"], 
        'const_dep_size': fc.mesh['elems']['count'], 
        'const_names': 0, 
        'const_types': 10, 
        'constants': np.zeros(fc.mesh['elems']['count'], dtype=np.float64), 
        'type': 0
    }, { # вязкость
        'const_dep': np.array([], dtype=np.float64),
        'const_dep_size': 0, 
        'const_names': 1, 
        'const_types': 0, 
        'constants': np.array([0.001], dtype=np.float64),  
        'type': 0
    }, { # число био
        'const_dep': np.array([], dtype=np.float64),
        'const_dep_size': 0, 
        'const_names': 5, 
        'const_types': 0, 
        'constants': np.array([0.6], dtype=np.float64),  
        'type': 0
    }, { # модуль упругости жидкости
        'const_dep': np.array([], dtype=np.float64),
        'const_dep_size': 0, 
        'const_names': 3, 
        'const_types': 0, 
        'constants': np.array([2e9], dtype=np.float64),  
        'type': 0
    }, { # плотность жидкости
        'const_dep': np.array([], dtype=np.float64),
        'const_dep_size': 0, 
        'const_names': 19, 
        'const_types': 0, 
        'constants': np.array([1000], dtype=np.float64),  
        'type': 0
    }]



    negative_counter = {}
    positive_counter = {}

    E_min_max_new = {
        1: {
            "min": 1e20,
            "max": 0
        },
        2: {
            "min": 1e20,
            "max": 0
        },
        3: {
            "min": 1e20,
            "max": 0
        },
        4: {
            "min": 1e20,
            "max": 0
        },
        5: {
            "min": 1e20,
            "max": 0
        },
        6: {
            "min": 1e20,
            "max": 0
        },
    }


    E_min_max_old = {
        1: {
            "min": 1e20,
            "max": 0
        },
        2: {
            "min": 1e20,
            "max": 0
        },
        3: {
            "min": 1e20,
            "max": 0
        },
        4: {
            "min": 1e20,
            "max": 0
        },
        5: {
            "min": 1e20,
            "max": 0
        },
        6: {
            "min": 1e20,
            "max": 0
        },
    }


    for i in range(fc.mesh['elems']['count']):

        elem_id = fc.mesh['elems']['id'][i]

        node_id = fc.mesh['elems']['nodes'][i][0]

        coord = nodes_coord_sorted[index_map[node_id]]

        order = index_map[node_id]%150+1

        layer_id = 0

        for layer in depth_layers:
            if layer['min_order'] <= order <= layer['max_order']:
                layer_id = layer['id']
                break
            
        layer = depth_layers[layer_id-1]

        e = layer['a']*E[i] + layer['b']
        
        if layer_id not in positive_counter:
            positive_counter[layer_id] = 0
        if layer_id not in negative_counter:
            negative_counter[layer_id] = 0

        assert e > 0

        positive_counter[layer_id] += 1

        if E_min_max_old[layer_id]['min'] > E[i]:
            E_min_max_old[layer_id]['min'] = E[i]

        if E_min_max_old[layer_id]['max'] < E[i]:
            E_min_max_old[layer_id]['max'] = E[i]

        E[i] = e

        if E_min_max_new[layer_id]['min'] > e:
            E_min_max_new[layer_id]['min'] = e

        if E_min_max_new[layer_id]['max'] < e:
            E_min_max_new[layer_id]['max'] = e


        fc.mesh['elems']["parent_id"][i] = 1
        fc.mesh['elems']["block"][i]     = 1

        # fc.mesh['elems']["parent_id"][i] = layer['id']
        # fc.mesh['elems']["block"][i]     = layer['id']

        fang = layer["FANG"]

        if layer['id'] == 1 or layer['id'] == 2:
            fc.materials[0]["properties"]["plasticity"][0]["constants"][i] = 0.1*(0.01*E[i]+0.0488)*(1-np.sin(np.pi*fang/180))/(2*np.cos(np.pi*fang/180))
        else:
            fc.materials[0]["properties"]["plasticity"][0]["constants"][i] = (0.01*E[i]+0.0488)*(1-np.sin(np.pi*fang/180))/(2*np.cos(np.pi*fang/180))
            
        fc.materials[0]["properties"]["plasticity"][1]["constants"][i] = fang
        fc.materials[0]["properties"]["plasticity"][2]["constants"][i] = fang/2


        Fi_min = 0.315
        Fi_max = 0.658

        tr_strain = tr_strains[i]
        # Fi = -0.000585*Ro[i] + 1.584795

        Fi = (Fi_max*(tr_strain - tr_strains_min) - Fi_min*(tr_strain - tr_strains_max))/(tr_strains_max-tr_strains_min)

        fc.materials[0]["properties"]["geomechanic"][0]["constants"][i] = Fi
        fc.materials[0]["properties"]["geomechanic"][1]["constants"][i] = 10**(-19.8+5.2*Fi)

    print(fc.materials[0]["properties"]["geomechanic"][1]["constants"].min(), fc.materials[0]["properties"]["geomechanic"][1]["constants"].max())
    print(fc.materials[0]["properties"]["geomechanic"][0]["constants"].min(), fc.materials[0]["properties"]["geomechanic"][0]["constants"].max())

    # print(fc.materials[0]["properties"]["plasticity"][0]["constants"].min())

    # print(positive_counter, negative_counter)

    # print(E_min_max_new)
    # print(E_min_max_old)





    # pass

    fc.write(fc_path_output)







if __name__ == '__main__':
    main()


