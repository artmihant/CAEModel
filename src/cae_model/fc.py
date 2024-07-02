import json
from base64 import b64decode, b64encode
from typing import Callable, Optional, TypeVar, TypedDict
import numpy as np
from .element_types import ELEMENT_TYPES

from numpy import ndarray, dtype, int8, int32, int64, float64

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
    if src == '':
        return np.array([], dtype=dtype)
    return np.frombuffer(b64decode(src), dtype).copy()


def fdecode(src:str, dtype: D = dtype('int32')) -> ndarray[int, D] | str:
    if src == '':
        return np.array([], dtype=dtype)
    if isBase64(src):
        return decode(src, dtype)
    return src



def encode(data: ndarray) -> str:
    return b64encode(data.tobytes()).decode()


def fencode(data: ndarray | str) -> str:
    if isinstance(data, str):
        return data
    elif isinstance(data, ndarray):
        if len(data) == 0:
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
    dependency: list[FCDependency] | int


class FCMaterial(TypedDict):
    id: int
    name: str
    properties: dict[str, list[FCMaterialProperty]]


class FCLoadAxis(TypedDict):
    data: ndarray[int, dtype[float64]] | str
    dependency: list[FCDependency] | int


class FCLoad(TypedDict):
    apply_to: ndarray[int, dtype[int64]] | str
    cs: Optional[int]
    name: str
    type: int
    id: int
    axes: list[FCLoadAxis]


class FCRestrainAxis(TypedDict):
    data: ndarray[int, dtype[float64]] | str
    dependency: list[FCDependency] | int
    flag: bool


class FCRestraint(TypedDict):
    apply_to: ndarray[int, dtype[int64]] | str
    cs: Optional[int]
    name: str
    id: int
    axes: list[FCRestrainAxis]


class FCNodeset(TypedDict):
    apply_to: ndarray[int, dtype[int64]] | str
    id: int
    name: str

