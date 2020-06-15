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

#TXA version v2.81.4
#Based on ANT version v0.1.8

# import modules
import bpy, bmesh
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        IntProperty,
        PointerProperty,
        )
from math import (
        sin, cos, pi, floor, ceil
        )
from .ant_noise import noise_gen
from .eroder import SaveImageNodes
from .eroder import RestoreImageNodes
from bl_operators.presets import AddPresetBase
import numpy as np
import os
from .ncb.read_json import read
import platform

# ------------------------------------------------------------
# Create a new mesh (object) from verts/edges/faces.
# verts/edges/faces ... List of vertices/edges/faces for the
#                    new mesh (as used in from_pydata).
# name ... Name of the new mesh (& object)

from bpy_extras import object_utils

# #Count nodes in a material node tree including groups
# def CountNodes(node_tree):
    # count = len(node_tree.nodes)
    # for node in node_tree.nodes:
        # if node.type == "GROUP":
            # count = count + len(node.node_tree.nodes)
    # return count

def add_preset_files():
    presets   = bpy.utils.user_resource('SCRIPTS', "presets")
    if platform.system() == 'Windows':
        mypresets = os.path.join(presets, "operator\\txa_ant")
    else:
        mypresets = os.path.join(presets, "operator/txa_ant")
    if not os.path.exists(mypresets):
        os.makedirs(mypresets)
        
# Use NodeCustomBuilder package to add node tree
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
        if not water_plane or not os.path.isfile(filename):    
            filename = os.path.join(os.path.dirname(__file__), "materials" + sep + PrefMat + ".json")
        # print("Used material: ", filename)
        read(filename)
        
    


            
    
       
def AddUVLayer(ob, mesh_size_x, mesh_size_y):
    me = ob.data
    #Add a default UV map
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    # bm.faces.layers.tex.verify()  # currently blender needs both layers.
    
    # print("UVLayer: %s", uv_layer.name)

    # adjust UVs
    for f in bm.faces:
        for l in f.loops:
            luv = l[uv_layer]
            luv.uv[0] = l.vert.co.x / mesh_size_x + 0.5
            luv.uv[1] = l.vert.co.y / mesh_size_y + 0.5
            # print("UV X Calc: ", mesh_size_x, l.vert.co.x, luv.uv[0])
            # print("UV Y Calc: ", mesh_size_y, l.vert.co.y, luv.uv[1])

    bmesh.update_edit_mesh(me)   


def create_mesh_object(context, verts, edges, faces, name):
    # Create new mesh
    mesh = bpy.data.meshes.new(name)
    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, [], faces)

    # Update mesh geometry after adding stuff.
    mesh.update()
    return object_utils.object_data_add(context, mesh, operator=None)


# def MakeErosionImage(ImageName, map):
    # size = map.shape

    # # blank image
    # # image = bpy.data.images.new("MyImage", width=size[0], height=size[1])
    # if ImageName not in bpy.data.images.keys():
        # bpy.data.images.new(ImageName, width=size[0], height=size[1], alpha=True, float_buffer=False)
    # outputImg = bpy.data.images[ImageName] 

    # pixels = np.zeros((size[0],size[1],4), dtype = np.float16)
    # pixels[:,:,-1:] = 1.0
    # pixels[:,:,:1] = 1 - map.reshape(size[0],size[1],1)

    # # flatten list
    # pixels = pixels.ravel()

    # # assign pixels
    # outputImg.pixels = pixels

def MakeHeightImage(meshsize_x, meshsize_y, meshsize_z, tex_size_x, tex_size_y, sub_d_x, props, new_name):

    
    ImageName = new_name+"_heightmap"
    if ImageName in bpy.data.images.keys():
        outputImg = bpy.data.images[ImageName]
        bpy.data.images.remove(outputImg)
    bpy.data.images.new(ImageName, width=tex_size_x, height=tex_size_y, alpha=False, float_buffer=True)
    outputImg = bpy.data.images[ImageName]
    outputImg.colorspace_settings.name = 'Linear'
    
    # print("MakeeightImage: strata: ", props[46])


    pixels = np.zeros((tex_size_y,tex_size_x,4), dtype = np.float16)
    pixels[:,:,-1:] = 1.0
    for i in range(tex_size_x):
        x = meshsize_x * (i / (tex_size_x - 1) - 1 / 2)
        for j in range(tex_size_y):
            y = meshsize_y * (j / (tex_size_y - 1) - 1 / 2)
            pixels[j,i,:1] = noise_gen((x, y, 0), props)
            # pixels[i,j,0] = i/size
            pixels[j,i,1] = pixels[j,i,:1]
            pixels[j,i,2] = pixels[j,i,:1]
            

    # assign pixels
    outputImg.pixels = pixels.ravel()
    outputImg.pack()
    outputImg.update()
    
    #NormalMap
    NormalMapName = new_name+"_normal"
    if NormalMapName in bpy.data.images:
        NormalMapImg = bpy.data.images[NormalMapName]
        bpy.data.images.remove(NormalMapImg)
    bpy.data.images.new(NormalMapName, width=tex_size_x, height=tex_size_y, alpha=False, float_buffer=True)
    NormalMapImg = bpy.data.images[NormalMapName]
    NormalMapImg.colorspace_settings.name = 'Linear'
    pixels = np.zeros((tex_size_y,tex_size_x,4), dtype = np.float16)
    pixels[:,:,-1:] = 1.0
    # calculate normals
    HMap = np.array(outputImg.pixels)
    HMap.shape = (outputImg.size[1], outputImg.size[0], 4)
    center = HMap[:,:,0]
    zy, zx = np.gradient(center)  

    normal = np.dstack((-zx/meshsize_x, -zy*center.shape[0]/(meshsize_y*center.shape[1]), np.ones_like(center)/(meshsize_z*center.shape[0])))
    n = np.linalg.norm(normal, axis=2)
    normal[:, :, 0] /= n
    normal[:, :, 1] /= n
    normal[:, :, 2] /= n

    # offset and rescale values to be in 0-255
    normal += 1
    normal /= 2

    pixels[:,:,0] = normal[:,:,0]
    pixels[:,:,1] = normal[:,:,1]
    pixels[:,:,2] = normal[:,:,2]
    
    NormalMapImg.pixels = pixels.ravel()
    NormalMapImg.pack()
    NormalMapImg.update()
    
        
    #BeachMap if water plane is enabled
    if props[47]: 
        BeachName = new_name+"_beach"
        if BeachName in bpy.data.images:
            BeachImg = bpy.data.images[BeachName]
            bpy.data.images.remove(BeachImg)
        bpy.data.images.new(BeachName, width=tex_size_x, height=tex_size_y, alpha=False, float_buffer=True)
        BeachImg = bpy.data.images[BeachName]
        BeachImg.colorspace_settings.name = 'Linear'
        pixels = np.zeros((tex_size_y,tex_size_x,4), dtype = np.float16)
        pixels[:,:,-1:] = 1.0
        BeachImg.pixels = pixels.ravel()
        BeachImg.pack()
        BeachImg.update()

    return outputImg


