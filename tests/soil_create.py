
import json

import numpy as np
from lib.fc_model import FCModel
from lib.fc_reader import FCReader


def main():

    fc_path_input = '/home/artem/ProveDesign/soil/data/model19_part.fc'

    fc = FCModel()
    fc.read(fc_path_input)
    
    fc.blocks.append({'cs_id': 1, 'id': 2, 'material_id': 1, 'property_id': -1})
    fc.blocks.append({'cs_id': 1, 'id': 3, 'material_id': 1, 'property_id': -1})
    fc.blocks.append({'cs_id': 1, 'id': 4, 'material_id': 1, 'property_id': -1})
    fc.blocks.append({'cs_id': 1, 'id': 5, 'material_id': 1, 'property_id': -1})
    fc.blocks.append({'cs_id': 1, 'id': 6, 'material_id': 1, 'property_id': -1})
    fc.blocks.append({'cs_id': 1, 'id': 7, 'material_id': 1, 'property_id': -1})

    

    # Для каждого элемента вычисляем его глубину. В соответствии с неё модифицируем блок элемента. 

    depth = np.zeros(len(fc.mesh))



    pass

    # fc.write(fc_path_output)




    # with open(fc_path, "r") as f:
    #     fc_data = json.load(f)


    # print_long_json(fc_data)



    # user = User.get(email="test@test.com")
    # if not user:
    #     return

    # project = user.add_project()

    # task = project.add_task()

    # body = task.add_body()





if __name__ == '__main__':
    main()