class FCSideset(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    id: int
    name: str

class FCReciver(TypedDict):
    apply_to: ndarray[int, dtype[int32]] | str
    dofs: list
    id: int
    name: str
    type: str


def decode_dependency(deps_types: list | int, dep_data) -> list[FCDependency] | int :

    if isinstance(deps_types, list):

        return [{
            "type": deps_type,
            "data": fdecode(dep_data[j], dtype(float64))
        } for j, deps_type in enumerate(deps_types)]

    elif isinstance(deps_types, int):
        return deps_types


def encode_dependency(dependency: list[FCDependency] | int):

    if isinstance(dependency, int):
        return dependency, ''
    elif isinstance(dependency, list):
        return [deps['type'] for deps in dependency], [fencode(deps['data']) for deps in dependency]


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
        self._decode_coordinate_systems(src_data)
        self._decode_mesh(src_data)
        self._decode_settings(src_data)
        self._decode_materials(src_data)
        self._decode_restraints(src_data)
        self._decode_loads(src_data)
        self._decode_receivers(src_data)

    def write(self, filepath):

        src_data = {}

        self._encode_header(src_data)
        self._encode_blocks(src_data)
        self._encode_coordinate_systems(src_data)
        self._encode_mesh(src_data)
        self._encode_settings(src_data)
        self._encode_materials(src_data)
        self._encode_restraints(src_data)
        self._encode_loads(src_data)
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
        
        pass


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
                        "data": decode(constants, dtype(float64)),
                        "type": property_src["type"],
                        "dependency": decode_dependency(
                            property_src["const_types"][i], 
                            property_src["const_dep"][i]
                        )
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

            for property_name in material["properties"]:

                material_src[property_name] = []

                for material_property in material["properties"][property_name]:

                    const_types, const_dep = encode_dependency(material_property["dependency"])
                    
                    material_src[property_name].append({
                        "const_dep": [const_dep],
                        "const_dep_size": [len(material_property["data"])],
                        "const_names": [material_property["name"]],
                        "const_types": [const_types],
                        "constants": [fencode(material_property["data"])],
                        "type": material_property["type"]
                    })
        
            data['materials'].append(material_src)

        pass


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

            apply_to = fdecode(restraint_src['apply_to'], dtype('int64'))
            assert len(apply_to) == restraint_src['apply_to_size']

            self.restraints.append({
                "id": restraint_src['id'],
                "name": restraint_src['name'],
                "cs": restraint_src.get('cs', 0),
                "apply_to": apply_to,
                "axes": axes
            })


    def _encode_restraints(self, data):

        data['restraints'] = []
        
        for restraint in self.restraints:

            restraint_src = {
                'id': restraint['id'],
                'name': restraint['name'],
                'cs': restraint['cs'],
                'apply_to': fencode(restraint['apply_to']),
                'apply_to_size': len(restraint['apply_to']),
                'data': [],
                'flag': [],
                'dependency_type': [],
                'dep_var_num': [],
                'dep_var_size': [],
            }

            for axis in restraint['axes']:
                restraint_src['data'].append(fencode(axis['data']))
                restraint_src['flag'].append(axis['flag'])

                const_types, const_dep = encode_dependency(restraint_src["dependency"])

                restraint_src['dependency_type'].append(const_types)
                restraint_src['dep_var_num'].append(const_dep)
                restraint_src['dep_var_size'].append(len(const_dep))

            data['restraints'].append(restraint_src)
            



    def _decode_loads(self, data):

        self.loads = []

        for load_src in data.get('loads', []):

            axes: list[FCLoadAxis] = []
            if 'dep_var_num' in load_src:
                for i, dep_var_num in enumerate(load_src['dep_var_num']):
                    axes.append({
                        "data": fdecode(load_src['data'][i], dtype('float64')),
                        "dependency": decode_dependency(load_src["dependency_type"][i], dep_var_num),
                    })

            apply_to = fdecode(load_src['apply_to'], dtype('int64'))

            assert len(apply_to) == load_src['apply_to_size']

            self.loads.append({
                "id": load_src['id'],
                "name": load_src['name'],
                "cs": load_src['cs'] if 'cs' in load_src else 0,
                "apply_to": apply_to,
                "axes": axes,
                "type": load_src['type'],
            })


    def _encode_loads(self, data):

        data['loads'] = []
        
        for load in self.loads:

            load_src = {
                'id': load['id'],
                'name': load['name'],
                'cs': load['cs'],
                'type': load['type'],
                'apply_to': fencode(load['apply_to']),
                'apply_to_size': len(load['apply_to']),
                'data': [],
                'dependency_type': [],
                'dep_var_num': [],
                'dep_var_size': [],
            }

            for axis in load['axes']:
                load_src['data'].append(fencode(axis['data']))

                const_types, const_dep = encode_dependency(load_src["dependency"])

                load_src['dependency_type'].append(const_types)
                load_src['dep_var_num'].append(const_dep)
                load_src['dep_var_size'].append(len(const_dep))

            data['loads'].append(load_src)
            


    # def _decode_nodesets(self, data):
    #     pass


    # def _encode_nodesets(self, data):
    #     pass

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
            'apply_to_size': len(cs['apply_to']),
            'dofs': cs['dofs'],
            "id" : cs['id'],
            "name": cs['name'],
            "type": cs['type']
        } for cs in self.receivers ]



    def cut(self, cut_function: Callable):

        nodes_mask = [cut_function(el) for el in self.mesh['nodes']['coord']]

        self.mesh['nodes']['coord'] = self.mesh['nodes']['coord'][nodes_mask]
        self.mesh['nodes']['id'] = self.mesh['nodes']['id'][nodes_mask]

        elems_mask = []

        node_set = set(self.mesh['nodes']['id'])

        for i in range(len(self.mesh['elems']['id'])):

            mask_append = True
            nodes = self.mesh['elems']['nodes'][i]
            for node in nodes:
                if node not in node_set:
                    mask_append = False
                    break

            elems_mask.append(mask_append)


        self.mesh['elems']['block'] = self.mesh['elems']['block'][elems_mask]
        self.mesh['elems']['order'] = self.mesh['elems']['order'][elems_mask]
        self.mesh['elems']['parent_id'] = self.mesh['elems']['parent_id'][elems_mask]
        self.mesh['elems']['type'] = self.mesh['elems']['type'][elems_mask]
        self.mesh['elems']['id'] = self.mesh['elems']['id'][elems_mask]
        self.mesh['elems']['nodes'] = [nodes for i, nodes in enumerate(self.mesh['elems']['nodes']) if elems_mask[i]]


        for material in self.materials:
            for key in material['properties']:
                for property in material['properties'][key]:

                    if isinstance(property['dependency'], list) and property['dependency']:
                        for dep in property['dependency']:
                            if dep['type'] == 10:
                                mat_mask = np.in1d(dep['data'], self.mesh['elems']['id'], assume_unique=True)
                                dep['data'] = dep['data'][mat_mask]
                                property['data'] = property['data'][mat_mask]
                            if dep['type'] == 11:
                                mat_mask = np.in1d(dep['data'], self.mesh['nodes']['id'], assume_unique=True)
                                dep['data'] = dep['data'][mat_mask]
                                property['data'] = property['data'][mat_mask]


    def compress(self):
        nodes_id_map = {(index):i+1 for i, index in enumerate(self.mesh['nodes']['id'])}
        elems_id_map = {(index):i+1 for i, index in enumerate(self.mesh['elems']['id'])}

        nodes_count = len(self.mesh['nodes']['id'])
        elems_count = len(self.mesh['elems']['id'])

        self.mesh['nodes']['id'] = np.arange(nodes_count, dtype=np.int32)+1
        self.mesh['elems']['id'] = np.arange(elems_count, dtype=np.int32)+1

        for node in self.mesh['elems']['nodes']:
            for i, n in enumerate(node):
                node[i] = nodes_id_map[n]


        for material in self.materials:
            for key in material['properties']:
                for property in material['properties'][key]:

                    if isinstance(property['dependency'], list) and property['dependency']:
                        for dep in property['dependency']:
                            if isinstance(dep['data'], ndarray):
                                if dep['type'] == 10:
                                    for i, n in enumerate(dep['data']):
                                        dep['data'][i] = elems_id_map[int(n)]
                                if dep['type'] == 11:
                                    for i, n in enumerate(dep['data']):
                                        dep['data'][i] = nodes_id_map[int(n)]
                        


    def stream_fragments(self, dim, rank, offset=0):

        fragments = []

        title = None

        for i in range(len(self.mesh['elems']['id'])):

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
