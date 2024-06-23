import json
from base64 import b64decode, b64encode
from typing import Callable, Optional, TypeVar, TypedDict
import numpy as np
from element_types import ELEMENT_TYPES

from numpy import ndarray, dtype, int8, int32, float64

D = TypeVar('D', bound=dtype)


def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return b64encode(b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False

def decode(src:str, dtype: D = dtype('int32')) -> ndarray[int, D]:
    return np.frombuffer(b64decode(src), dtype).copy()


def fdecode(src:str, dtype: D = dtype('int32')) -> ndarray[int, D] | str:
    if src == '':
        return np.array([], dtype=dtype)
    if isBase64(src):
        return decode(src, dtype)
    return src

def decode_dependency(deps_types, dep_data):

    dependency: list[FCDependency] = []

    if type(deps_types) == list:
        for j, deps_type in enumerate(deps_types):
            if deps_type == 6:
                dependency.append({
                    "type": deps_type,
                    "data": dep_data[j]
                })
            else:
                dependency.append({
                    "type": deps_type,
                    "data": fdecode(dep_data[j], dtype(float64))
                })

    return dependency



def encode(data: ndarray) -> str:
    return b64encode(data.tobytes()).decode()


def fencode(data: ndarray | str) -> str:
    if type(data) == str:
        return data
    elif len(data) == 0:
        return ''
    return encode(data)


FC_ELEMENT_TYPES = {}

for ELEMENT_TYPE in ELEMENT_TYPES:
    for i in ELEMENT_TYPE['fc_id']:
        FC_ELEMENT_TYPES[i] = ELEMENT_TYPE


class FCElems(TypedDict):
    block: ndarray[int, dtype[int32]]
    order: ndarray[int, dtype[int32]]
    parent_id: ndarray[int, dtype[int32]]
    type: ndarray[int, dtype[int8]]
    id: ndarray[int, dtype[int32]]
    nodes: list[ndarray[int, dtype[int32]]]


class FCNodes(TypedDict):
    id: ndarray[int, dtype[int32]]
    coord: ndarray[int, dtype[float64]]


class FCMesh(TypedDict):
    nodes: FCNodes
    elems: FCElems


class FCBlock(TypedDict):
    cs_id : int
    id: int
    material_id: int
    property_id: int


class FCCoordinateSystem(TypedDict):
    dir1: ndarray[int, dtype[float64]]
    dir2: ndarray[int, dtype[float64]]
    id: int
    name: str
    origin: ndarray[int, dtype[float64]]
    type: str


class FCDependency(TypedDict):
    type: int
    data: ndarray[int, dtype[float64]] | str


class FCMaterialProperty(TypedDict):
    type : int
    name: int
    data : ndarray[int, dtype[float64]] | str
    dependency: list[FCDependency]


class FCMaterial(TypedDict):
    id: int
    name: str
    properties: dict[str, list[FCMaterialProperty]]


class FCLoadAxis(TypedDict):
    data: ndarray[int, dtype[float64]] | str
    dependency: list[FCDependency]


class FCLoad(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    cs: Optional[int]
    name: str
    type: int
    id: int
    axes: list[FCLoadAxis]


class FCRestrainAxis(TypedDict):
    data: ndarray[int, dtype[float64]] | str
    dependency: list[FCDependency]
    flag: bool


class FCRestraint(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    cs: Optional[int]
    name: str
    id: int
    axes: list[FCRestrainAxis]


class FCNodeset(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    id: int
    name: str

class FCSideset(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    id: int
    name: str

class FCReciver(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    # dofs



class FCModel:


    header = {
      "binary" : True,
      "description" : "Fidesys Case Format",
      "types" : { "char":1, "double":8, "int":4, "short_int":2 },
      "version" : 3
    }

    settings = {}

    blocks: list[FCBlock] = []

    coordinate_systems: list[FCCoordinateSystem]= []

    materials: list[FCMaterial] = []

    restraints: list[FCRestraint] = []
    loads: list[FCLoad] = []

    receivers: list[FCReciver] = []


    mesh: FCMesh = {
        "nodes": {
            "id": np.array([], dtype=int32),
            "coord": np.array([], dtype=float64),
        },
        "elems": {
            "block": np.array([], dtype=int32),
            "order": np.array([], dtype=int32),
            "parent_id": np.array([], dtype=int32),
            "type": np.array([], dtype=int8),
            "id": np.array([], dtype=int32),
            "nodes": [],
        }
    }


    def read(self, filepath):

        with open(filepath, "r") as f:
            src_data = json.load(f)

        self.src_data = src_data

        self._decode_header(src_data)
        self._decode_blocks(src_data)
        self._decode_contact_constrains(src_data)
        self._decode_coordinate_systems(src_data)
        self._decode_mesh(src_data)
        self._decode_settings(src_data)
        self._decode_materials(src_data)
        self._decode_restraints(src_data)
        self._decode_loads(src_data)
        # self._decode_nodesets(src_data)
        # self._decode_sidesets(src_data)
        self._decode_receivers(src_data)

    def write(self, filepath):

        src_data = {}

        self._encode_header(src_data)
        self._encode_blocks(src_data)
        self._encode_coordinate_systems(src_data)
        self._encode_contact_constrains(src_data)
        self._encode_mesh(src_data)
        self._encode_settings(src_data)
        self._encode_materials(src_data)
        self._encode_restraints(src_data)
        self._encode_loads(src_data)
        # self._encode_nodesets(src_data)
        # self._encode_sidesets(src_data)
        self._encode_receivers(src_data)

        with open(filepath, "w") as f:
            json.dump(src_data, f, indent=4)


    def _decode_header(self, data):
        self.header = data.get('header')
        assert self.header

    def _encode_header(self, data):
        data['header'] = self.header


    def _decode_blocks(self, data):
        blocks_src = data.get('blocks', [])
        for block_src in blocks_src:
            block: FCBlock = {
                'cs_id': block_src['cs_id'],
                'id': block_src['id'],
                'material_id': block_src['material_id'],
                'property_id': block_src['property_id'],
            }
            self.blocks.append(block)

    def _encode_blocks(self, data):
        data['blocks'] = self.blocks


    def _decode_contact_constrains(self, data):
        pass

    def _encode_contact_constrains(self, data):
        pass


    def _decode_coordinate_systems(self, data):

        self.coordinate_systems = [{
            'dir1': decode(cs['dir1'],   dtype(float64)),
            'dir2': decode(cs['dir2'],   dtype(float64)),
            'origin': decode(cs['origin'],   dtype(float64)),
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in data.get('coordinate_systems') ]


    def _encode_coordinate_systems(self, data):

        data['coordinate_systems'] = [{
            'dir1': encode(cs['dir1']),
            'dir2': encode(cs['dir2']),
            'origin': encode(cs['origin']),
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in self.coordinate_systems ]


    def _decode_mesh(self, data):

        mesh_src = data.get('mesh', {})

        self.mesh = {
            'elems': {
                'block': decode(mesh_src['elem_blocks']),
                'order': decode(mesh_src['elem_orders']),
                'parent_id': decode(mesh_src['elem_parent_ids']),
                'type': decode(mesh_src['elem_types'], dtype(int8)),
                'id': decode(mesh_src['elemids']),
                'nodes': [],
            },
            'nodes': {
                'id': decode(mesh_src['nids']),
                'coord': decode(mesh_src['nodes'], dtype(float64)).reshape(-1,3),
            }
        }

        counter = 0
        nodes_list = decode(mesh_src['elems'])

        elem_types = self.mesh['elems']['type']

        for elem_type in elem_types:
            count = FC_ELEMENT_TYPES[elem_type]['nodes']
            element_raw = nodes_list[counter:(counter+count)]
            self.mesh['elems']['nodes'].append(element_raw)
            counter += count


    def _encode_mesh(self, data):
        mesh = self.mesh

        data['mesh'] = {
            "elem_blocks": encode(mesh['elems']['block']),
            "elem_orders": encode(mesh['elems']['order']),
            "elem_parent_ids": encode(mesh['elems']['parent_id']),
            "elem_types": encode(mesh['elems']['type']),
            "elemids": encode(mesh['elems']['id']),
            "elems": encode(np.concatenate(mesh['elems']['nodes'])),
            "elems_count": len(mesh['elems']['id']),
            "nids": encode(mesh['nodes']['id']),
            "nodes": encode(mesh['nodes']['coord']),
            "nodes_count": len(mesh['nodes']['id']),
        }

    def _decode_settings(self, data):
        self.settings = data.get('settings')
        assert self.settings


    def _encode_settings(self, data):
        settings = self.settings
        data['settings'] = settings


    def _decode_materials(self, data):

        self.materials = []

        for material_src in data.get('materials', []):

            properties: dict[str, list[FCMaterialProperty]] = {}

            for property_name in material_src:
                properties_src = material_src[property_name]

                if type(properties_src) != list:
                    continue

                properties[property_name] = [{
                        "name": property_src["const_names"][i],
                        "data": fdecode(constants, dtype(float64)),
                        "type": property_src["type"],
                        "dependency": decode_dependency(property_src["const_types"][i],property_src["const_dep"][i])
                    }
                    for property_src in properties_src
                    for i, constants in enumerate(property_src["constants"])
                ]


            self.materials.append({
                "id": material_src['id'],
                "name": material_src['name'],
                "properties": properties
            })


    def _encode_materials(self, data):

        data['materials'] = []

        for material in self.materials:

            material_src = {
                "id": material['id'],
                "name": material['name'],
            }

            data['materials'].append(material_src)

            for property_name in material["properties"]:

                material_src[property_name] = []

                for material_property in material["properties"][property_name]:

                    if material_property['const_types']:
                        const_dep = [encode(material_property["const_dep"])]
                        const_types = [material_property['const_types']]
                    else:
                        const_dep = ""
                        const_types = 0

                    material_src[property_name].append({
                        "const_dep": [const_dep],
                        "const_dep_size": [material_property["const_dep_size"]],
                        "const_names": [material_property["const_names"]],
                        "const_types": [const_types],
                        "constants": [encode(material_property["constants"])],
                        "type": material_property["type"]
                    })


    def _decode_restraints(self, data):

        self.restraints = []

        for restraint_src in data.get('restraints', []):

            axes: list[FCRestrainAxis] = []

            for i, dep_var_num in enumerate(restraint_src['dep_var_num']):

                axis_data = restraint_src['data'][i] \
                    if restraint_src["dependency_type"][i] == 6 \
                    else fdecode(restraint_src['data'][i], dtype('float64'))

                axes.append({
                    "data": axis_data,
                    "dependency": decode_dependency(restraint_src["dependency_type"][i], dep_var_num),
                    "flag": restraint_src['flag'][i],
                })

            self.restraints.append({
                "id": restraint_src['id'],
                "name": restraint_src['name'],
                "cs": restraint_src['cs'] if 'cs' in restraint_src else 0,
                "apply_to": fdecode(restraint_src['apply_to']),
                "axes": axes
            })


    def _encode_restraints(self, data):

        data['restraints'] = [{
            'dir1': encode(cs['dir1']),
            'dir2': encode(cs['dir2']),
            'origin': encode(cs['origin']),
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in self.restraints ]


    def _decode_loads(self, data):

        self.loads = []


        for load_src in data.get('loads', []):

            axes: list[FCLoadAxis] = []

            for i, dep_var_num in enumerate(load_src['dep_var_num']):

                axes.append({
                    "data": fdecode(load_src['data'][i], dtype('float64')),
                    "dependency": decode_dependency(load_src["dependency_type"][i], dep_var_num),
                })

            self.loads.append({
                "id": load_src['id'],
                "name": load_src['name'],
                "cs": load_src['cs'] if 'cs' in load_src else 0,
                "apply_to": fdecode(load_src['apply_to']),
                "axes": axes,
                "type": load_src['type'],
            })


    def _encode_loads(self, data):

        data['restraints'] = [{
            'dir1': encode(cs['dir1']),
            'dir2': encode(cs['dir2']),
            'origin': encode(cs['origin']),
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in self.restraints ]


    # def _decode_nodesets(self, data):
    #     pass


    # def _encode_nodesets(self, data):
    #     pass


    # def _decode_sidesets(self, data):
    #     self.receivers = [{
    #         'apply_to': fdecode(cs['apply_to']),
    #         'dofs': cs['dofs'],
    #         "id" : cs['id'],
    #         "name": cs['name'],
    #         "type": cs['type']
    #     } for cs in data.get('receivers',[]) ]


    # def _encode_sidesets(self, data):
    #     pass


    def _decode_receivers(self, data):

        self.receivers = [{
            'apply_to': fdecode(cs['apply_to']),
            'dofs': cs['dofs'],
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in data.get('receivers',[]) ]


    def _encode_receivers(self, data):

        data['receivers'] = [{
            'apply_to': fencode(cs['apply_to']),
            'apply_to_size': cs['apply_to_size'],
            'dofs': cs['dofs'],
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in self.receivers ]



    def cut(self, cut_function: Callable):

        nodes_mask = [cut_function(el) for el in self.mesh['nodes']['coord']]

        self.mesh['nodes']['coord'] = self.mesh['nodes']['coord'][nodes_mask]
        self.mesh['nodes']['id'] = self.mesh['nodes']['id'][nodes_mask]
        self.mesh['nodes']['count'] = len(self.mesh['nodes']['id'])

        elems_mask = []

        node_set = set(self.mesh['nodes']['id'])

        for i in range(self.mesh['elems']['count']):

            mask_append = True

            for node in self.mesh['elems']['nodes'][i]:
                if node not in node_set:
                    mask_append = False
                    break

            if mask_append:
                elems_mask.append(i)


        self.mesh['elems']['block'] = self.mesh['elems']['block'][elems_mask]
        self.mesh['elems']['order'] = self.mesh['elems']['order'][elems_mask]
        self.mesh['elems']['parent_id'] = self.mesh['elems']['parent_id'][elems_mask]
        self.mesh['elems']['type'] = self.mesh['elems']['type'][elems_mask]
        self.mesh['elems']['id'] = self.mesh['elems']['id'][elems_mask]
        self.mesh['elems']['nodes'] = [self.mesh['elems']['nodes'][i] for i in elems_mask]
        self.mesh['elems']['count'] = len(self.mesh['elems']['id'])

        for material in self.materials:
            for key in material['properties']:
                for property in material['properties'][key]:
                    if property['const_types'] == 10:

                        mat_mask = np.in1d(property['const_dep'], self.mesh['elems']['id'], assume_unique=True)

                        property['const_dep'] = property['const_dep'][mat_mask]
                        property['constants'] = property['constants'][mat_mask]
                        property['const_dep_size'] = len(property['const_dep'])

                    if property['const_types'] == 11:

                        mat_mask = np.in1d(property['const_dep'], self.mesh['nodes']['id'], assume_unique=True)

                        property['const_dep'] = property['const_dep'][mat_mask]
                        property['constants'] = property['constants'][mat_mask]
                        property['const_dep_size'] = len(property['const_dep'])



    def stream_fragments(self, dim, rank, offset=0):

        fragments = []

        title = None

        for i in range(self.mesh['elems']['count']):

            element_type_id = self.mesh['elems']['type'][i]
            element_nodes = self.mesh['elems']['nodes'][i]

            element_type = FC_ELEMENT_TYPES[element_type_id]

            if dim < element_type['site'] or element_type['site'] < rank:
                continue;

            element_structure = element_type['structure'][rank]

            element_nodes[element_structure]

            element_parts = element_nodes[element_structure].reshape((-1,rank+1))

            if title and title[1] == self.mesh['elems']['block'][i] and title[2] == element_type['site']:
                title[4] += len(element_parts)
            else:
                title = [dim, self.mesh['elems']['block'][i]+offset, element_type['site'], rank, len(element_parts)]

                fragments.append(title)

            fragments.extend(element_parts)
            pass

        stream = []
        for a in fragments:
            stream.extend(a)

        return stream
