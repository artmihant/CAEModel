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

    fc = FCModel()
    fc.read(fc_path_input)

    E = fc.materials[0]['properties']['elasticity'][0]['data']
    Nu = fc.materials[0]['properties']['elasticity'][1]['data']
    Ro = fc.materials[0]['properties']['common'][0]['data']

    print(len(E), len(Nu), len(Ro), len(np.unique(E)), len(np.unique(Nu)), len(np.unique(Ro)))

    Mat = np.array([E, Nu, Ro]).transpose()
    # Mat_u = np.unique(Mat)
    # print(Mat.shape)
    print(len(np.unique(Mat, axis=0)), np.unique(Mat, axis=0))
    # fc.write(fc_path_output)

    import matplotlib.pyplot as plt

    # plt.title("Plotting 1-D array")
    # plt.xlabel("X axis")
    # plt.ylabel("Y axis")
    # plt.plot(np.arange(len(Nu)), np.sort(Nu), color="green", ls='-', label= "Array elements")
    # plt.legend()
    # plt.show()

    pass


if __name__ == '__main__':
    main()