# Generate XY Grid
def grid_gen(sub_d_x, sub_d_y, tex_size_x, tex_size_y, tri, meshsize_x, meshsize_y, meshsize_z, props, water_plane, water_level, new_name):
    # print("Values: ", sub_d_x, sub_d_y, meshsize_x, meshsize_y, props[22])
    # verts = [[-meshsize_x/2,-meshsize_y/2,0], [meshsize_x/2,-meshsize_y/2,0], [meshsize_x/2,meshsize_y/2,0], [-meshsize_x/2,meshsize_y/2,0]]
    # faces = [[0,1,2,3]]	

    sub_d_x = round(meshsize_x/meshsize_y)+1
    if sub_d_x < 2:
        sub_d_x = 2
    sub_d_y = round(meshsize_y/meshsize_x)+1
    if sub_d_y < 2:
        sub_d_y = 2
    # print("Values: ", sub_d_x, sub_d_y, meshsize_x, meshsize_y, props[22])
    
    verts = []
    faces = []
    for i in range (0, sub_d_x):
        x = meshsize_x * (i / (sub_d_x - 1) - 1 / 2)
        for j in range(0, sub_d_y):
            y = meshsize_y * (j / (sub_d_y - 1) - 1 / 2)
            if water_plane:
                z = water_level
            else:
                # z = noise_gen((x, y, 0), props)
                z = 0.

            verts.append((x,y,z))

    count = 0
    for i in range (0, sub_d_y * (sub_d_x - 1)):
        if count < sub_d_y - 1 :
            A = i + 1
            B = i
            C = (i + sub_d_y)
            D = (i + sub_d_y) + 1
            if tri:
                faces.append((A, B, D))
                faces.append((B, C, D))
            else:
                faces.append((A, B, C, D))
            count = count + 1
        else:
            count = 0

    # print("Make Height Map")
    if not water_plane:
        HeightMap = MakeHeightImage(meshsize_x, meshsize_y, meshsize_z, tex_size_x, tex_size_y, sub_d_x, props, new_name)
    # AddMaterial(BumpMap)
    return verts, faces


# Generate UV Sphere
def sphere_gen(sub_d_x, sub_d_y, tri, meshsize, props, water_plane, water_level):
    verts = []
    faces = []
    sub_d_x += 1
    sub_d_y += 1
    for i in range(0, sub_d_x):
        for j in range(0, sub_d_y):
            u = sin(j * pi * 2 / (sub_d_y - 1)) * cos(-pi / 2 + i * pi / (sub_d_x - 1)) * meshsize / 2
            v = cos(j * pi * 2 / (sub_d_y - 1)) * cos(-pi / 2 + i * pi / (sub_d_x - 1)) * meshsize / 2
            w = sin(-pi / 2 + i * pi / (sub_d_x - 1)) * meshsize / 2
            if water_plane:
                h = water_level
            else:
                h = noise_gen((u, v, w), props) / meshsize
            verts.append(((u + u * h), (v + v * h), (w + w * h)))

    count = 0
    for i in range (0, sub_d_y * (sub_d_x - 1)):
        if count < sub_d_y - 1 :
            A = i + 1
            B = i
            C = (i + sub_d_y)
            D = (i + sub_d_y) + 1
            if tri:
                faces.append((A, B, D))
                faces.append((B, C, D))
            else:
                faces.append((A, B, C, D))
            count = count + 1
        else:
            count = 0

    return verts, faces


# ------------------------------------------------------------
# Do refresh - redraw
class AntLandscapeRefresh(bpy.types.Operator):
    bl_idname = "mesh.txa_ant_landscape_refresh"
    bl_label = "Refresh"
    bl_description = "Refresh landscape with current settings"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return (ob.txaant_landscape and not ob.txaant_landscape['sphere_mesh'])


    def execute(self, context):
        # turn off undo
        # undo = bpy.context.preferences.edit.use_global_undo
        # bpy.context.preferences.edit.use_global_undo = False

        # ant object items
        obj = bpy.context.active_object

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        if obj and obj.txaant_landscape.keys():
            ob = obj.txaant_landscape
            obi = ob.items()
            prop = []
            for i in range(len(obi)):
                prop.append(obi[i][1])

            # redraw verts
            mesh = obj.data

            if ob['vert_group'] != "" and ob['vert_group'] in obj.vertex_groups:
                vertex_group = obj.vertex_groups[ob['vert_group']]
                gi = vertex_group.index
                for v in mesh.vertices:
                    for g in v.groups:
                        if g.group == gi:
                            v.co[2] = 0.0
                            v.co[2] = vertex_group.weight(v.index) * noise_gen(v.co, prop)
            else:
                for v in mesh.vertices:
                    v.co[2] = 0.0
                    v.co[2] = noise_gen(v.co, prop)
            mesh.update()
        else:
            pass

        # restore pre operator undo state
        # context.preferences.edit.use_global_undo = undo

        return {'FINISHED'}

