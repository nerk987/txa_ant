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

# Another Noise Tool - Suite (W.I.P.)
# Jimmy Hazevoet 5/2017
#TXA version v2.91.1 Presets fix
#Based on ANT version v0.1.8

bl_info = {
    "name": "TXA Landscape",
    "author": "Jimmy Hazevoet/Michel Anders/Ian Huish",
    # "version": (0, 1, 8), 
    "version": (2, 91, 1),
    "blender": (2, 81, 0),
    "location": "View3D > Tool Shelf",
    "description": "Another Noise Tool: Textured Version",
    "warning": "",
    "wiki_url": "https://github.com/nerk987/txa_ant",
    "tracker_url": "http://github.com/nerk987/txa_ant/issues",
    "category": "Add Mesh",
}

if "bpy" in locals():
    import importlib
    importlib.reload(add_mesh_ant_landscape)
    importlib.reload(mesh_ant_displace)
    importlib.reload(ant_functions)
    importlib.reload(ant_noise)
    # importlib.reload(Textures)
    importlib.reload(ncb.read_json)
    # importlib.reload(txaExtraSetting)
    # importlib.reload(txaExtraSettingComp)
else:
    from txa_ant import add_mesh_ant_landscape
    from txa_ant import mesh_ant_displace
    from txa_ant import ant_functions
    from txa_ant import ant_noise
    # from txa_ant import Textures
    from txa_ant.ncb import read_json
    # from txa_ant import txaExtraSetting
    # from txa_ant import txaExtraSettingComp

import bpy
import os
import platform

from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        PointerProperty,
        EnumProperty,
        )
from .ant_functions import (
        draw_ant_refresh,
        draw_ant_main,
        draw_ant_noise,
        draw_ant_displace,
        EroderProps,
        MESH_MT_ant_presets,
        MESH_MT_main_ant_presets,
        AddPresetTxa_Ant,
        )

# ------------------------------------------------------------
# Menu's and panels

def menu_func_eroder(self, context):
    ob = bpy.context.active_object
    if ob and (ob.txaant_landscape.keys() and not ob.txaant_landscape['sphere_mesh']):
        self.layout.operator('mesh.txa_eroder', text="TXA Landscape Eroder", icon='SMOOTHCURVE')


def menu_func_landscape(self, context):
    self.layout.operator('mesh.txa_landscape_add', text="TXA Landscape", icon="RNDCURVE")


# Landscape Add Panel
class AntLandscapeAddPanel(bpy.types.Panel):
    bl_idname = "TXA_ANTLANDSCAPE_PT_add"
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "TXA Landscape"
    bl_category = "Create"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        col = self.layout.column()
        col.operator('mesh.txa_landscape_add', text="Landscape", icon="RNDCURVE")


# # Landscape Tools:
# class AntLandscapeToolsPanel(bpy.types.Panel):
    # bl_space_type = "VIEW_3D"
    # bl_context = "objectmode"
    # bl_region_type = "UI"
    # bl_label = "Landscape Tools"
    # bl_category = "TXA Landscape"
    # bl_options = {'DEFAULT_CLOSED'}

    # @classmethod
    # def poll(cls, context):
        # ob = bpy.context.active_object
        # return (ob and ob.type == 'MESH')

    # def draw(self, context):
        # layout = self.layout
        # ob = context.active_object
        # col = layout.column()
        # col.operator('mesh.txa_ant_displace', text="Mesh Displace", icon="RNDCURVE")
        # col.operator('mesh.txa_ant_slope_map', icon='GROUP_VERTEX')
        # if ob.txaant_landscape.keys() and not ob.txaant_landscape['sphere_mesh']:
            # col.operator('mesh.txa_eroder', text="Landscape Eroder", icon='SMOOTHCURVE')


