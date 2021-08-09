# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Another Noise Tool - Functions
# Jimmy Hazevoet

# ErosionR:
# Michel Anders, Ian Huish

#TXA version v3.00.0 For Blender version 3.0
#Based on ANT version v0.1.8

# import modules
import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        IntProperty,
        PointerProperty,
        )
import os
from .ncb.read_json import read
import platform



def AddLandscapeMaterial(ob, PrefMat, ob_name, water_plane):

    # nodedict = SaveImageNodes()

    newmat = False
    
    matName = ob_name + "_" + PrefMat

    mat = bpy.data.materials.get(matName)

    if  mat is None:
        newmat = True
        mat = bpy.data.materials.new(matName)
        mat.use_nodes = True

        nt = mat.node_tree
        for node in nt.nodes:
            nt.nodes.remove(node)
        
        
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)
        
    #If adding new material, use NodeCustomBuiler read_json to add nodes
    if newmat:
        if platform.system() == 'Windows':
            sep = "\\"
        else:
            sep = "/"
        filename = os.path.join(os.path.dirname(__file__), "materials" + sep + "island" + sep + PrefMat + ".json")
        # print("Island material: ", water_plane, filename)
        if PrefMat == 'pbr':
            filename = os.path.join(os.path.dirname(__file__), "materials" + sep + "pbr" + sep + PrefMat + ".json")
        elif not water_plane or not os.path.isfile(filename):    
            filename = os.path.join(os.path.dirname(__file__), "materials" + sep + PrefMat + ".json")
        # print("Used material: ", filename)
        read(filename)
        
    

