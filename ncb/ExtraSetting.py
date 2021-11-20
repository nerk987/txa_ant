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
import os
from . import NodeGroupComputer

def txaChangeImageName(imageName):
    # print("TXA JSon prefix, name: ", imageName[:2], bpy.context.object.name + imageName[5:])
    if imageName[:3] == "ant":
        # print("replacing")
        return bpy.context.object.name + imageName[5:]
    else:
        return imageName
        

def checkVersion():
    numero = bpy.app.version
    tulos = int(eval(f"{numero[0]}{numero[1]}{numero[2]}"))
    return tulos

def writeGroupExtraSettings(node):

    settings = []

    if(len(node.inputs) > 0):

        for index, input in enumerate(node.inputs):
            # print('input', input)
            if input.type == 'VALUE':
                settings.append([11, index, node.inputs[index].default_value, node.node_tree.inputs[index].min_value, node.node_tree.inputs[index].max_value])

            elif input.type == 'RGBA':
                settings.append([10, index,
                                 [node.inputs[index].default_value[0],
                                  node.inputs[index].default_value[1],
                                  node.inputs[index].default_value[2],
                                  node.inputs[index].default_value[3]]])

            elif input.type == 'VECTOR':
                settings.append([10, index,
                                 [node.inputs[index].default_value[0],
                                  node.inputs[index].default_value[1],
                                  node.inputs[index].default_value[2]]])

    else:

        settings.append([-1,-1,-1])

    return settings