# ------------------------------------------------------------
# Do regenerate
class AntLandscapeRegenerate(bpy.types.Operator):
    bl_idname = "mesh.txa_ant_landscape_regenerate"
    bl_label = "Regenerate"
    bl_description = "Regenerate landscape with current settings"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.txaant_landscape


    def execute(self, context):

        # turn off undo
        # undo = bpy.context.preferences.edit.use_global_undo
        # bpy.context.preferences.edit.use_global_undo = False
        wobj = None
        
        nodedict = SaveImageNodes()
        # print("Starting Regen")

        scene = bpy.context.scene
        # ant object items
        # ant object items
        obj = bpy.context.active_object
        # print("TTTTTTT: ", context.scene.EroderMats)
        # if context.scene.EroderMats == '':
            # context.scene.EroderMats = 'Forrested'

        if obj and obj.txaant_landscape.keys():
            # print("Regen Allowed")
            ob = obj.txaant_landscape
            # print("ant_landscape:", obj.txaant_landscape)
            obi = ob.items()
            ant_props = []
            for i in range(len(obi)):
                ant_props.append(obi[i][1])
            # print("Regen: Strata:", len(obi), obi[46])
            
            #get existing modifer details
            # print("obj.modifers length: ", len(obj.modifiers))
            if "ANTSubsurf" in obj.modifiers:
                levels = obj.modifiers["ANTSubsurf"].levels
            else:
                levels = 7

            new_name = obj.name

            # Main function, create landscape mesh object
            if ob['sphere_mesh']:
                # sphere
                verts, faces = sphere_gen(
                        ob['subdivision_y'],
                        ob['subdivision_x'],
                        ob['tri_face'],
                        ob['mesh_size'],
                        ant_props,
                        False,
                        0.0
                        )
                new_ob = create_mesh_object(context, verts, [], faces, new_name).object
                if ob['remove_double']:
                    new_ob.select_set(True)
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
                    bpy.ops.object.mode_set(mode = 'OBJECT')
            else:
                # grid
                verts, faces = grid_gen(
                        ob['subdivision_x'],
                        ob['subdivision_y'],
                        ob['tex_size_x'],
                        ob['tex_size_y'],
                        ob['tri_face'],
                        ob['mesh_size_x'],
                        ob['mesh_size_y'],
                        ob['mesh_size_z'],
                        ant_props,
                        False,
                        0.0,
                        new_name
                        )
                # new_ob = create_mesh_object(context, verts, [], faces, new_name).object
                new_ob = create_mesh_object(context, verts, [], faces, new_name)
                # print("Grid_Gen Run")
                
                #Add subsurf and display modifiers
                SubMod = new_ob.modifiers.new(name="ANTSubsurf", type='SUBSURF')
                SubMod.subdivision_type = 'SIMPLE'
                SubMod.levels = levels
                DisplaceTexName = new_name + "_antdisplace"
                if DisplaceTexName not in bpy.data.textures:
                    ANTDisplaceTex = bpy.data.textures.new(DisplaceTexName, type = 'IMAGE')
                else:
                    ANTDisplaceTex = bpy.data.textures[DisplaceTexName]
                ANTDisplaceTex.image = bpy.data.images[new_name+'_heightmap']
                ANTDisplaceMod = new_ob.modifiers.new("ANTDisplace", type='DISPLACE')
                ANTDisplaceMod.texture = ANTDisplaceTex                
                ANTDisplaceMod.direction = 'Z'                
                ANTDisplaceMod.texture_coords = 'UV'                
                ANTDisplaceMod.strength = ob['mesh_size_z']                
                ANTDisplaceMod.mid_level = 0.0                
                new_ob.select_set(True)
                bpy.ops.object.mode_set(mode = 'EDIT')
                AddUVLayer(new_ob, ob['mesh_size_x'], ob['mesh_size_y'])
                bpy.ops.object.mode_set(mode = 'OBJECT')
                # print("Object location 1: ",obj.location)

            new_ob.select_set(True)

            if ob['smooth_mesh']:
                bpy.ops.object.shade_smooth()

            # Landscape Material
            if ob['land_material'] != "" and ob['land_material'] in bpy.data.materials:
                mat = bpy.data.materials[ob['land_material']]
                bpy.context.object.data.materials.append(mat)

            # Water plane
            if ob['water_plane']:
                water_name = new_name + "_water"
                #delete old water plane
                if new_name + "_water" not in bpy.context.scene.objects:
                    # wobj_old = bpy.context.scene.objects[water_name]
                    # wobj_old.select_set(True)
                    # context.view_layer.objects.active = wobj_old
                    # bpy.ops.object.delete(use_global=False)

                # else:    
                    if ob['sphere_mesh']:
                        # sphere
                        verts, faces = sphere_gen(
                                ob['subdivision_y'],
                                ob['subdivision_x'],
                                ob['tri_face'],
                                ob['mesh_size'],
                                ant_props,
                                ob['water_plane'],
                                ob['water_level']
                                )
                        wobj = create_mesh_object(context, verts, [], faces, new_name+"_plane").object
                        if ob['remove_double']:
                            wobj.select_set(True)
                            bpy.ops.object.mode_set(mode = 'EDIT')
                            bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
                            bpy.ops.object.mode_set(mode = 'OBJECT')
                    else:
                        # grid
                        verts, faces = grid_gen(
                            ob['subdivision_x'],
                            ob['subdivision_y'],
                            ob['tex_size_x'],
                            ob['tex_size_y'],
                            ob['tri_face'],
                            ob['mesh_size_x']*2,
                            ob['mesh_size_y']*2,
                            ob['mesh_size_z'],
                            ant_props,
                            ob['water_plane'],
                            ob['water_level'],
                            new_name + "_water"
                            )
                        
                        # print("Grid_Gen Run water")
                        wobj = create_mesh_object(context, verts, [], faces, new_name+"_water")
                        wobj.name = water_name
                        wobj.select_set(True)
                        bpy.ops.object.mode_set(mode = 'EDIT')
                        AddUVLayer(wobj, ob['mesh_size_x'], ob['mesh_size_y'])
                        bpy.ops.object.mode_set(mode = 'OBJECT')
                        AddLandscapeMaterial(wobj, "water", new_name, False)

                if ob['smooth_mesh']:
                    bpy.ops.object.shade_smooth()

                # Water Material
                
                # if ob['water_material'] != "" and ob['water_material'] in bpy.data.materials:
                    # mat = bpy.data.materials[ob['water_material']]
                    # bpy.context.object.data.materials.append(mat)

            # Loc Rot Scale
            # if ob['water_plane']:
            if wobj is not None:
                wobj.location = obj.location
                wobj.rotation_euler = obj.rotation_euler
                wobj.scale = obj.scale
                wobj.select_set(False)

            new_ob.location = obj.location
            new_ob.rotation_euler = obj.rotation_euler
            new_ob.scale = obj.scale

            # Store props
            new_ob = store_properties(ob, new_ob)

            # Delete old object
            new_ob.select_set(False)

            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.delete(use_global=False)

            # Select landscape and make active
            new_ob.select_set(True)
            context.view_layer.objects.active = new_ob
            new_ob.name = new_name
            AddLandscapeMaterial(new_ob, "NormalOnly", new_name, False)

            #Restore any lost image references in materials
            RestoreImageNodes(nodedict)
    
            # restore pre operator undo state
            # context.preferences.edit.use_global_undo = undo

        return {'FINISHED'}