# Landscape Main Settings
class AntMainSettingsPanel(bpy.types.Panel):
    bl_idname = "TXA_ANTMAIN_PT_layout"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_label = "Landscape Main"
    bl_category = "TXA Landscape"

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob.txaant_landscape.keys() if ob else False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = bpy.context.active_object
        ant = ob.txaant_landscape
        # box = layout.box()
        # col = box.column(align=False)
        # col.scale_y = 1.5
        layout.operator('mesh.txa_ant_landscape_regenerate', text="Regenerate", icon="TRACKING_FORWARDS")
        # row = box.row(align=True)
        # split = row.split(align=True)
        layout.prop(ant, "smooth_mesh", toggle=True, text="Smooth", icon='NONE')
        layout.prop(ant, "tri_face", toggle=True, text="Triangulate", icon='NONE')
        if ant.sphere_mesh:
            layout.prop(ant, "remove_double", toggle=True, text="Remove Doubles", icon='NONE')
        layout.prop(ant, "ant_terrain_name")
        # layout.prop_search(ant, "land_material",  bpy.data, "materials")
        # col = box.column(align=True)
        # layout.prop(ant, "subdivision_x")
        # layout.prop(ant, "subdivision_y")
        layout.prop(ant, "tex_size_x")
        layout.prop(ant, "tex_size_y")
        # layout = box.column(align=True)
        if ant.sphere_mesh:
            layout.prop(ant, "mesh_size")
        else:
            layout.prop(ant, "mesh_size_x")
            layout.prop(ant, "mesh_size_y")
            layout.prop(ant, "mesh_size_z")
        layout.prop(ant, "water_plane")
        layout.prop(ant, "water_level")



# Landscape Noise Settings
class AntNoiseSettingsPanel(bpy.types.Panel):
    bl_idname = "TXA_ANTNOISE_PT_layout"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_label = "Landscape Noise"
    bl_category = "TXA Landscape"

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob.txaant_landscape.keys() if ob else False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = bpy.context.active_object
        ant = ob.txaant_landscape
        box = layout.box()
        # col = box.column(align=True)
        # col.scale_y = 1.5
        # if ant.sphere_mesh:
        layout.operator('mesh.txa_ant_landscape_regenerate', text="Regenerate", icon="LOOP_FORWARDS")
        # else:
            # layout.operator('mesh.txa_ant_landscape_refresh', text="Refresh", icon="FILE_REFRESH")

        layout.prop(ant, "noise_type")
        if ant.noise_type == "blender_texture":
            layout.prop_search(ant, "texture_block", bpy.data, "textures")
        else:
            layout.prop(ant, "basis_type")

        # col = box.column(align=True)
        layout.prop(ant, "random_seed")
        # col = box.column(align=True)
        layout.prop(ant, "noise_offset_x")
        layout.prop(ant, "noise_offset_y")
        if ant.sphere_mesh:
            layout.prop(ant, "noise_offset_z")
        layout.prop(ant, "noise_size_x")
        layout.prop(ant, "noise_size_y")
        if ant.sphere_mesh:
            layout.prop(ant, "noise_size_z")
        # col = box.column(align=True)
        layout.prop(ant, "noise_size")

        # col = box.column(align=True)
        if ant.noise_type == "multi_fractal":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
        elif ant.noise_type == "ridged_multi_fractal":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "gain")
        elif ant.noise_type == "hybrid_multi_fractal":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "gain")
        elif ant.noise_type == "hetero_terrain":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
        elif ant.noise_type == "fractal":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
        elif ant.noise_type == "turbulence_vector":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "amplitude")
            layout.prop(ant, "frequency")
            # layout.separator()
            # layout = layout.layout(align=True)
            layout.prop(ant, "hard_noise", expand=True)
        elif ant.noise_type == "variable_lacunarity":
            box.prop(ant, "vl_basis_type")
            box.prop(ant, "distortion")
        elif ant.noise_type == "marble_noise":
            box.prop(ant, "marble_shape")
            box.prop(ant, "marble_bias")
            box.prop(ant, "marble_sharp")
            # layout = box.layoutumn(align=True)
            layout.prop(ant, "distortion")
            layout.prop(ant, "noise_depth")
            # layout.separator()
            # layout = layout.layout(align=True)
            layout.prop(ant, "hard_noise", expand=True)
        elif ant.noise_type == "shattered_hterrain":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "distortion")
        elif ant.noise_type == "strata_hterrain":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "distortion", text="Strata")
        elif ant.noise_type == "ant_turbulence":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "amplitude")
            layout.prop(ant, "frequency")
            layout.prop(ant, "distortion")
            layout.separator()
            layout = layout.layout(align=True)
            layout.prop(ant, "hard_noise", expand=True)
        elif ant.noise_type == "vl_noise_turbulence":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "amplitude")
            layout.prop(ant, "frequency")
            layout.prop(ant, "distortion")
            layout.separator()
            layout.prop(ant, "vl_basis_type")
            # layout.separator()
            # layout = layout.layout(align=True)
            layout.prop(ant, "hard_noise", expand=True)
        elif ant.noise_type == "vl_hTerrain":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "distortion")
            # layout.separator()
            # box.prop(ant, "vl_basis_type")
        elif ant.noise_type == "distorted_heteroTerrain":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "distortion")
            # layout.separator()
            # layout.prop(ant, "vl_basis_type")
        elif ant.noise_type == "double_multiFractal":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "offset")
            layout.prop(ant, "gain")
            # layout.separator()
            # box.prop(ant, "vl_basis_type")
        elif ant.noise_type == "rocks_noise":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "distortion")
            layout.separator()
            # layout = layout.layout(align=True)
            # layout.prop(ant, "hard_noise", expand=True)
        elif ant.noise_type == "slick_rock":
            layout.prop(ant, "noise_depth")
            layout.prop(ant, "dimension")
            layout.prop(ant, "lacunarity")
            layout.prop(ant, "gain")
            layout.prop(ant, "offset")
            layout.prop(ant, "distortion")
            # layout.separator()
            # box.prop(ant, "vl_basis_type")
        elif ant.noise_type == "planet_noise":
            layout.prop(ant, "noise_depth")
            # layout.separator()
            # layout = layout.layout(align=True)
            layout.prop(ant, "hard_noise", expand=True)

        # Effects mix
        # layout = box.layoutumn(align=False)
        layout.prop(ant, "fx_type")
        if ant.fx_type != "0":
            if int(ant.fx_type) <= 12:
                layout.prop(ant, "fx_bias")

            layout.prop(ant, "fx_mix_mode")
            # layout = box.layoutumn(align=True)
            layout.prop(ant, "fx_mixfactor")

            # layout = box.layoutumn(align=True)
            layout.prop(ant, "fx_loc_x")
            layout.prop(ant, "fx_loc_y")
            layout.prop(ant, "fx_size")

            # layout = box.layoutumn(align=True)
            layout.prop(ant, "fx_depth")
            if ant.fx_depth != 0:
                layout.prop(ant, "fx_frequency")
                layout.prop(ant, "fx_amplitude")
            layout.prop(ant, "fx_turb")

            col = layout.column(align=True)
            row = col.row(align=True).split(factor=0.92, align=True)
            row.prop(ant, "fx_height")
            row.prop(ant, "fx_invert", toggle=True, text="", icon='ARROW_LEFTRIGHT')
            # layout.prop(ant, "fx_invert", toggle=True, text="Invert")
            layout.prop(ant, "fx_offset")


