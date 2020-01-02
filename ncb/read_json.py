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
# Author: HaiKalle
# Based on NodeCustomBuilder version v0.0.50
# Included with TXA Landscape with the generous permission of HaiKalle 


import bpy
import json
from . import ExtraSetting
from . import ExtraSettingComp

def read(filename):
    # print("JSON filename: ", filename)


    # if (bpy.context.active_object.material_slots.keys() == [] and bpy.context.area.ui_type != 'CompositorNodeTree'):
        # newmat = bpy.data.materials.new('Material')
        # newmat.use_nodes = True
        # bpy.context.active_object.data.materials.append(newmat)

    # if(bpy.context.area.ui_type == 'CompositorNodeTree'):
        # if bpy.context.scene.use_nodes == False:
            # bpy.context.scene.use_nodes = True

        # active_nodetree = bpy.context.scene.node_tree
    # else:
        # if (bpy.context.space_data.shader_type == 'OBJECT'):
    active_nodetree = bpy.context.active_object.active_material.node_tree
        # elif (bpy.context.space_data.shader_type == 'WORLD'):
            # active_nodetree = bpy.data.worlds[0].node_tree


    if(len(active_nodetree.nodes) > 0):
        for node in active_nodetree.nodes:
            node.select = False

    type_not = []
    used_frames = []
    new_nodes = []
    imported_frames = []
    frame_and_location = []

    with open(filename) as json_file:
        data = json.load(json_file)

        ''' Material Settings'''
        active_material = bpy.context.object.active_material
        # if (bpy.context.space_data.shader_type == 'OBJECT'):
        if data.get('material'):
            for material in data['material']:

                active_material.use_backface_culling = material['use_backface_culling']
                active_material.blend_method = material['blend_method']
                active_material.shadow_method = material['shadow_method']
                active_material.alpha_threshold = material['alpha_threshold']
                active_material.use_screen_refraction = material['use_screen_refraction']
                active_material.refraction_depth = material['refraction_depth']
                active_material.use_sss_translucency = material['use_sss_translucency']
                active_material.pass_index = material['pass_index']


        ''' Let's first read external nodetrees and build them '''

        for frame in data['frames']:

            new_frame = active_nodetree.nodes.new(frame['node'])
            new_frame.name = frame['name']
            #new_frame.location = frame['location']
            new_frame.use_custom_color = frame['use_color']
            new_frame.color[0] = frame['color'][0]
            new_frame.color[1] = frame['color'][1]
            new_frame.color[2] = frame['color'][2]
            new_frame.height = frame['height']
            new_frame.width = frame['width']
            new_frame.label = frame['label']
            if frame.get('label_size'):
                new_frame.label_size = frame['label_size']

            imported_frames.append(new_frame.name)

        for frame in data['frames']:
            if (frame['parent'] != ''):
                try:
                    active_nodetree.nodes[frame['name']].parent = active_nodetree.nodes[frame['parent']]
                except:
                    pass

        for group in data['groups']:
            if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                group_nodetree = bpy.data.node_groups.new(type="CompositorNodeTree", name=group['name'])
            else:
                group_nodetree = bpy.data.node_groups.new(type="ShaderNodeTree", name=group['name'])

            for node in group['nodes']:
                new_node = group_nodetree.nodes.new(node['node'])
                new_node.name = node['name']
                try:
                    new_node.label = node['label']
                except:
                    pass
                # print ('NODE name: ' + node['name'])
                new_node.hide = node['hide']
                new_node.height = node['height']
                new_node.width = node['width']
                if (new_node.type != 'FRAME'):
                    new_node.location = node['location']
                if node['parent'] != '':
                    new_node.parent = group_nodetree.nodes[node['parent']]

                if (node['extra_settings'][0] != -1):
                    if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                        ExtraSettingComp.readExtraSettings(node['extra_settings'], new_node)
                    else:
                        ExtraSetting.readExtraSettings(node['extra_settings'], new_node)

                if(new_node.type == 'FRAME'):
                    new_node.use_custom_color = node['use_color']
                    new_node.color[0] = node['color'][0]
                    new_node.color[1] = node['color'][1]
                    new_node.color[2] = node['color'][2]
                    #new_node.location = node['location']
                    new_node.height = node['height']
                    new_node.width = node['width']
                    new_node.label = node['label']
                    if node.get('label_size'):
                        new_node.label_size = node['label_size']
                    frame_and_location.append([node['name'],node['location']])
                    if node['parent'] != '':
                        new_node.parent = group_nodetree.nodes[node['parent']]


                elif(new_node.type == 'GROUP_OUTPUT'):
                    for input in node['inputs']:
                        group_nodetree.outputs.new(input[0], input[1])
                elif (new_node.type == 'GROUP_INPUT'):
                    for input in node['outputs']:
                        group_nodetree.inputs.new(input[0], input[1])

                else:
                    if (bpy.context.area.ui_type != 'CompositorNodeTree'):
                        if (len(node['hidden_outputs']) > 0):
                            for output in node['hidden_outputs']:
                                new_node.outputs[output[0]].hide = True

        #bpy.data.node_groups['NodeGroup'].nodes['Frame'].location = []
        ''' Next, let's jump to the main node tree and start to build it node by node'''

        for p in data['nodes']:

            if (p['main_socket_type'] == ''):

                node_new = active_nodetree.nodes.new(p['node'])

                if(p['parent'] != ''):
                    try:
                        active_nodetree.nodes[-1].parent = active_nodetree.nodes[p['parent']]
                    except:
                        print('ei yoim')

                active_nodetree.nodes[-1].name = p['name']
                try:
                    active_nodetree.nodes[-1].label = p['label']
                except:
                    pass
                active_nodetree.nodes[-1].height = p['height']
                active_nodetree.nodes[-1].width = p['width']
                if(active_nodetree.nodes[-1].type == 'GROUP'):
                    if p['node_tree'] != '':
                        active_nodetree.nodes[-1].node_tree = bpy.data.node_groups[p['node_tree']]
                active_nodetree.nodes[-1].location = p['location']
                new_nodes.append(node_new.name)

                if(p['extra_settings'][0] != -1):
                    if(bpy.context.area.ui_type == 'CompositorNodeTree'):
                        ExtraSettingComp.readExtraSettings(p['extra_settings'], node_new)
                    else:
                        ExtraSetting.readExtraSettings(p['extra_settings'], node_new)


            else:

                if (active_nodetree.nodes.active.inputs[p['main_socket_type']].is_linked == False):
                    node_new = active_nodetree.nodes.new(p['node'])

                    if (p['parent'] != ''):
                        try:
                            active_nodetree.nodes[-1].parent = active_nodetree.nodes[p['parent']]
                        except:
                            print('heee')

                    active_nodetree.nodes[-1].name = p['name']
                    active_nodetree.nodes[-1].height = p['height']
                    active_nodetree.nodes[-1].width = p['width']
                    if (active_nodetree.nodes[-1].type == 'GROUP'):
                        active_nodetree.nodes[-1].node_tree = bpy.data.node_groups[p['node_tree']]
                    active_nodetree.nodes[-1].location = p['location']
                    new_nodes.append(node_new.name)

                    if (p['extra_settings'][0] != -1):
                        if (bpy.context.area.ui_type == 'CompositorNodeTree'):
                            ExtraSettingComp.readExtraSettings(p['extra_settings'], node_new)
                        else:
                            ExtraSetting.readExtraSettings(p['extra_settings'], node_new)
                else:
                    type_not.append(p['main_socket_type'])
            if (bpy.context.area.ui_type != 'CompositorNodeTree'):
                if (len(p['hidden_outputs']) > 0):
                    for output in p['hidden_outputs']:
                        node_new.outputs[output[0]].hide = True



        # print('new_nodes:', new_nodes)

        for new_node_name in new_nodes:
            objekti = active_nodetree.nodes[new_node_name]
            # print('\nOB:',objekti.name)
            if(objekti.parent != ''):
                temp = objekti.parent
                while (temp != None):

                    if temp.name not in used_frames:
                        used_frames.append(temp.name)
                    if(temp.parent != None):
                        temp = temp.parent
                    else:
                        temp = None

        for frame in data['frames']:

             active_nodetree.nodes[frame['name']].location = frame['location']

        for link in data['links']:
            if link['main_socket_type'] in type_not:
                pass
            else:
                create_link = True

                try:
                    active_nodetree.nodes[link['output_node']]
                except:
                    create_link = False

                try:
                    active_nodetree.nodes[link['input_node']]
                except:
                    create_link = False

                if(create_link):
                    try:
                        active_nodetree.links.new(active_nodetree.nodes[link['output_node']].outputs[link['output_socket']],
                                              active_nodetree.nodes[link['input_node']].inputs[link['input_socket']])
                    except:
                        pass



    ''' Asetetaan nodetreet group nodiin ja tehdaan linkitys nodetreee ryhmissa'''

    for group in data['groups']:
        group_tree = bpy.data.node_groups[group['name']]

        if(bpy.context.area.ui_type == 'CompositorNodeTree'):

            for node in group['nodes']:
                if (node['node'] == 'CompositorNodeGroup'):
                    group_tree.nodes[node['name']].node_tree = bpy.data.node_groups[node['node_tree']]

        else:

            for node in group['nodes']:
                if(node['node'] == 'ShaderNodeGroup'):
                    if node['node_tree'] != '':
                        try:
                            print('nodeNAME: ' + group_tree.nodes[node['name']].name)
                        except:
                            pass
                        # print ('NODETREE: ' + node['node_tree'])
                        try:
                            group_tree.nodes[node['name']].node_tree = bpy.data.node_groups[node['node_tree']]
                        except:
                            pass

    for group in data['groups']:
        group_tree = bpy.data.node_groups[group['name']]

        for link in group['links']:

            try:
                group_tree.links.new(group_tree.nodes[link[0]].outputs[link[1]], group_tree.nodes[link[2]].inputs[link[3]])
            except:
                pass

    for group in bpy.data.node_groups:
        for node in group.nodes:
            if(node.name.startswith('__node__')):
                if node.type == 'FRAME':
                    for seek in frame_and_location:
                        if seek[0] == node.name:
                            node.location = seek[1]
                            break

    for node in active_nodetree.nodes:
        if node.name.startswith('__node__'):
            node.name = node.name[8:]

    for node in bpy.data.node_groups:
        if node.name.startswith('__node__'):
            node.name = node.name[8:]