def writeExtraSettings(dict, node, type, nimi, main_mode):

    settings = []
    hidden_outputs = []
    script = []
    color_ramp_data = []



    #  INPUT


    if node.type == 'AMBIENT_OCCLUSION':

        settings.append([0, 'samples', node.samples])
        settings.append([0, 'inside', node.inside])
        settings.append([0, 'only_local', node.only_local])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])
        settings.append([1, 'Distance', node.inputs['Distance'].default_value])

    elif node.type == 'ATTRIBUTE':

        settings.append([0, 'attribute_name', node.attribute_name])

    elif node.type == 'BEVEL':

        settings.append([0, 'samples', node.samples])
        settings.append([1, 'Radius', node.inputs['Radius'].default_value])

    elif node.type == 'FRESNEL':

        settings.append([1, 'IOR', node.inputs['IOR'].default_value])

    elif node.type == 'LAYER_WEIGHT':

        settings.append([1, 'Blend', node.inputs['Blend'].default_value])

    elif node.type == 'RGB':

        settings.append([2, 'Color',
                         [node.outputs['Color'].default_value[0],
                          node.outputs['Color'].default_value[1],
                          node.outputs['Color'].default_value[2],
                          node.outputs['Color'].default_value[3]]])

    elif node.type == 'TANGENT':

        settings.append([0, 'direction_type', node.direction_type])
        settings.append([0, 'axis', node.axis])

    elif node.type == 'TEX_COORD':

        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([0, 'from_instancer', node.from_instancer])

    elif node.type == 'UVMAP':

        settings.append([0, 'uv_map', node.uv_map])
        settings.append([0, 'from_instancer', node.from_instancer])

    elif node.type == 'VALUE':

        settings.append([2, 'Value', node.outputs['Value'].default_value])

    elif node.type == 'WIREFRAME':

        settings.append([0, 'pixel_size', node.pizel_size])
        settings.append([1, 'Size', node.inputs['Size'].default_value])



    # OUTPUT



    elif node.type == 'OUTPUT_LIGHT':

        settings.append([0, 'target', node.target])

    elif node.type == 'OUTPUT_MATERIAL':

        settings.append([0, 'target', node.target])


    # SHADER

    elif node.type == 'BSDF_ANISOTROPIC':

        settings.append([0, 'distribution', node.distribution])

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'Anisotropy', node.inputs['Anisotropy'].default_value])
        settings.append([1, 'Rotation', node.inputs['Rotation'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_DIFFUSE':

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'EMISSION':

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_GLASS':

        settings.append([0, 'distribution', node.distribution])

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'IOR', node.inputs['IOR'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_GLOSSY':

        settings.append([0, 'distribution', node.distribution])

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_HAIR':

        settings.append([0, 'component', node.component])

        settings.append([1, 'RoughnessU', node.inputs['RoughnessU'].default_value])
        settings.append([1, 'RoughnessV', node.inputs['RoughnessV'].default_value])
        settings.append([1, 'Offset', node.inputs['Offset'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_HAIR':

        settings.append([0, 'component', node.component])

        settings.append([1, 'RoughnessU', node.inputs['RoughnessU'].default_value])
        settings.append([1, 'RoughnessV', node.inputs['RoughnessV'].default_value])
        settings.append([1, 'Offset', node.inputs['Offset'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'MIX_SHADER':

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

    elif node.type == 'BSDF_PRINCIPLED':

        settings.append([0, 'distribution', node.distribution])
        settings.append([0, 'subsurface_method', node.subsurface_method])

        settings.append([1, 'Subsurface', node.inputs['Subsurface'].default_value])
        settings.append([1, 'Metallic', node.inputs['Metallic'].default_value])
        settings.append([1, 'Specular', node.inputs['Specular'].default_value])
        settings.append([1, 'Specular Tint', node.inputs['Specular Tint'].default_value])
        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'Anisotropic', node.inputs['Anisotropic'].default_value])
        settings.append([1, 'Anisotropic Rotation', node.inputs['Anisotropic Rotation'].default_value])
        settings.append([1, 'Sheen', node.inputs['Sheen'].default_value])
        settings.append([1, 'Sheen Tint', node.inputs['Sheen Tint'].default_value])
        settings.append([1, 'Clearcoat', node.inputs['Clearcoat'].default_value])
        settings.append([1, 'Clearcoat Roughness', node.inputs['Clearcoat Roughness'].default_value])
        settings.append([1, 'IOR', node.inputs['IOR'].default_value])
        settings.append([1, 'Transmission', node.inputs['Transmission'].default_value])
        settings.append([1, 'Transmission Roughness', node.inputs['Transmission Roughness'].default_value])

        settings.append([1, 'Base Color',
                         [node.inputs['Base Color'].default_value[0],
                          node.inputs['Base Color'].default_value[1],
                          node.inputs['Base Color'].default_value[2],
                          node.inputs['Base Color'].default_value[3]]])

        settings.append([1, 'Subsurface Color',
                         [node.inputs['Subsurface Color'].default_value[0],
                          node.inputs['Subsurface Color'].default_value[1],
                          node.inputs['Subsurface Color'].default_value[2],
                          node.inputs['Subsurface Color'].default_value[3]]])

        settings.append([1, 'Subsurface Radius',
                         [node.inputs['Subsurface Radius'].default_value[0],
                          node.inputs['Subsurface Radius'].default_value[1],
                          node.inputs['Subsurface Radius'].default_value[2]]])

    elif node.type == 'BSDF_HAIR_PRINCINPLED':

        settings.append([0, 'distribution', node.distribution])

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'Radial Roughness', node.inputs['Radial Roughness'].default_value])
        settings.append([1, 'Coat', node.inputs['Coat'].default_value])
        settings.append([1, 'IOR', node.inputs['IOR'].default_value])
        settings.append([1, 'Offset', node.inputs['Offset'].default_value])
        settings.append([1, 'Random Roughness', node.inputs['Random Roughness'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'PRINCIPLED_VOLUME':

        settings.append([1, 'Density', node.inputs['Density'].default_value])
        settings.append([1, 'Anisotropy', node.inputs['Anisotropy'].default_value])
        settings.append([1, 'Emission Strength', node.inputs['Emission Strength'].default_value])
        settings.append([1, 'Blackbody Intensity', node.inputs['Blackbody Intensity'].default_value])
        settings.append([1, 'Temperature', node.inputs['Temperature'].default_value])
        settings.append([1, 'Temperature Attribute', node.inputs['Temperature Attribute'].default_value])
        settings.append([1, 'Color Attribute', node.inputs['Color Attribute'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

        settings.append([1, 'Emission Color',
                         [node.inputs['Emission Color'].default_value[0],
                          node.inputs['Emission Color'].default_value[1],
                          node.inputs['Emission Color'].default_value[2],
                          node.inputs['Emission Color'].default_value[3]]])

        settings.append([1, 'Blackbody Tint',
                         [node.inputs['Blackbody Tint'].default_value[0],
                          node.inputs['Blackbody Tint'].default_value[1],
                          node.inputs['Blackbody Tint'].default_value[2],
                          node.inputs['Blackbody Tint'].default_value[3]]])

    elif node.type == 'BSDF_REFRACTION':

        settings.append([0, 'distribution', node.distribution])

        settings.append([1, 'Roughness', node.inputs['Roughness'].default_value])
        settings.append([1, 'IOR', node.inputs['IOR'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'SUBSURFACE_SCATTERING':

        settings.append([0, 'falloff', node.falloff])

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Texture Blur', node.inputs['Texture Blur'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

        settings.append([1, 'Radius',
                         [node.inputs['Radius'].default_value[0],
                          node.inputs['Radius'].default_value[1],
                          node.inputs['Radius'].default_value[2]]])

    elif node.type == 'BSDF_TOON':

        settings.append([0, 'component', node.component])

        settings.append([1, 'Size', node.inputs['Size'].default_value])
        settings.append([1, 'Smooth', node.inputs['Smooth'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_TRANSLUCENT':

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_TRANSPARENT':

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'BSDF_VELVET':

        settings.append([1, 'Sigma', node.inputs['Sigma'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'VOLUME_ABSORPTION':

        settings.append([1, 'Density', node.inputs['Density'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'VOLUME_SCATTER':

        settings.append([1, 'Density', node.inputs['Density'].default_value])
        settings.append([1, 'Anisotropy', node.inputs['Anisotropy'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])




    # TEXTURE

    elif node.type == 'TEX_BRICK':

        settings.append([0, 'offset', node.offset])
        settings.append([0, 'offset_frequency', node.offset_frequency])
        settings.append([0, 'squash', node.squash])
        settings.append([0, 'squash_frequency', node.squash_frequency])

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Mortar Size', node.inputs['Mortar Size'].default_value])
        settings.append([1, 'Mortar Smooth', node.inputs['Mortar Smooth'].default_value])
        settings.append([1, 'Bias', node.inputs['Bias'].default_value])
        settings.append([1, 'Brick Width', node.inputs['Brick Width'].default_value])
        settings.append([1, 'Row Height', node.inputs['Row Height'].default_value])

        settings.append([1, 'Color1',
                         [node.inputs['Color1'].default_value[0],
                          node.inputs['Color1'].default_value[1],
                          node.inputs['Color1'].default_value[2],
                          node.inputs['Color1'].default_value[3]]])

        settings.append([1, 'Color2',
                         [node.inputs['Color2'].default_value[0],
                          node.inputs['Color2'].default_value[1],
                          node.inputs['Color2'].default_value[2],
                          node.inputs['Color2'].default_value[3]]])

        settings.append([1, 'Mortar',
                         [node.inputs['Mortar'].default_value[0],
                          node.inputs['Mortar'].default_value[1],
                          node.inputs['Mortar'].default_value[2],
                          node.inputs['Mortar'].default_value[3]]])

    elif node.type == 'TEX_CHECKER':

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])

        settings.append([1, 'Color1',
                         [node.inputs['Color1'].default_value[0],
                          node.inputs['Color1'].default_value[1],
                          node.inputs['Color1'].default_value[2],
                          node.inputs['Color1'].default_value[3]]])

        settings.append([1, 'Color2',
                         [node.inputs['Color2'].default_value[0],
                          node.inputs['Color2'].default_value[1],
                          node.inputs['Color2'].default_value[2],
                          node.inputs['Color2'].default_value[3]]])

    elif node.type == 'TEX_ENVIRONMENT':

        if(node.image == None):
            filepath = ''
        else:
            filepath = node.image.filepath
            settings.append([5, 'source', node.image.source])
            settings.append([14, 'image', node.image.name])

        settings.append([4, 'filepath', filepath])
        if(node.image != None):
            settings.append([12, 'name', node.image.colorspace_settings.name])
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'projection', node.projection])


    elif node.type == 'TEX_GRADIENT':

        settings.append([0, 'gradient_type', node.gradient_type])

    elif node.type == 'TEX_IES':

        settings.append([0, 'mode', node.mode])
        settings.append([0, 'ies', node.ies])
        settings.append([0, 'filepath', node.filepath])

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])

    elif node.type == 'TEX_IMAGE':

        if(node.image == None):
            filepath = ''
        else:
            filepath = node.image.filepath
            settings.append([5, 'source', node.image.source])
            settings.append([14, 'image', node.image.name])

        settings.append([4, 'filepath', filepath])
        if(node.image != None):
            settings.append([12, 'name', node.image.colorspace_settings.name])
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'projection', node.projection])
        settings.append([0, 'extension', node.extension])


        #TODO
        pass

    elif node.type == 'TEX_MAGIC':

        settings.append([0, 'turbulence_depth', node.turbulence_depth])

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Distortion', node.inputs['Distortion'].default_value])

    elif node.type == 'TEX_MUSGRAVE':

        settings.append([0, 'musgrave_type', node.musgrave_type])

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Detail', node.inputs['Detail'].default_value])
        settings.append([1, 'Dimension', node.inputs['Dimension'].default_value])
        settings.append([1, 'Lacunarity', node.inputs['Lacunarity'].default_value])
        settings.append([1, 'Offset', node.inputs['Offset'].default_value])
        settings.append([1, 'Gain', node.inputs['Gain'].default_value])

    elif node.type == 'TEX_NOISE':

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Detail', node.inputs['Detail'].default_value])
        settings.append([1, 'Distortion', node.inputs['Distortion'].default_value])

    elif node.type == 'TEX_POINTDENSITY':

        settings.append([0, 'point_source', node.point_source])
        #settings.append([0, 'object', node.object.name])  TODO
        settings.append([0, 'space', node.space])
        settings.append([0, 'radius', node.radius])
        settings.append([0, 'interpolation', node.interpolation])
        settings.append([0, 'resolution', node.resolution])
        settings.append([0, 'particle_color_source', node.particle_color_source])

    elif node.type == 'TEX_SKY':

        settings.append([0, 'sky_type', node.sky_type])
        settings.append([0, 'sun_direction', node.sun_direction])
        settings.append([0, 'grounf_albedo', node.ground_albedo])
        settings.append([0, 'turbidity', node.turbidity])

    elif node.type == 'TEX_VORONOI':

        version = checkVersion()
        if version >= 281:


            settings.append([0, 'distance', node.distance])
            settings.append([0, 'feature', node.feature])
            settings.append([0, 'voronoi_dimensions', node.voronoi_dimensions])

            settings.append([1, 'Scale', node.inputs['Scale'].default_value])
            settings.append([1, 'Exponent', node.inputs['Exponent'].default_value])
            settings.append([1, 'Randomness', node.inputs['Randomness'].default_value])
            settings.append([1, 'W', node.inputs['W'].default_value])
            settings.append([1, 'Scale', node.inputs['Scale'].default_value])

            settings.append([1, 'Vector',
                [node.inputs['Vector'].default_value[0],
                node.inputs['Vector'].default_value[1],
                node.inputs['Vector'].default_value[2]]])
        else:

            settings.append([0, 'coloring', node.coloring])
            settings.append([0, 'distance', node.distance])
            settings.append([0, 'feature', node.feature])

            settings.append([1, 'Scale', node.inputs['Scale'].default_value])

    elif node.type == 'TEX_WAVE':

        settings.append([0, 'wave_type', node.wave_type])
        settings.append([0, 'wave_profile', node.wave_profile])

        settings.append([1, 'Scale', node.inputs['Scale'].default_value])
        settings.append([1, 'Distortion', node.inputs['Distortion'].default_value])
        settings.append([1, 'Detail', node.inputs['Detail'].default_value])
        settings.append([1, 'Detail Scale', node.inputs['Detail Scale'].default_value])




    # COLOR

    elif node.type == 'BRIGHTCONTRAST':


        settings.append([1, 'Bright', node.inputs['Bright'].default_value])
        settings.append([1, 'Contrast', node.inputs['Contrast'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'GAMMA':

        settings.append([1, 'Gamma', node.inputs['Gamma'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'HUE_SAT':

        settings.append([1, 'Hue', node.inputs['Hue'].default_value])
        settings.append([1, 'Saturation', node.inputs['Saturation'].default_value])
        settings.append([1, 'Value', node.inputs['Value'].default_value])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'INVERT':

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'LIGHT_FALLOFF':

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])
        settings.append([1, 'Smooth', node.inputs['Smooth'].default_value])

    elif node.type == 'MIX_RGB':

        settings.append([0, 'blend_type', node.blend_type])
        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Color1',
                         [node.inputs['Color1'].default_value[0],
                          node.inputs['Color1'].default_value[1],
                          node.inputs['Color1'].default_value[2],
                          node.inputs['Color1'].default_value[3]]])

        settings.append([1, 'Color2',
                         [node.inputs['Color2'].default_value[0],
                          node.inputs['Color2'].default_value[1],
                          node.inputs['Color2'].default_value[2],
                          node.inputs['Color2'].default_value[3]]])

    elif node.type == 'CURVE_VEC':

        settings.append([1, 'Vector',
                     [node.inputs['Vector'].default_value[0],
                      node.inputs['Vector'].default_value[1],
                      node.inputs['Vector'].default_value[2]]])

        curve_0 = []
        curve_1 = []
        curve_2 = []

        for point in node.mapping.curves[0].points:
            curve_0.append([point.location[0], point.location[1]])

        for point in node.mapping.curves[1].points:
            curve_1.append([point.location[0], point.location[1]])

        for point in node.mapping.curves[2].points:
            curve_2.append([point.location[0], point.location[1]])


        settings.append([9, 0, curve_0])
        settings.append([9, 1, curve_1])
        settings.append([9, 2, curve_2])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

    elif node.type == 'CURVE_RGB':

        curve_0 = []
        curve_1 = []
        curve_2 = []
        curve_3 = []

        for point in node.mapping.curves[0].points:
            curve_0.append([point.location[0], point.location[1]])

        for point in node.mapping.curves[1].points:
            curve_1.append([point.location[0], point.location[1]])

        for point in node.mapping.curves[2].points:
            curve_2.append([point.location[0], point.location[1]])

        for point in node.mapping.curves[3].points:
            curve_3.append([point.location[0], point.location[1]])

        settings.append([9, 0, curve_0])
        settings.append([9, 1, curve_1])
        settings.append([9, 2, curve_2])
        settings.append([9, 3, curve_3])



        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])


    # VECTOR



    elif node.type == 'BUMP':

        settings.append([0, 'invert', node.invert])

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])
        settings.append([1, 'Distance', node.inputs['Distance'].default_value])

    elif node.type == 'DISPLACEMENT':

        settings.append([0, 'space', node.space])

        settings.append([1, 'Height', node.inputs['Height'].default_value])
        settings.append([1, 'Midlevel', node.inputs['Midlevel'].default_value])
        settings.append([1, 'Scale', node.inputs['Scale'].default_value])

    elif node.type == 'MAPPING':
        version = checkVersion()
        if version >= 281:
            settings.append([0, 'vector_type', node.vector_type])

            settings.append([1, 'Vector',
                    [node.inputs['Vector'].default_value[0],
                    node.inputs['Vector'].default_value[1],
                    node.inputs['Vector'].default_value[2]]])

            settings.append([1, 'Location',
                [node.inputs['Location'].default_value[0],
                node.inputs['Location'].default_value[1],
                node.inputs['Location'].default_value[2]]])
            
            settings.append([1, 'Rotation',
                [node.inputs['Rotation'].default_value[0],
                node.inputs['Rotation'].default_value[1],
                node.inputs['Rotation'].default_value[2]]])

            settings.append([1, 'Scale',
                [node.inputs['Scale'].default_value[0],
                node.inputs['Scale'].default_value[1],
                node.inputs['Scale'].default_value[2]]])

        else:
            settings.append([0, 'vector_type', node.vector_type])

            settings.append([0, 'translation', [node.translation[0], node.translation[1], node.translation[2]]])
            settings.append([0, 'rotation', [node.rotation[0], node.rotation[1], node.rotation[2]]])
            settings.append([0, 'scale', [node.scale[0], node.scale[1], node.scale[2]]])

            settings.append([0, 'use_min', node.use_min])
            settings.append([0, 'use_max', node.use_max])

            settings.append([0, 'min', [node.min[0], node.min[1], node.min[2]]])
            settings.append([0, 'max', [node.max[0], node.max[1], node.max[2]]])

    elif node.type == 'NORMAL':

        settings.append([1, 'Normal',
                         [node.inputs['Normal'].default_value[0],
                          node.inputs['Normal'].default_value[1],
                          node.inputs['Normal'].default_value[2]]])

        settings.append([2, 'Normal', [node.outputs['Normal'].default_value[0],
                                       node.outputs['Normal'].default_value[1],
                                       node.outputs['Normal'].default_value[2]]])

    elif node.type == 'NORMAL_MAP':

        settings.append([0, 'space', node.space])
        settings.append([0, 'uv_map', node.uv_map])

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'CURVE_VEC':

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        #TODO

    elif node.type == 'VECTOR_DISPLACEMENT':

        settings.append([0, 'space', node.space])

        settings.append([1, 'Midlevel', node.inputs['Midlevel'].default_value])
        settings.append([1, 'Scale', node.inputs['Scale'].default_value])

    elif node.type == 'VECT_TRANSFORM':

        settings.append([0, 'vector_type', node.vector_type])
        settings.append([0, 'convert_from', node.convert_from])
        settings.append([0, 'convert_to', node.convert_to])

        settings.append([1, 'Vector',
                         [node.inputs['Vector'].default_value[0],
                          node.inputs['Vector'].default_value[1],
                          node.inputs['Vector'].default_value[2]]])




    # CONVERTER




    elif node.type == 'BLACKBODY':

        settings.append([1, 'Temperature', node.inputs['Temperature'].default_value])

    elif node.type == 'VALTORGB':

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()

        for data in ramp_data:
            color_ramp_data.append([data.position,[data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])



    elif node.type == 'COMBHSV':

        settings.append([1, 'H', node.inputs['H'].default_value])
        settings.append([1, 'S', node.inputs['S'].default_value])
        settings.append([1, 'V', node.inputs['V'].default_value])

    elif node.type == 'COMBRGB':

        settings.append([1, 'B', node.inputs['B'].default_value])
        settings.append([1, 'G', node.inputs['G'].default_value])
        settings.append([1, 'R', node.inputs['R'].default_value])

    elif node.type == 'MAP_RANGE':

        settings.append([0, 'clamp', node.clamp])

        settings.append([1, 'Value', node.inputs['Value'].default_value])
        settings.append([1, 'To Max', node.inputs['To Max'].default_value])
        settings.append([1, 'To Min', node.inputs['To Min'].default_value])
        settings.append([1, 'From Max', node.inputs['From Max'].default_value])
        settings.append([1, 'From Min', node.inputs['From Min'].default_value])

    elif node.type == 'COMBXYZ':

        settings.append([1, 'X', node.inputs['X'].default_value])
        settings.append([1, 'Y', node.inputs['Y'].default_value])
        settings.append([1, 'Z', node.inputs['Z'].default_value])

    elif node.type == 'MATH':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([10, 0, node.inputs[0].default_value])
        settings.append([10, 1, node.inputs[1].default_value])

        # TODO need some work because there is no value1 and value2, only value

    elif node.type == 'RGBTOBW':

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'SEPHSV':

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'SEPRGB':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SEPXYZ':

        settings.append([1, 'Vector',
                         [node.inputs['Vector'].default_value[0],
                          node.inputs['Vector'].default_value[1],
                          node.inputs['Vector'].default_value[2]]])

    elif node.type == 'VECT_MATH':

        settings.append([0, 'operation', node.operation])

        settings.append([10, 0,
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2]]])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2]]])

    elif node.type == 'TEX_WHITE_NOISE':

        settings.append([0, 'noise_dimensions', node.noise_dimensions])

        settings.append([1, 'Vector',
                        [node.inputs['Vector'].default_value[0],
                        node.inputs['Vector'].default_value[1],
                        node.inputs['Vector'].default_value[2]]])

        settings.append([1, 'W', node.inputs['W'].default_value])

    elif node.type == 'WAVELENGTH':

        settings.append([1, 'Wavelength', node.inputs['Wavelength'].default_value])

    elif node.type == 'SCRIPT':

        settings.append([0, 'mode', node.mode])
        if (node.mode == 'EXTERNAL'):
            settings.append([0, 'filepath', node.filepath])
        elif (node.mode == 'INTERNAL'):

            if node.script != '':
                for line in node.script.lines:
                    script.append(line.body)

            settings.append(['script',node.script.name, script])
    # WORLD NODES

    elif node.type == 'BACKGROUND':

        settings.append([1, 'Strength', node.inputs['Strength'].default_value])
        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])



    else:
        settings.append([-1,-1,-1]) #  -1 Means that it dosen't have any extra settings


    if(len(node.outputs) > 0):
        for output in node.outputs:
            if output.hide == True:
                hidden_outputs.append([output.name])

    if main_mode == 'SUB_TREE':

        dict['node'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': type,
            'parent': nimi,
            'hidden_outputs': hidden_outputs,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

    elif main_mode == 'MAIN_TREE':

        dict['nodes'].append({
            'node': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': "",
            'parent': nimi,
            'hidden_outputs': hidden_outputs,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

    return dict

def readExtraSettings(extra_settings, node):
    for setting in extra_settings:
        # print("ExtraSetting", setting)
        if setting[0] == 0:
            setattr(node, setting[1], setting[2])
        elif setting[0] == 1:
            node.inputs[setting[1]].default_value = setting[2]
        elif setting[0] == 2:
            node.outputs[setting[1]].default_value = setting[2]

        # Image loading for image texture node

        elif setting[0] == 4:
            if(setting[2] != '' and node.image == None):

                use_this_path = ''
                for image in bpy.data.images:
                    if(image.filepath == setting[2]):
                        use_this_path = image
                        break
                if(use_this_path == ''):
                    if(os.path.isfile(setting[2])):
                        node.image = bpy.data.images.load(setting[2])
                else:
                    node.image = use_this_path


        elif setting[0] == 14:
            if(setting[2] != ''):
                for image in bpy.data.images:
                    if image.name == txaChangeImageName(setting[2]):
                        node.image = image
        # COLOR RAMP


        elif setting[0] == 7:
            setattr(node.color_ramp, setting[1], setting[2])

        elif setting[0] == 8:
            data = setting[2]
            if(len(data) > 2):
                while(len(node.color_ramp.elements) < len(data)):
                    node.color_ramp.elements.new(0)

            for index, element in enumerate(setting[2]):
                node.color_ramp.elements[index].position = element[0]
                node.color_ramp.elements[index].color = element[1]

        # CURVE NODE

        elif setting[0] == 9:
            data = setting[2]
            curve = node.mapping.curves[setting[1]]

            if (len(data) > 2):
                while (len(curve.points) < len(data)):
                    curve.points.new(0, 0)
            elif (len(data) < 2):
                while (len(curve.points) > len(data)):
                    curve.points.remove(curve.points[0])

            for index, loc in enumerate(setting[2]):
                curve.points[index].location = loc

        # Image1 ja Image2 kasittely taalla // 10

        elif setting[0] == 10:
            node.inputs[setting[1]].default_value = setting[2]

        # Group Node

        elif setting[0] == 11:
            node.inputs[setting[1]].default_value = setting[2]
            node.node_tree.inputs[setting[1]].min_value = setting[3]
            node.node_tree.inputs[setting[1]].max_value = setting[4]

        elif setting[0] == 12:
            if node.image != None:
                node.image.colorspace_settings.name = setting[2]

        elif setting[0] == 'script':
            textFile = bpy.data.texts.new(setting[1])

            for line in setting[2]:
                textFile.write(line + '\n')

            node.script = textFile