# Landscape Displace Settings
class AntDisplaceSettingsPanel(bpy.types.Panel):
    bl_idname = "TXA_ANTDISP_PT_layout"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "object"
    bl_label = "Landscape Displace"

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob.txaant_landscape.keys() if ob else False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = bpy.context.active_object
        ant = ob.txaant_landscape
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 1.5
        if ant.sphere_mesh:
            col.operator('mesh.txa_ant_landscape_regenerate', text="Regenerate", icon="LOOP_FORWARDS")
        else:
            col.operator('mesh.txa_ant_landscape_refresh', text="Refresh", icon="FILE_REFRESH")

        col = box.column(align=True)
        row = col.row(align=True).split(0.92, align=True)
        row.prop(ant, "height")
        row.prop(ant, "height_invert", toggle=True, text="", icon='ARROW_LEFTRIGHT')
        col.prop(ant, "height_offset")
        col.prop(ant, "maximum")
        col.prop(ant, "minimum")
        if not ant.sphere_mesh:
            col = box.column()
            col.prop(ant, "edge_falloff")
            if ant.edge_falloff != "0":
                col = box.column(align=True)
                col.prop(ant, "edge_level")
                if ant.edge_falloff in ["2", "3"]:
                    col.prop(ant, "falloff_x")
                if ant.edge_falloff in ["1", "3"]:
                    col.prop(ant, "falloff_y")

        col = box.column()
        col.prop(ant, "strata_type")
        if ant.strata_type != "0":
            col = box.column()
            col.prop(ant, "strata")
        col = box.column()
        col.prop_search(ant, "vert_group", ob, "vertex_groups")