# ------------------------------------------------------------
# Z normal value to vertex group (Slope map)
class AntVgSlopeMap(bpy.types.Operator):
    bl_idname = "mesh.txa_ant_slope_map"
    bl_label = "Weight from Slope"
    bl_description = "A.N.T. Slope Map - z normal value to vertex group weight"
    bl_options = {'REGISTER', 'UNDO'}

    z_method: EnumProperty(
            name="Method:",
            default='SLOPE_Z',
            items=[
                ('SLOPE_Z', "Z Slope", "Slope for planar mesh"),
                ('SLOPE_XYZ', "Sphere Slope", "Slope for spherical mesh")
                ])
    group_name: StringProperty(
            name="Vertex Group Name:",
            default="Slope",
            description="Name"
            )
    select_flat: BoolProperty(
            name="Vert Select:",
            default=True,
            description="Select vertices on flat surface"
            )
    select_range: FloatProperty(
            name="Vert Select Range:",
            default=0.0,
            min=0.0,
            max=1.0,
            description="Increase to select more vertices on slopes"
            )

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'MESH')


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def execute(self, context):
        message = "Popup Values: %d, %f, %s, %s" % \
            (self.select_flat, self.select_range, self.group_name, self.z_method)
        # self.report({'INFO'}, message)

        bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.context.active_object
        dim = ob.dimensions

        if self.select_flat:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.context.tool_settings.mesh_select_mode = [True, False, False]
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.vertex_group_add()
        vg_normal = ob.vertex_groups.active

        for v in ob.data.vertices:
            if self.z_method == 'SLOPE_XYZ':
                zval = (v.co.normalized() * v.normal.normalized()) * 2 - 1
            else:
                zval = v.normal[2]

            vg_normal.add([v.index], zval, 'REPLACE')

            if self.select_flat:
                if zval >= (1.0 - self.select_range):
                    v.select_set(True)

        vg_normal.name = self.group_name

        bpy.ops.paint.weight_paint_toggle()
        return {'FINISHED'}


# ------------------------------------------------------------
# draw properties

def draw_ant_refresh(self, context):
    layout = self.layout
    row = layout.row()
    row.menu("MESH_MT_main_ant_presets", text=bpy.types.MESH_MT_main_ant_presets.bl_label)
    row.operator(AddPresetTxa_Ant.bl_idname, text="", icon='ZOOM_IN')
    row.operator(AddPresetTxa_Ant.bl_idname, text="", icon='ZOOM_OUT').remove_active = True        
    if self.auto_refresh is False:
        self.refresh = False
    elif self.auto_refresh is True:
        self.refresh = True
    row = layout.box().row()
    split = row.split()
    split.scale_y = 1.5
    split.prop(self, "auto_refresh", toggle=True, icon_only=True, icon='AUTO')
    split.prop(self, "refresh", toggle=True, icon_only=True, icon='FILE_REFRESH')


def draw_ant_main(self, context, generate=True):
    layout = self.layout
    box = layout.box()
    box.prop(self, "show_main_settings", toggle=True)

    if self.show_main_settings:
        if generate:
            row = box.row(align=True)
            split = row.split(align=True)
            split.prop(self, "at_cursor", toggle=True, icon_only=True, icon='PIVOT_CURSOR')
            split.prop(self, "smooth_mesh", toggle=True, icon_only=True, icon='SHADING_SOLID')
            split.prop(self, "tri_face", toggle=True, icon_only=True, icon='MESH_DATA')

            # if not self.sphere_mesh:
                # row = box.row(align=True)
                # row.prop(self, "sphere_mesh", toggle=True)
            # else:
                # row = box.row(align=True)
                # split = row.split(factor=0.5, align=True)
                # split.prop(self, "sphere_mesh", toggle=True)
                # split.prop(self, "remove_double", toggle=True)

            box.prop(self, "ant_terrain_name")
            # box.prop_search(self, "land_material",  bpy.data, "materials")

        # col = box.column(align=True)
        # col.prop(self, "subdivision_x")
        # col.prop(self, "subdivision_y")
        col = box.column(align=True)
        col.prop(self, "tex_size_x")
        col.prop(self, "tex_size_y")
        col = box.column(align=True)
        if self.sphere_mesh:
            col.prop(self, "mesh_size")
        else:
            col.prop(self, "mesh_size_x")
            col.prop(self, "mesh_size_y")


