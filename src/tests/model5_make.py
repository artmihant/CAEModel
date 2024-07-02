import numpy as np
from src.cae_model.fc import FCModel


def local_coords_2D(ax,ay, bx,by, cx,cy, px,py):
    p = np.linalg.det([
        [ax,ay,1],
        [bx,by,1],
        [cx,cy,1],
    ])
    if abs(p) > 1000:

        a = np.linalg.det([
            [px,py,1],
            [bx,by,1],
            [cx,cy,1],
        ])

        b = np.linalg.det([
            [ax,ay,1],
            [px,py,1],
            [cx,cy,1],
        ])

        c = np.linalg.det([
            [ax,ay,1],
            [bx,by,1],
            [px,py,1],
        ])

        return [
            a/p, b/p, c/p
        ]
    else:
        print(p)
        p = np.linalg.det([
            [ax,1],
            [bx,1],
        ])
        print(p)
        if abs(p) > 0:

            a = np.linalg.det([
                [px,1],
                [bx,1],
            ])

            b = np.linalg.det([
                [ax,1],
                [px,1],
            ])

            return [
                a/p, b/p, 0
            ]
        else:
            return [1,0,0]


def main():

    fc_path_input = '/home/artem/Projects/MSU270/SEM3D/data/src/model5_rec_fix_bc.fc'
    fc_path_output = '/home/artem/Projects/MSU270/SEM3D/data/src/model5_rec_fix_bc_2.fc'
    fc_path_top = '/home/artem/Projects/MSU270/SEM3D/data/src/model5_top.fc'

    fc_top = FCModel()
    fc_top.read(fc_path_top)


    fc = FCModel()
    fc.read(fc_path_input)

    coord = fc_top.mesh['nodes']['coord']

    coord_z = coord[:,2]

    center = [
        439021.250000,
        7839164.000000, 
        0
    ]

    nodes = []

    for i in range(0,50):
        for j in range(0,200):

            

            x = center[0]+(j-99.5)*50
            y = center[1]+(i-24.5)*300

            point0 = np.zeros(3)
            point1 = np.zeros(3)
            point2 = np.zeros(3)

            d_point0 = 10000
            d_point1 = 10000
            d_point2 = 10000

            k_point0 = 0
            k_point1 = 0
            k_point2 = 0

            for k, point in enumerate(coord):

                delta = (point[0] - x)**2 + (point[1] - y)**2

                if delta < d_point0:

                    d_point2, d_point1, d_point0 = d_point1, d_point0, delta

                    point2, point1, point0 = point1, point0, point

                    k_point2, k_point1, k_point0 = k_point1, k_point0,  fc_top.mesh['nodes']['id'][k]

                elif delta < d_point1:

                    d_point2, d_point1  = d_point1, delta

                    point2, point1 = point1, point

                    k_point2, k_point1 = k_point1, fc_top.mesh['nodes']['id'][k]

                elif delta < d_point2:

                    d_point2 = delta

                    point2 = point

                    k_point2 = fc_top.mesh['nodes']['id'][k]

            l = local_coords_2D(
                point0[0],point0[1],
                point1[0],point1[1], 
                point2[0],point2[1], 
                x, y
            )
            if(l[2]==0):
                print(i,j)

            z = l[0]*point0[2] + l[1]*point1[2] + l[2]*point2[2] + center[2]

            if l[0] < -0.1 or l[1] < -0.1 or l[2] < -0.1:
                print('!', l)
                pass


            # print(z, k_point0, k_point1, k_point2)

            nodes.append([
                x,y,z
            ])


    node_index = fc.mesh['nodes']['id'].max()
    element_index = fc.mesh['elems']['id'].max()

    nodes_id = []
    nodes_coord = []

    elems_block = []
    elems_order = []
    elems_parent_id = []
    elems_type = []
    elems_id = []
    elems_nodes = []
    
    for node in nodes:
        node_index += 1
        element_index += 1

        nodes_id.append(node_index)
        nodes_coord.append(node)

        elems_block.append(2)
        elems_order.append(1)
        elems_parent_id.append(2)
        elems_type.append(101)
        elems_id.append(element_index)
        elems_nodes.append(np.array([node_index], dtype=np.int32))


    fc.mesh['nodes']['id'] = np.concatenate((fc.mesh['nodes']['id'], nodes_id), dtype=np.int32) 
    fc.mesh['nodes']['coord'] = np.concatenate((fc.mesh['nodes']['coord'], nodes_coord), dtype=np.float64) 

    fc.mesh['elems']['block'] = np.concatenate((fc.mesh['elems']['block'], elems_block), dtype=np.int32)
    fc.mesh['elems']['order'] = np.concatenate((fc.mesh['elems']['order'], elems_order), dtype=np.int32)
    fc.mesh['elems']['parent_id'] = np.concatenate((fc.mesh['elems']['parent_id'], elems_parent_id), dtype=np.int32)
    fc.mesh['elems']['type'] = np.concatenate((fc.mesh['elems']['type'], elems_type), dtype=np.int8)
    fc.mesh['elems']['id'] = np.concatenate((fc.mesh['elems']['id'], elems_id), dtype=np.int32)
    fc.mesh['elems']['nodes'].extend(elems_nodes)



    # # pass
    # # def selector(coord):
    # #     return abs(coord[0]) < 101 and abs(coord[1]) < 101 and -41 < coord[2] < 1e-10

    # # fc.cut(selector)

    # fc.compress()

    fc.write(fc_path_output)

    pass


if __name__ == '__main__':
    main()