# ------------------------------------------------------------
# Properties group
class AntLandscapePropertiesGroup(bpy.types.PropertyGroup):

    ant_terrain_name: StringProperty(
            name="Name",
            default="Landscape"
            )
    land_material: StringProperty(
            name='Material',
            default="",
            description="Terrain material"
            )
    water_material: StringProperty(
            name='Material',
            default="",
            description="Water plane material"
            )
    texture_block: StringProperty(
            name="Texture",
            default=""
            )
    at_cursor: BoolProperty(
            name="Cursor",
            default=True,
            description="Place at cursor location",
            )
    smooth_mesh: BoolProperty(
            name="Smooth",
            default=True,
            description="Shade smooth"
            )
    tri_face: BoolProperty(
            name="Triangulate",
            default=False,
            description="Triangulate faces"
            )
    sphere_mesh: BoolProperty(
            name="Sphere",
            default=False,
            description="Generate uv sphere - remove doubles when ready"
            )
    subdivision_x: IntProperty(
            name="Subdivisions X",
            default=16,
            min=4,
            max=6400,
            description="Mesh X subdivisions"
            )
    subdivision_y: IntProperty(
            default=16,
            name="Subdivisions Y",
            min=4,
            max=6400,
            description="Mesh Y subdivisions"
            )
    tex_size_x: IntProperty(
            default=128,
            name="Texture Size",
            min=16,
            max=4096,
            description="Texture Size"
            )
    tex_size_y: IntProperty(
            default=128,
            name="Texture Size",
            min=16,
            max=4096,
            description="Texture Size"
            )
    mesh_size: FloatProperty(
            default=2.0,
            name="Mesh Size",
            min=0.01,
            max=100000.0,
            description="Mesh size"
            )
    mesh_size_x: FloatProperty(
            default=2.0,
            name="Mesh Size X",
            min=0.01,
            description="Mesh x size"
            )
    mesh_size_y: FloatProperty(
            name="Mesh Size Y",
            default=2.0,
            min=0.01,
            description="Mesh y size"
            )
    random_seed: IntProperty(
            name="Random Seed",
            default=0,
            min=0,
            description="Randomize noise origin"
            )
    noise_offset_x: FloatProperty(
            name="Offset X",
            default=0.0,
            description="Noise X Offset"
            )
    noise_offset_y: FloatProperty(
            name="Offset Y",
            default=0.0,
            description="Noise Y Offset"
            )
    noise_offset_z: FloatProperty(
            name="Offset Z",
            default=0.0,
            description="Noise Z Offset"
            )
    noise_size_x: FloatProperty(
            default=1.0,
            name="Size X",
            min=0.01,
            max=1000.0,
            description="Noise x size"
            )
    noise_size_y: FloatProperty(
            name="Size Y",
            default=1.0,
            min=0.01,
            max=1000.0,
            description="Noise y size"
            )
    noise_size_z: FloatProperty(
            name="Size Z",
            default=1.0,
            min=0.01,
            max=1000.0,
            description="Noise Z size"
            )
    noise_size: FloatProperty(
            name="Noise Size",
            default=1.0,
            min=0.01,
            max=1000.0,
            description="Noise size"
            )
    noise_type: EnumProperty(
            name="Noise Type",
            default='hetero_terrain',
            description="Noise type",
            items = [
                ('multi_fractal', "Multi Fractal", "Blender: Multi Fractal algorithm", 0),
                ('ridged_multi_fractal', "Ridged MFractal", "Blender: Ridged Multi Fractal", 1),
                ('hybrid_multi_fractal', "Hybrid MFractal", "Blender: Hybrid Multi Fractal", 2),
                ('hetero_terrain', "Hetero Terrain", "Blender: Hetero Terrain", 3),
                ('fractal', "fBm Fractal", "Blender: fBm - Fractional Browninian motion", 4),
                ('turbulence_vector', "Turbulence", "Blender: Turbulence Vector", 5),
                ('variable_lacunarity', "Distorted Noise", "Blender: Distorted Noise", 6),
                ('marble_noise', "Marble", "A.N.T.: Marble Noise", 7),
                ('shattered_hterrain', "Shattered hTerrain", "A.N.T.: Shattered hTerrain", 8),
                ('strata_hterrain', "Strata hTerrain", "A.N.T: Strata hTerrain", 9),
                ('ant_turbulence', "Another Noise", "A.N.T: Turbulence variation", 10),
                ('vl_noise_turbulence', "vlNoise turbulence", "A.N.T: Real vlNoise turbulence", 11),
                ('vl_hTerrain', "vlNoise hTerrain", "A.N.T: vlNoise hTerrain", 12),
                ('distorted_heteroTerrain', "Distorted hTerrain", "A.N.T distorted hTerrain", 13),
                ('double_multiFractal', "Double MultiFractal", "A.N.T: double multiFractal", 14),
                ('rocks_noise', "Noise Rocks", "A.N.T: turbulence variation", 15),
                ('slick_rock', "Slick Rock", "A.N.T: slick rock", 16),
                ('planet_noise', "Planet Noise", "Planet Noise by: Farsthary", 17),
                ('blender_texture', "Blender Texture - Texture Nodes", "Blender texture data block", 18)]
            )
    basis_type: EnumProperty(
            name="Noise Basis",
            default=ant_noise.noise_basis_default,
            description="Noise basis algorithms",
            items = ant_noise.noise_basis
            )
    vl_basis_type: EnumProperty(
            name="vlNoise Basis",
            default=ant_noise.noise_basis_default,
            description="VLNoise basis algorithms",
            items =  ant_noise.noise_basis
            )
    distortion: FloatProperty(
            name="Distortion",
            default=1.0,
            min=0.01,
            max=100.0,
            description="Distortion amount"
            )
    hard_noise: EnumProperty(
            name="Soft Hard",
            default="0",
            description="Soft Noise, Hard noise",
            items = [
                ("0", "Soft", "Soft Noise", 0),
                ("1", "Hard", "Hard noise", 1)]
            )
    noise_depth: IntProperty(
            name="Depth",
            default=8,
            min=0,
            max=16,
            description="Noise Depth - number of frequencies in the fBm"
            )
    amplitude: FloatProperty(
            name="Amp",
            default=0.5,
            min=0.01,
            max=1.0,
            description="Amplitude"
            )
    frequency: FloatProperty(
            name="Freq",
            default=2.0,
            min=0.01,
            max=5.0,
            description="Frequency"
            )
    dimension: FloatProperty(
            name="Dimension",
            default=1.0,
            min=0.01,
            max=2.0,
            description="H - fractal dimension of the roughest areas"
            )
    lacunarity: FloatProperty(
            name="Lacunarity",
            min=0.01,
            max=6.0,
            default=2.0,
            description="Lacunarity - gap between successive frequencies"
            )
    offset: FloatProperty(
            name="Offset",
            default=1.0,
            min=0.01,
            max=6.0,
            description="Offset - raises the terrain from sea level"
            )
    gain: FloatProperty(
            name="Gain",
            default=1.0,
            min=0.01,
            max=6.0,
            description="Gain - scale factor"
            )
    marble_bias: EnumProperty(
            name="Bias",
            default="0",
            description="Marble bias",
            items = [
                ("0", "Sin", "Sin", 0),
                ("1", "Cos", "Cos", 1),
                ("2", "Tri", "Tri", 2),
                ("3", "Saw", "Saw", 3)]
            )
    marble_sharp: EnumProperty(
            name="Sharp",
            default="0",
            description="Marble sharpness",
            items = [
                ("0", "Soft", "Soft", 0),
                ("1", "Sharp", "Sharp", 1),
                ("2", "Sharper", "Sharper", 2),
                ("3", "Soft inv.", "Soft", 3),
                ("4", "Sharp inv.", "Sharp", 4),
                ("5", "Sharper inv.", "Sharper", 5)]
            )
    marble_shape: EnumProperty(
            name="Shape",
            default="0",
            description="Marble shape",
            items= [
                ("0", "Default", "Default", 0),
                ("1", "Ring", "Ring", 1),
                ("2", "Swirl", "Swirl", 2),
                ("3", "Bump", "Bump", 3),
                ("4", "Wave", "Wave", 4),
                ("5", "Z", "Z", 5),
                ("6", "Y", "Y", 6),
                ("7", "X", "X", 7)]
        )
    height: FloatProperty(
            name="Height",
            default=0.5,
            min=-10000.0,
            max=10000.0,
            description="Noise intensity scale"
            )
    height_invert: BoolProperty(
            name="Invert",
            default=False,
            description="Height invert",
            )
    height_offset: FloatProperty(
            name="Offset",
            default=0.0,
            min=-10000.0,
            max=10000.0,
            description="Height offset"
            )
    fx_mixfactor: FloatProperty(
            name="Mix Factor",
            default=0.0,
            min=-1.0,
            max=1.0,
            description="Effect mix factor: -1.0 = Noise, +1.0 = Effect"
            )
    fx_mix_mode: EnumProperty(
            name="Effect Mix",
            default="0",
            description="Effect mix mode",
            items = [
                ("0", "Mix", "Mix", 0),
                ("1", "Add", "Add", 1),
                ("2", "Sub", "Subtract", 2),
                ("3", "Mul", "Multiply", 3),
                ("4", "Abs", "Absolute", 4),
                ("5", "Scr", "Screen", 5),
                ("6", "Mod", "Modulo", 6),
                ("7", "Min", "Minimum", 7),
                ("8", "Max", "Maximum", 8)
                ]
            )
    fx_type: EnumProperty(
            name="Effect Type",
            default="0",
            description="Effect type",
            items = [
                ("0", "None", "No effect", 0),
                ("1", "Gradient", "Gradient", 1),
                ("2", "Waves", "Waves - Bumps", 2),
                ("3", "Zigzag", "Zigzag", 3),
                ("4", "Wavy", "Wavy", 4),
                ("5", "Bump", "Bump", 5),
                ("6", "Dots", "Dots", 6),
                ("7", "Rings", "Rings", 7),
                ("8", "Spiral", "Spiral", 8),
                ("9", "Square", "Square", 9),
                ("10", "Blocks", "Blocks", 10),
                ("11", "Grid", "Grid", 11),
                ("12", "Tech", "Tech", 12),
                ("13", "Crackle", "Crackle", 13),
                ("14", "Cracks", "Cracks", 14),
                ("15", "Rock", "Rock noise", 15),
                ("16", "Lunar", "Craters", 16),
                ("17", "Cosine", "Cosine", 17),
                ("18", "Spikey", "Spikey", 18),
                ("19", "Stone", "Stone", 19),
                ("20", "Flat Turb", "Flat turbulence", 20),
                ("21", "Flat Voronoi", "Flat voronoi", 21)
                ]
            )
    fx_bias: EnumProperty(
            name="Effect Bias",
            default="0",
            description="Effect bias type",
            items = [
                ("0", "Sin", "Sin", 0),
                ("1", "Cos", "Cos", 1),
                ("2", "Tri", "Tri", 2),
                ("3", "Saw", "Saw", 3),
                ("4", "None", "None", 4)]
            )
    fx_turb: FloatProperty(
            name="Distortion",
            default=0.0,
            min=0.0,
            max=1000.0,
            description="Effect turbulence distortion"
            )
    fx_depth: IntProperty(
            name="Depth",
            default=0,
            min=0,
            max=16,
            description="Effect depth - number of frequencies"
            )
    fx_amplitude: FloatProperty(
            name="Amp",
            default=0.5,
            min=0.01,
            max=1.0,
            description="Amplitude"
            )
    fx_frequency: FloatProperty(
            name="Freq",
            default=2.0,
            min=0.01,
            max=5.0,
            description="Frequency"
            )
    fx_size: FloatProperty(
            name="Effect Size",
            default=1.0,
            min=0.01,
            max=1000.0,
            description="Effect size"
            )
    fx_loc_x: FloatProperty(
            name="Offset X",
            default=0.0,
            description="Effect x offset"
            )
    fx_loc_y: FloatProperty(
            name="Offset Y",
            default=0.0,
            description="Effect y offset"
            )
    fx_height: FloatProperty(
            name="Intensity",
            default=1.0,
            min=-1000.0,
            max=1000.0,
            description="Effect intensity scale"
            )
    fx_invert: BoolProperty(
            name="Invert",
            default=False,
            description="Effect invert"
            )
    fx_offset: FloatProperty(
            name="Offset",
            default=0.0,
            min=-1000.0,
            max=1000.0,
            description="Effect height offset"
            )

    edge_falloff: EnumProperty(
            name="Falloff",
            default="3",
            description="Flatten edges",
            items = [
                ("0", "None", "None", 0),
                ("1", "Y", "Y Falloff", 1),
                ("2", "X", "X Falloff", 2),
                ("3", "X Y", "X Y Falloff", 3)]
            )
    falloff_x: FloatProperty(
            name="Falloff X",
            default=4.0,
            min=0.1,
            max=100.0,
            description="Falloff x scale"
            )
    falloff_y: FloatProperty(
            name="Falloff Y",
            default=4.0,
            min=0.1,
            max=100.0,
            description="Falloff y scale"
            )
    edge_level: FloatProperty(
            name="Edge Level",
            default=0.0,
            min=-10000.0,
            max=10000.0,
            description="Edge level, sealevel offset"
            )
    maximum: FloatProperty(
            name="Maximum",
            default=1.0,
            min=-10000.0,
            max=10000.0,
            description="Maximum, flattens terrain at plateau level"
            )
    minimum: FloatProperty(
            name="Minimum",
            default=-1.0,
            min=-10000.0,
            max=10000.0,
            description="Minimum, flattens terrain at seabed level"
            )
    vert_group: StringProperty(
            name="Vertex Group",
            default=""
            )
    strata: FloatProperty(
            name="Amount",
            default=5.0,
            min=0.01,
            max=1000.0,
            description="Strata layers / terraces"
            )
    strata_type: EnumProperty(
            name="Strata",
            default="0",
            description="Strata types",
            items = [
                ("0", "None", "No strata", 0),
                ("1", "Smooth", "Smooth transitions", 1),
                ("2", "Sharp Sub", "Sharp subtract transitions", 2),
                ("3", "Sharp Add", "Sharp add transitions", 3),
                ("4", "Quantize", "Quantize", 4),
                ("5", "Quantize Mix", "Quantize mixed", 5)]
            )
    water_plane: BoolProperty(
            name="Water Plane",
            default=False,
            description="Add water plane"
            )
    water_level: FloatProperty(
            name="Level",
            default=0.1,
            min=-10000.0,
            max=10000.0,
            description="Water level"
            )
    remove_double: BoolProperty(
            name="Remove Doubles",
            default=False,
            description="Remove doubles"
            )
    refresh: BoolProperty(
            name="Refresh",
            default=False,
            description="Refresh"
            )
    auto_refresh: BoolProperty(
            name="Auto",
            default=True,
            description="Automatic refresh"
            )
    mesh_size_z: FloatProperty(
            name="Mesh Height",
            default=1.0,
            min=0.01,
            description="Mesh height"
            )
            
