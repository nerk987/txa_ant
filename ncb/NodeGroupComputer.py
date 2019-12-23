# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy
from . import ExtraSetting
from . import ExtraSettingComp

def find_all_groupnodes(base_group_nodes):

    result_groups = []

    for base_node in base_group_nodes:

        if base_node not in result_groups:
            result_groups.append(base_node)

        index_groups = []
        new_index_group = []
        index_groups.append(base_node)

        while index_groups != []:
            for base_sub_group in index_groups:
                for node in base_sub_group.nodes:
                    if node.type == 'GROUP':
                        if node.node_tree != None:
                            if node.node_tree not in new_index_group:
                                new_index_group.append(node.node_tree)
                                result_groups.append(node.node_tree)

            index_groups = new_index_group
            new_index_group = []

    return result_groups

def write_groupnodetrees(allgroups):

    dict_groups = {}
    dict_groups['groups'] = []
    nodes = {}
    nodes['node'] = []
    links = {}
    links['links'] = []
    inputs = {}
    outputs = {}
    new_groups = []
    all_groups_here = []


    while allgroups != []:
        for group in allgroups:
            if group != None:
                if (group.name.startswith('__node__') == False):
                    group.name = '__node__' + group.name

                if group.name not in all_groups_here:
                    all_groups_here.append(group.name)
                    for node in group.nodes:



                        if (node.parent != None):
                            parent = node.parent.name
                        else:
                            parent = ''

                        if(node.type == 'GROUP'):
                            if (node.node_tree != None):
                                name_node_tree = node.node_tree.name
                            else:
                                name_node_tree = ''

                            if(name_node_tree.startswith('__node__') == False):
                                name_node_tree = '__node__' + name_node_tree

                            nodes['node'].append({
                                'node': node.bl_idname,
                                'name': node.name,
                                'label': node.label,
                                'node_tree': name_node_tree,
                                'location': [node.location[0], node.location[1]],
                                'parent': parent,
                                'hide': node.hide,
                                'hidden_outputs': [],
                                'height': node.height,
                                'width': node.width,
                                'extra_settings': [-1, -1, -1]
                            })
                            new_groups.append(node.node_tree)
                        elif(node.type == 'GROUP_INPUT'):

                            outputs['outputs'] = []

                            for input in node.outputs:
                                if(input.name != ''):
                                    outputs['outputs'].append([input.bl_idname, input.name])

                            nodes['node'].append({
                                'node': node.bl_idname,
                                'name': node.name,
                                'label': node.label,
                                'outputs': outputs['outputs'],
                                'location': [node.location[0], node.location[1]],
                                'parent': parent,
                                'hide': node.hide,
                                'hidden_outputs': [],
                                'height': node.height,
                                'width': node.width,
                                'extra_settings': [-1, -1, -1]
                            })

                        elif(node.type == 'GROUP_OUTPUT'):

                            inputs['inputs'] = []

                            for input in node.inputs:
                                if(input.name != ''):
                                    inputs['inputs'].append([input.bl_idname, input.name])

                            nodes['node'].append({
                                'node': node.bl_idname,
                                'name': node.name,
                                'label': node.label,
                                'inputs': inputs['inputs'],
                                'location': [node.location[0], node.location[1]],
                                'hide': node.hide,
                                'parent': parent,
                                'hide': node.hide,
                                'hidden_outputs': [],
                                'height': node.height,
                                'width': node.width,
                                'extra_settings': [-1, -1, -1]
                            })

                        elif (node.type == 'FRAME'):

                            if (node.name.startswith('__node__') == False):
                                node.name = '__node__' + node.name

                            nodes['node'].append({
                                'node': node.bl_idname,
                                'name': node.name,
                                'label': node.label,
                                'color': [node.color[0], node.color[1], node.color[2]],
                                'hide': node.hide,
                                'height': node.height,
                                'width': node.width,
                                'use_color': node.use_custom_color,
                                'location': [node.location[0], node.location[1]],
                                'parent': parent,
                                'hide': node.hide,
                                'hidden_outputs': [],
                                'extra_settings': [-1, -1, -1]
                            })

                        else:

                            if node.parent != None:
                                nimi = node.parent.name
                            else:
                                nimi = ''

                            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                                nodes = ExtraSettingComp.writeExtraSettings(nodes, node, '', nimi, 'SUB_TREE')
                            else:
                                nodes = ExtraSetting.writeExtraSettings(nodes, node, '', nimi, 'SUB_TREE')

                        if (len(node.inputs) > 0):
                            for index, input in enumerate(node.inputs):
                                if(input.is_linked):

                                    nimi = input.links[0].from_node.name

                                    links['links'].append([nimi, input.links[0].from_socket.name, node.name, index])


                dict_groups['groups'].append ({
                    'name': group.name,
                    'nodes': nodes['node'],
                    'links': links['links']
                })

                nodes['node'] = []
                links['links'] = []




        allgroups = new_groups
        new_groups = []



    return dict_groups