def draw_ant_noise(self, context, generate=True):
    layout = self.layout
    box = layout.box()
    box.prop(self, "show_noise_settings", toggle=True)
    if self.show_noise_settings:
        box.prop(self, "noise_type")
        if self.noise_type == "blender_texture":
            box.prop_search(self, "texture_block", bpy.data, "textures")
        else:
            box.prop(self, "basis_type")

        col = box.column(align=True)
        col.prop(self, "random_seed")
        col = box.column(align=True)
        col.prop(self, "noise_offset_x")
        col.prop(self, "noise_offset_y")
        if self.sphere_mesh == True or generate == False:
            col.prop(self, "noise_offset_z")
        col.prop(self, "noise_size_x")
        col.prop(self, "noise_size_y")
        if self.sphere_mesh == True or generate == False:
            col.prop(self, "noise_size_z")

        col = box.column(align=True)
        col.prop(self, "noise_size")

        col = box.column(align=True)
        if self.noise_type == "multi_fractal":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
        elif self.noise_type == "ridged_multi_fractal":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "gain")
        elif self.noise_type == "hybrid_multi_fractal":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "gain")
        elif self.noise_type == "hetero_terrain":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
        elif self.noise_type == "fractal":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
        elif self.noise_type == "turbulence_vector":
            col.prop(self, "noise_depth")
            col.prop(self, "amplitude")
            col.prop(self, "frequency")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)
        elif self.noise_type == "variable_lacunarity":
            box.prop(self, "vl_basis_type")
            box.prop(self, "distortion")
        elif self.noise_type == "marble_noise":
            box.prop(self, "marble_shape")
            box.prop(self, "marble_bias")
            box.prop(self, "marble_sharp")
            col = box.column(align=True)
            col.prop(self, "distortion")
            col.prop(self, "noise_depth")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)
        elif self.noise_type == "shattered_hterrain":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "distortion")
        elif self.noise_type == "strata_hterrain":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "distortion", text="Strata")
        elif self.noise_type == "ant_turbulence":
            col.prop(self, "noise_depth")
            col.prop(self, "amplitude")
            col.prop(self, "frequency")
            col.prop(self, "distortion")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)
        elif self.noise_type == "vl_noise_turbulence":
            col.prop(self, "noise_depth")
            col.prop(self, "amplitude")
            col.prop(self, "frequency")
            col.prop(self, "distortion")
            col.separator()
            box.prop(self, "vl_basis_type")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)
        elif self.noise_type == "vl_hTerrain":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "distortion")
            col.separator()
            box.prop(self, "vl_basis_type")
        elif self.noise_type == "distorted_heteroTerrain":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "distortion")
            col.separator()
            box.prop(self, "vl_basis_type")
        elif self.noise_type == "double_multiFractal":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "offset")
            col.prop(self, "gain")
            col.separator()
            box.prop(self, "vl_basis_type")
        elif self.noise_type == "rocks_noise":
            col.prop(self, "noise_depth")
            col.prop(self, "distortion")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)
        elif self.noise_type == "slick_rock":
            col.prop(self, "noise_depth")
            col.prop(self, "dimension")
            col.prop(self, "lacunarity")
            col.prop(self, "gain")
            col.prop(self, "offset")
            col.prop(self, "distortion")
            col.separator()
            box.prop(self, "vl_basis_type")
        elif self.noise_type == "planet_noise":
            col.prop(self, "noise_depth")
            col.separator()
            row = col.row(align=True)
            row.prop(self, "hard_noise", expand=True)

        # Effects mix
        col = box.column(align=False)
        box.prop(self, "fx_type")
        if self.fx_type != "0":
            if int(self.fx_type) <= 12:
                box.prop(self, "fx_bias")

            box.prop(self, "fx_mix_mode")
            col = box.column(align=True)
            col.prop(self, "fx_mixfactor")

            col = box.column(align=True)
            col.prop(self, "fx_loc_x")
            col.prop(self, "fx_loc_y")
            col.prop(self, "fx_size")

            col = box.column(align=True)
            col.prop(self, "fx_depth")
            if self.fx_depth != 0:
                col.prop(self, "fx_frequency")
                col.prop(self, "fx_amplitude")
            col.prop(self, "fx_turb")

            col = box.column(align=True)
            row = col.row(align=True).split(factor=0.92, align=True)
            row.prop(self, "fx_height")
            # col.prop(self, "fx_invert", toggle=True, text="Invert")
            row.prop(self, "fx_invert", toggle=True, text="", icon='ARROW_LEFTRIGHT')
            col.prop(self, "fx_offset")


def draw_ant_displace(self, context, generate=True):
    layout = self.layout
    box = layout.box()
    box.prop(self, "show_displace_settings", toggle=True)
    if self.show_displace_settings:
        if not generate:
            col = box.column(align=False)
            col.prop(self, "direction", toggle=True)

        col = box.column(align=True)
        row = col.row(align=True).split(factor=0.92, align=True)
        row.prop(self, "height")
        row.prop(self, "height_invert", toggle=True, text="", icon='ARROW_LEFTRIGHT')
        col.prop(self, "height_offset")
        col.prop(self, "maximum")
        col.prop(self, "minimum")
        if generate:
            if not self.sphere_mesh:
                col = box.column()
                col.prop(self, "edge_falloff")
                if self.edge_falloff != "0":
                    col = box.column(align=True)
                    col.prop(self, "edge_level")
                    if self.edge_falloff in ["2", "3"]:
                        col.prop(self, "falloff_x")
                    if self.edge_falloff in ["1", "3"]:
                        col.prop(self, "falloff_y")

        col = box.column()
        col.prop(self, "strata_type")
        if self.strata_type != "0":
            col = box.column()
            col.prop(self, "strata")

        if not generate:
            col = box.column(align=False)
            col.prop_search(self, "vert_group",  bpy.context.object, "vertex_groups")


def draw_ant_water(self, context):
    layout = self.layout
    box = layout.box()
    col = box.column()
    col.prop(self, "water_plane", toggle=True)
    if self.water_plane:
        col = box.column(align=True)
        col.prop_search(self, "water_material",  bpy.data, "materials")
        col = box.column()
        col.prop(self, "water_level")