# ------------------------------------------------------------
# Do refresh - redraw
class AntLandscapeBake(bpy.types.Operator):
    bl_idname = "object.txa_ant_bake"
    bl_label = "Bake"
    bl_description = "Bake procedural material to PBR"
    bl_options = {'REGISTER', 'UNDO'}
    
    def RecordLink(self, ip, input):
        NodeDetail = {}
        NodeDetail["link"] = True
        NodeDetail["input"] = input
        # NodeDetail["to"] = ip.links[0].to_socket
        NodeDetail["from"] = ip.links[0].from_socket
        print("NodeDetail.from: ", NodeDetail["from"])
        return NodeDetail

    def RecordVector(self, ip):
        print("RecordVector Links: ", ip.links)
        if len(ip.links) > 0:
            return self.RecordLink(ip, True)
        else:
            NodeDetail = {}
            NodeDetail["link"] = False
            NodeDetail["vector"] = ip.default_value
            return NodeDetail

    def RecordFloat(self, ip):
        print("RecordFloat Links: ", ip.links)
        if len(ip.links) > 0:
            return self.RecordLink(ip, True)
        else:
            NodeDetail = {}
            NodeDetail["link"] = False
            NodeDetail["float"] = ip.default_value
            return NodeDetail

    def ReplaceWithEmission(self, node_tree, pbrTexture):
        #for each Principled node, record basecolor, roughness, normal connections or setting
        # node_tree = bake_mat.node_tree
        print("pbrTexture: ", pbrTexture)
        for n in [n for n in node_tree.nodes if n.type == 'GROUP']:
            n.node_tree = n.node_tree.copy()
            self.ReplaceWithEmission(n.node_tree, pbrTexture)
        for n in [n for n in node_tree.nodes if n.type == 'TEX_IMAGE']:
            n.select = False
        for n in [n for n in node_tree.nodes if n.type == 'BSDF_PRINCIPLED']:
            print("Node", n.type)
            for ip in n.inputs:
                # print("ip.id: ",ip.identifier,  pbrTexture['type'])
                if ip.identifier == pbrTexture['id']:
                    # print("input_type: ", pbrTexture['id'])
                    if pbrTexture['input_type'] == 'vector':
                        NodeSave = self.RecordVector(ip)
                    if pbrTexture['input_type'] == 'float':
                        NodeSave = self.RecordFloat(ip)
            if len(n.outputs[0].links) > 0:
                NodeSave["to"] = n.outputs[0].links[0].to_socket
            print("NodeSave:", NodeSave)
            
            #replace the Prinipled node with emission node with correct connections
            node_tree.nodes.remove(n)
            nn = node_tree.nodes.new('ShaderNodeEmission')
            if pbrTexture['type'] == 'normal2':
                nn1 = node_tree.nodes.new('ShaderNodeVectorMath')
                nn1.operation = 'MULTIPLY'
                nn1.inputs[1].default_value = [0.5, 0.5, 0.5]
                nn2 = node_tree.nodes.new('ShaderNodeVectorMath')
                nn2.operation = 'ADD'
                nn2.inputs[1].default_value = [0.5, 0.5, 0.5]
                node_tree.links.new(nn2.inputs[0], nn1.outputs[0])
                node_tree.links.new(nn.inputs[0], nn2.outputs[0])
            else:
                nn1 = nn
            if NodeSave["link"]:
                print("Add link: ", NodeSave["from"])
                node_tree.links.new(nn1.inputs[0], NodeSave["from"])
                if "to" in NodeSave.keys():
                    print("Add to link: ", NodeSave["from"])
                    node_tree.links.new(NodeSave["to"], nn.outputs[0])
            else:
                print("Adding scalar")
                node_tree.links.new(NodeSave["to"], nn.outputs[0])
                if pbrTexture['input_type'] == 'vector':
                    print("Vector required")
                    if nn1.inputs[0].identifier == 'Color': #Emission input
                        print("Input is Color - vector")
                        print("Adding vector: ", NodeSave["vector"])
                        nn1.inputs[0].default_value[0] = NodeSave["vector"][0]
                        nn1.inputs[0].default_value[1] = NodeSave["vector"][1]
                        nn1.inputs[0].default_value[2] = NodeSave["vector"][2]
                    if nn1.inputs[0].identifier == 'Vector': # Normal input
                        print("Input is vector - vector")
                        print("Adding a normal vector: ", NodeSave["vector"])
                        nn1.inputs[0].default_value[0] = 0.0
                        nn1.inputs[0].default_value[1] = 0.0
                        nn1.inputs[0].default_value[2] = 1.0
                if pbrTexture['input_type'] == 'float':
                    print("Float required")
                    if nn1.inputs[0].identifier == 'Color':
                        print("Input is Color - Float")
                        print("Adding float: ", NodeSave["float"])
                        nn1.inputs[0].default_value[0] = NodeSave["float"]
                        nn1.inputs[0].default_value[1] = NodeSave["float"]
                        nn1.inputs[0].default_value[2] = NodeSave["float"]
        


    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return (ob.txaant_landscape and not ob.txaant_landscape['sphere_mesh'])


    def execute(self, context):
        #PBR textures to create
        # pbrTextures = [{'type':'basecolor', 'id':'Base Color', 'input_type':'vector'}]
        # pbrTextures = [{'type':'basecolor', 'id':'Base Color', 'input_type':'vector'}, {'type':'roughness', 'id':'Roughness', 'input_type':'float'}]
        # pbrTextures = [{'type':'basecolor', 'id':'Base Color', 'input_type':'vector'}, {'type':'roughness', 'id':'Roughness', 'input_type':'float'}, {'type':'normal2', 'id':'Normal', 'input_type':'vector'}]
        pbrTextures = [{'type':'basecolor', 'id':'Base Color', 'input_type':'vector'}, {'type':'roughness', 'id':'Roughness', 'input_type':'float'}, {'type':'normal2', 'id':'Normal', 'input_type':'vector'}, {'type':'emmission', 'id':'Emission', 'input_type':'vector'}]
        #Identify object
        print("Starting")
        saveRenderEngine = bpy.context.scene.render.engine
        context.scene.render.engine = 'CYCLES'
        print("Render Engine: ", context.scene.render.engine)
        ob = context.active_object
        current_mat = ob.active_material
        print("Current Mat: ", current_mat.name)
        
        #for each pbr type:
        for pbrTexture in pbrTextures:

            #Copy current material to *_bake
            # ob.data.materials.append(current_mat.copy())
            # ob.active_material_index = len(ob.material_slots) - 1
            bake_mat = current_mat.copy()
            bake_mat.name = current_mat.name + "_bake"
            save_mat = ob.material_slots[0].material
            ob.material_slots[0].material = bake_mat
            print("Current, bake, save: ", current_mat.name, bake_mat.name, save_mat.name)
            # bake_mat = ob.active_material
                
                
            #for each Principled node, record the relevant input and output details
            node_tree = bake_mat.node_tree
            if pbrTexture['type'] != 'emmission':
                self.ReplaceWithEmission(node_tree, pbrTexture)
                
            #create texture output node and a pbr image if required
            found = False
            name = ob.name
            img_name = name+"_" + pbrTexture['type']
            for n in [n for n in node_tree.nodes if n.type == 'TEX_IMAGE']:
                found = False

                if n.image != None and n.image.name == img_name:
                    n.select = True
                    node_tree.nodes.active = n
                    found = True
                    break
            if not found:
                node = node_tree.nodes.new("ShaderNodeTexImage")
                node.select = True
                node_tree.nodes.active = node
                if img_name in bpy.data.images:
                    node.image = bpy.data.images[img_name]
                    #Todo hadle resolution changes
                else:
                    # float_buf = (pbrTexture["type"] == 'Normal2')
                    node.image = bpy.data.images.new(img_name, ob.txaant_landscape.tex_size_x, ob.txaant_landscape.tex_size_y)
                    node.image.pack()
                    if pbrTexture['type'] == 'basecolor':
                        node.image.colorspace_settings.name = "sRGB"
                    else:
                        node.image.colorspace_settings.name = "Non-Color"

            img = bpy.data.images[img_name]

                
            #bake emmision
            print("Bake Result: ", bpy.ops.object.bake(type='EMIT'))
            img.pack()
            img.update()
            if pbrTexture['type'] == 'basecolor':
                img.colorspace_settings.name = 'sRGB'
            else:
                img.colorspace_settings.name = 'Linear'

            ob.material_slots[0].material = save_mat
            
            #remove bake material
            # for n in [n for n in bake_mat.node_tree.nodes if n.type == 'GROUP']:
                # bpy.data.node_groups.remove(n.node_tree)
            # bpy.data.materials.remove(bake_mat)
        
        
            
        #Add a pbr material
        AddLandscapeMaterial(ob, 'pbr', ob.name, False)       
        #Replace texture names as required
        
        #Clean up
        
        context.scene.render.engine = saveRenderEngine
        return {'FINISHED'}