def GetEroderMatItems(self, context):
    # print("OS Type: ", platform.system())
    if platform.system() == 'Windows':
        # print("Using Windows")
        directory = os.path.join(os.path.dirname(__file__), "materials")
    else:
        directory = os.path.join(os.path.dirname(__file__), "materials")
    # print("Directory: ", directory)
    if directory and os.path.exists(directory):
        # Scan the directory for json files
        items = [("NormalOnly","NormalOnly","NormalOnly")]
        i = 0
        for fn in os.listdir(directory):
            if fn.lower().endswith(".json"):
                i +=1
                MatName = fn[:-5]
                if MatName != "NormalOnly" and MatName != "Water":
                    items.append((MatName, MatName, MatName))
    else:
        items = [("NormalOnly","NormalOnly","NormalOnly")]
    # print("Items: ", items)    
    return items

# ------------------------------------------------------------
# Register:

classes = (
    AntLandscapeAddPanel,
    # AntLandscapeToolsPanel,
    AntMainSettingsPanel,
    AntNoiseSettingsPanel,
    AntDisplaceSettingsPanel,
    AntLandscapePropertiesGroup,
    add_mesh_ant_landscape.AntAddLandscape,
    mesh_ant_displace.AntMeshDisplace,
    ant_functions.AntLandscapeRefresh,
    ant_functions.AntLandscapeRegenerate,
    ant_functions.AntVgSlopeMap,
    ant_functions.Eroder,
    ant_functions.MESH_OT_ImageSave,
    ant_functions.ANTMAIN_PT_eroder,
    ant_functions.EroderProps,
    MESH_MT_ant_presets,
    MESH_MT_main_ant_presets,
    AddPresetTxa_Ant,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_landscape)
    bpy.types.Object.txaant_landscape = PointerProperty(type=AntLandscapePropertiesGroup, name="ANT_Landscape", description="Landscape properties")
    bpy.types.Scene.txaEroderProps = bpy.props.PointerProperty(type=EroderProps)
    bpy.types.Scene.EroderMats = EnumProperty(
            name="",
            description="Preferred Material",
            items=GetEroderMatItems,
            )
    bpy.types.VIEW3D_MT_paint_weight.append(menu_func_eroder)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func_landscape)
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_func_eroder)
    del bpy.types.Scene.txaEroderProps
    del bpy.types.Scene.EroderMats


if __name__ == "__main__":
    register()