# Store propereties
def store_properties(operator, ob):
    ob.txaant_landscape.ant_terrain_name = operator.ant_terrain_name
    ob.txaant_landscape.at_cursor = operator.at_cursor
    ob.txaant_landscape.smooth_mesh = operator.smooth_mesh
    ob.txaant_landscape.tri_face = operator.tri_face
    ob.txaant_landscape.sphere_mesh = operator.sphere_mesh
    ob.txaant_landscape.land_material = operator.land_material
    ob.txaant_landscape.water_material = operator.water_material
    ob.txaant_landscape.texture_block = operator.texture_block
    ob.txaant_landscape.subdivision_x = operator.subdivision_x
    ob.txaant_landscape.subdivision_y = operator.subdivision_y
    ob.txaant_landscape.mesh_size_x = operator.mesh_size_x
    ob.txaant_landscape.mesh_size_y = operator.mesh_size_y
    ob.txaant_landscape.mesh_size = operator.mesh_size
    ob.txaant_landscape.random_seed = operator.random_seed
    ob.txaant_landscape.noise_offset_x = operator.noise_offset_x
    ob.txaant_landscape.noise_offset_y = operator.noise_offset_y
    ob.txaant_landscape.noise_offset_z = operator.noise_offset_z
    ob.txaant_landscape.noise_size_x = operator.noise_size_x
    ob.txaant_landscape.noise_size_y = operator.noise_size_y
    ob.txaant_landscape.noise_size_z = operator.noise_size_z
    ob.txaant_landscape.noise_size = operator.noise_size
    ob.txaant_landscape.noise_type = operator.noise_type
    ob.txaant_landscape.basis_type = operator.basis_type
    ob.txaant_landscape.vl_basis_type = operator.vl_basis_type
    ob.txaant_landscape.distortion = operator.distortion
    ob.txaant_landscape.hard_noise = operator.hard_noise
    ob.txaant_landscape.noise_depth = operator.noise_depth
    ob.txaant_landscape.amplitude = operator.amplitude
    ob.txaant_landscape.frequency = operator.frequency
    ob.txaant_landscape.dimension = operator.dimension
    ob.txaant_landscape.lacunarity = operator.lacunarity
    ob.txaant_landscape.offset = operator.offset
    ob.txaant_landscape.gain = operator.gain
    ob.txaant_landscape.marble_bias = operator.marble_bias
    ob.txaant_landscape.marble_sharp = operator.marble_sharp
    ob.txaant_landscape.marble_shape = operator.marble_shape
    ob.txaant_landscape.height = operator.height
    ob.txaant_landscape.height_invert = operator.height_invert
    ob.txaant_landscape.height_offset = operator.height_offset
    ob.txaant_landscape.maximum = operator.maximum
    ob.txaant_landscape.minimum = operator.minimum
    ob.txaant_landscape.edge_falloff = operator.edge_falloff
    ob.txaant_landscape.edge_level = operator.edge_level
    ob.txaant_landscape.falloff_x = operator.falloff_x
    ob.txaant_landscape.falloff_y = operator.falloff_y
    ob.txaant_landscape.strata_type = operator.strata_type
    ob.txaant_landscape.strata = operator.strata
    ob.txaant_landscape.water_plane = operator.water_plane
    ob.txaant_landscape.water_level = operator.water_level
    ob.txaant_landscape.vert_group = operator.vert_group
    ob.txaant_landscape.remove_double = operator.remove_double
    ob.txaant_landscape.fx_mixfactor = operator.fx_mixfactor
    ob.txaant_landscape.fx_mix_mode = operator.fx_mix_mode
    ob.txaant_landscape.fx_type = operator.fx_type
    ob.txaant_landscape.fx_bias = operator.fx_bias
    ob.txaant_landscape.fx_turb = operator.fx_turb
    ob.txaant_landscape.fx_depth = operator.fx_depth
    ob.txaant_landscape.fx_frequency = operator.fx_frequency
    ob.txaant_landscape.fx_amplitude = operator.fx_amplitude
    ob.txaant_landscape.fx_size = operator.fx_size
    ob.txaant_landscape.fx_loc_x = operator.fx_loc_x
    ob.txaant_landscape.fx_loc_y = operator.fx_loc_y
    ob.txaant_landscape.fx_height = operator.fx_height
    ob.txaant_landscape.fx_offset = operator.fx_offset
    ob.txaant_landscape.fx_invert = operator.fx_invert
    ob.txaant_landscape.tex_size_x = operator.tex_size_x
    ob.txaant_landscape.tex_size_y = operator.tex_size_y
    ob.txaant_landscape.mesh_size_z = operator.mesh_size_z
    # print("Store tex_size_x:", ob.txaant_landscape['tex_size_x'])
    # print("Store Strata:",  ob.txaant_landscape.strata)
    return ob


# ------------------------------------------------------------
# "name": "ErosionR"
# "author": "Michel Anders, Ian Huish"

from random import random as rand
from math import tan, radians
from .eroder import Grid
# from .stats import Stats
# from .utils import numexpr_available


def availableVertexGroupsOrNone(self, context):
    groups = [ ('None', 'None', 'None', 1) ]
    return groups + [(name, name, name, n+1) for n,name in enumerate(context.active_object.vertex_groups.keys())]

class MESH_MT_ant_presets(bpy.types.Menu):
    bl_label = "Erosion Presets"
    preset_subdir = "../addons/txa_ant/presets"
    preset_subdir = "../addons/txa_ant/presets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset

class MESH_MT_main_ant_presets(bpy.types.Menu):
    bl_label = "Main Presets"
    preset_subdir = "../addons/txa_ant/mainpresets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset
    
class AddPresetTxa_Ant(AddPresetBase, bpy.types.Operator):
    '''Add a Object Draw Preset'''
    bl_idname = "mesh.addpresettxa_ant"
    bl_label = "Add erosion Preset"
    preset_menu = "MESH_MT_ant_presets"

    # variable used for all preset values
    preset_defines = [
        "pEP = bpy.context.scene.txaEroderProps"
        ]

    # properties to store in the preset
    preset_values = [
        "pEP.PrefMat",
        "pEP.Iterations",
        "pEP.IterRiver",
        "pEP.Ks",
        "pEP.Kc",
        "pEP.Kdep",
        "pEP.Kr",
        "pEP.Kv",
        "pEP.Kev",
        "pEP.Ef",
        "pEP.IterSoilMovement",
        "pEP.IterAva",
        "pEP.Kt",
        "pEP.Ktr",
        "pEP.Pa",
        "pEP.Pn",
        "pEP.Kz",
        "pEP.smooth"
        ]

    # where to store the preset
    preset_subdir = "../addons/txa_ant/presets"
         
class EroderProps(bpy.types.PropertyGroup):        
    Iterations: IntProperty(
            name="Iterations",
            description="Number of overall iterations",
            default=1,
            min=1,
            soft_max=100
            )
    IterRiver: IntProperty(
            name="River Iterations",
            description="Number of river iterations",
            default=300,
            min=1,
            soft_max=1000
            )
    IterAva: IntProperty(
            name="Avalanche Iterations",
            description="Number of avalanche iterations",
            default=1,
            min=0,
            soft_max=10
            )
    IterDiffuse: IntProperty(
            name="Diffuse Iterations",
            description="Number of diffuse iterations",
            default=5,
            min=1,
            soft_max=10
            )
    IterSoilMovement: IntProperty(
            name="Soil Movement Iterations",
            description="Number of soil movement iterations",
            default=1,
            min=1,
            soft_max=100
            )
#Not used at this time
    Ef: FloatProperty(
            name="Rain on Plains",
            description="1 gives equal rain across the terrain, 0 rains more at the mountain tops",
            default=0.0,
            min=0,
            max=1
            )
    Kd: FloatProperty(
            name="Kd",
            description="Thermal diffusion rate (1.0 is a fairly high rate)",
            default=0.1,
            min=0,
            soft_max=100
            )
    Kt: FloatProperty(
            name="Kt",
            description="Maximum stable rock talus angle",
            default=radians(80),
            min=0,
            max=radians(90),
            subtype='ANGLE'
            )
    Ktr: FloatProperty(
            name="Ktr",
            description="Maximum stable river talus angle",
            default=radians(40),
            min=0,
            max=radians(90),
            subtype='ANGLE'
            )
    Kr: FloatProperty(
            name="Rain amount",
            description="Total Rain amount",
            default=0.5,
            min=0,
            soft_max=1,
            precision=3
            )
    Kv: FloatProperty(
            name="Rain variance",
            description="Rain variance (0 is constant, 1 is uniform)",
            default=0,
            min=0,
            max=1
            )
    userainmap: BoolProperty(
            name="Use rain map",
            description="Use active vertex group as a rain map",
            default=True
            )
    Ks: FloatProperty(
            name="Soil solubility",
            description="Soil solubility - how quickly water quickly reaches saturation point",
            default=0.5,
            min=0,
            soft_max=1
            )
    Kdep: FloatProperty(
            name="Deposition rate",
            description="Sediment deposition rate - how quickly silt is laid down once water stops flowing quickly",
            default=0.1,
            min=0,
            soft_max=1
            )
    Kz: FloatProperty(name="Fluvial Erosion Rate",
            description="Amount of sediment moved each main iteration - if 0, then rivers are formed but the mesh is not changed",
            default=0.3,
            min=0,
            soft_max=20
            )
    Kc: FloatProperty(
            name="Carrying capacity",
            description="Base sediment carrying capacity",
            default=0.9,
            min=0,
            soft_max=1
            )
    Ka: FloatProperty(
            name="Slope dependence",
            description="Slope dependence of carrying capacity (not used)",
            default=1.0,
            min=0,
            soft_max=2
            )
    Kev: FloatProperty(
            name="Evaporation",
            description="Evaporation Rate per grid square in % - causes sediment to be dropped closer to the hills",
            default=.5,
            min=0,
            soft_max=2
            )
    numexpr: BoolProperty(
            name="Numexpr",
            description="Use numexpr module (if available)",
            default=True
            )
    Pd: FloatProperty(
            name="Diffusion Amount",
            description="Diffusion probability",
            default=0.2,
            min=0,
            max=1
            )
    Pa: FloatProperty(
            name="River Sensitivty",
            description="River Sensitivty",
            default=0.9,
            min=0,
            max=1
            )
    Pn: FloatProperty(
            name="Noise Effect",
            description="Randomize Avalanche Effects",
            default=0.5,
            min=0,
            max=1
            )
    Pw: FloatProperty(
            name="River Amount",
            description="Water erosion probability",
            default=1,
            min=0,
            max=1
            )
    PrefMat: EnumProperty(
            name="Material",
            description="Preferred Material",
            items=[("Forrested","Forrested","",1), ("Volcano","Vocano","",2), ("Masks","Masks","",3)],
            # items=[("Simple","Simple","",1), ("Masks","Masks","",2)],
            default='Forrested',
            # min=0,
            # max=1
            )
    BeachHeight: FloatProperty(
            name="Beach Height",
            description="Height above water where beach starts",
            default=0.01,
            min=0,
            max=10
            )
    BeachSlope: FloatProperty(
            name="Beach Slope",
            description="Beach Slope with 0 as flat and 1 is no change",
            default=0.5,
            min=-10,
            max=1
            )
    FoamDepth: FloatProperty(
            name="Foam Depth",
            description="Depth of water when foam is found",
            default=0.05,
            min=-10,
            max=1
            )
    BeachErosion: FloatProperty(
            name="Beach Erosion",
            description="Amount of fluvial erosion on beach and foam",
            default=0.5,
            min=0,
            max=1
            )
    smooth: BoolProperty(
            name="Smooth",
            description="Set smooth shading",
            default=True
            )
    showiterstats: BoolProperty(
            name="Iteration Stats",
            description="Show iteraration statistics",
            default=False
            )
    showmeshstats: BoolProperty(name="Mesh Stats",
            description="Show mesh statistics",
            default=False
            )

class MESH_OT_ImageSave(bpy.types.Operator):
    bl_idname = "mesh.txa_imagesave"
    bl_label = "Save Images"
    bl_description = "Save the generated images. "
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    @classmethod
    def poll(cls, context):
        return bpy.path.abspath('//') != ''
        
    def SaveImage(self, image, scn):
        img_path = bpy.path.abspath('//')
        image.file_format = 'OPEN_EXR'
        img_file = image.name+'.exr'
        img_name = image.name
        # print("Image filename: ", img_path+img_file)
        image.save_render(img_path+img_file, scene=scn)
        # bpy.data.images.remove(image)
        # bpy.ops.image.open(filepath=img_path+img_file)
        # image = bpy.data.images[img_file]
        # image.name = img_name
        # image.update()
        image.pack()
        os.remove(img_path+img_file)

    def execute(self, context):
        scn = bpy.data.scenes.new('img_settings')
        scn.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        scn.render.image_settings.color_mode = 'RGBA'
        scn.render.image_settings.color_depth = '32'
        img = bpy.data.images['WaterMaps']
        self.SaveImage(img, scn)
        img = bpy.data.images['AvalancheMaps']
        self.SaveImage(img, scn)
        img = bpy.data.images['ErodedHeight']
        self.SaveImage(img, scn)
        bpy.data.scenes.remove(scn, do_unlink=True)
        return {'FINISHED'}
            
class Eroder(bpy.types.Operator):
    bl_idname = "mesh.txa_eroder"
    bl_label = "Erosion"
    bl_description = "Apply various kinds of erosion to a square ANT-Landscape grid. "
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}


    # stats = Stats()
    counts= {}
    

    def execute(self, context):
    
        ob = context.active_object
        pEP = context.scene.txaEroderProps
        # me = ob.data

        HMap = bpy.data.images[ob.name+'_heightmap']
        # print("Starting erode - Image Name for Grid", HMap.name)
        g = Grid.fromImage(HMap)
        # print("Grid created, starting river iterations")
        for i in range(pEP.Iterations):
            g.sedimentcalc(pEP.Kc)
            if pEP.IterRiver > 0:
                for i in range(pEP.IterRiver):
                    g.rivergeneration(pEP.Kr, pEP.Kv, None, pEP.Ks, pEP.Kdep, pEP.Ka, pEP.Kev/100, 0,0,0,0, pEP.numexpr)
                    
            if pEP.IterSoilMovement > 0:
                for i in range(pEP.IterSoilMovement):
                            
                    if pEP.Kz > 0:
                        g.fluvial_erosion(pEP.Kr, pEP.Kv, pEP.userainmap, pEP.Ks, pEP.Kz, pEP.Ka, pEP.Kdep, 0,0,0,0, pEP.numexpr,ob.txaant_landscape.water_plane,ob.txaant_landscape.water_level, pEP.BeachHeight, pEP.BeachErosion)
                        # self.counts['water']+=1
                    
                    if pEP.Kt < radians(90):
                        # print("Repose Angle Kt: ", pEP.Kt)
                        for k in range(pEP.IterAva):
                            # since dx and dy are scaled to 1, tan(Kt) is the height for a given angle
                            g.avalanche(tan(pEP.Kt), tan(pEP.Ktr), pEP.IterAva, 1.0 - pEP.Pa, pEP.Pn, pEP.numexpr, ob.txaant_landscape.mesh_size_x,ob.txaant_landscape.mesh_size_y,ob.txaant_landscape.mesh_size_z)
                            
            #Beach erosion
            if ob.txaant_landscape.water_plane:
                g.beach_erosion(ob.txaant_landscape.water_level, pEP.BeachHeight, pEP.BeachSlope, pEP.FoamDepth)
                            # self.counts['avalanche']+=1
            # g.makegradient()
        g.toImage(ob.txaant_landscape.mesh_size_x, ob.txaant_landscape.mesh_size_y, ob.txaant_landscape.mesh_size_z, ob.name)
        del g
        # print("AddLandscapeMaterial with water_plane: ", ob.txaant_landscape.water_plane)
        AddLandscapeMaterial(ob, context.scene.EroderMats, ob.name, ob.txaant_landscape.water_plane)
        if ob.name + "_water" in context.scene.objects:
            ob_water = context.scene.objects[ob.name + "_water"]
            AddLandscapeMaterial(ob_water, "water", ob.name, ob.txaant_landscape.water_plane)
        # print("Trying to use eroded height")
        if ob.name+"_antdisplace" in bpy.data.textures:
            # print("Using eroded height")
            bpy.data.textures[ob.name+"_antdisplace"].image = bpy.data.images[ob.name+"_erodedheight"]


        return {'FINISHED'}

class ANTMAIN_PT_eroder(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Eroder Params"
    bl_idname = "TXA_ANTMAIN_PT_eroder"
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "data"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TXA Landscape"
    


    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob.txaant_landscape.keys() if ob else False

    def draw(self,context):
        add_preset_files()
        
        pEP = context.scene.txaEroderProps
        layout = self.layout

        layout.operator('mesh.txa_eroder', text="Landscape Eroder", icon='SMOOTHCURVE')
        # layout.operator('mesh.txa_imagesave', text="Pack Generated Images")
        row = layout.row()
        row.menu("MESH_MT_ant_presets", text=bpy.types.MESH_MT_ant_presets.bl_label)
        row.operator(AddPresetTxa_Ant.bl_idname, text="", icon='ZOOM_IN')
        row.operator(AddPresetTxa_Ant.bl_idname, text="", icon='ZOOM_OUT').remove_active = True        

        layout.label(text="Preferred Material")
        # layout.prop(pEP, 'PrefMat')
        layout.prop(context.scene, 'EroderMats')
        layout.prop(pEP, 'Iterations')

        # # box = layout.box()
        # # col = box.column(align=True)
        # layout.label(text="Thermal (Diffusion)")
        # layout.prop(pEP, 'Kd')
        # layout.prop(pEP, 'IterDiffuse')
        layout.label(text="River Generation")
        layout.prop(pEP, 'IterRiver')
        layout.prop(pEP, 'Ks')
        layout.prop(pEP, 'Kc')
        layout.prop(pEP, 'Kdep')
        layout.prop(pEP, 'Kr')
        layout.prop(pEP, 'Kv')
        layout.prop(pEP, 'Kev')
        # layout.prop(pEP, 'Ef')

        layout.label(text="Soil Movment")
        layout.prop(pEP, 'IterSoilMovement')

        # box = layout.box()
        # col = box.column(align=True)
        layout.label(text="Avalanche (Talus)")
        layout.prop(pEP, 'IterAva')
        layout.prop(pEP, 'Kt')
        layout.prop(pEP, 'Ktr')
        layout.prop(pEP, 'Pa')
        layout.prop(pEP, 'Pn')

        # box = layout.box()
        # col = box.column(align=True)
        layout.label(text="River erosion")
        layout.prop(pEP, 'Kz')

        # Beach
        if context.object.txaant_landscape.water_plane:
            layout.label(text="Beach")
            layout.prop(pEP, 'BeachHeight')
            layout.prop(pEP, 'BeachSlope')
            layout.prop(pEP, 'FoamDepth')
            layout.prop(pEP, 'BeachErosion')
        layout.prop(pEP,'smooth')
