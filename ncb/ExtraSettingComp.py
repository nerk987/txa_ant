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
import os
from . import NodeGroupComputer


def writeExtraSettings(dict, node, type, nimi, main_mode):

    settings = []
    #  INPUT


    if node.type == 'BOKEHIMAGE':

        settings.append([0, 'flaps', node.flaps])
        settings.append([0, 'angle', node.angle])
        settings.append([0, 'rounding', node.rounding])
        settings.append([0, 'catadioptric', node.catadioptric])
        settings.append([0, 'shift', node.shift])

    elif node.type == 'IMAGE':

        if (node.image == None):
            filepath = ''
        else:
            filepath = node.image.filepath
            settings.append([5, 'source', node.image.source])

        settings.append([4, 'filepath', filepath])

    elif node.type == 'MASK':

        settings.append([0, 'use_feather', node.use_feather])
        settings.append([0, 'size_source', node.size_source])
        settings.append([0, 'use_motion_blur', node.use_motion_blur])

    elif node.type == 'MOVIECLIP':

        if (node.clip == None):
            filepath = ''
        else:
            filepath = node.clip.filepath
            settings.append([5, 'source', node.clip.source])

        settings.append([3, 'filepath', filepath])

    elif node.type == 'R_LAYERS':

        settings.append([-1, -1, -1])

    elif node.type == 'RGB':

        #settings.append([-1, -1, -1])
        settings.append([2, 'RGBA', [node.outputs['RGBA'].default_value[0],
                                     node.outputs['RGBA'].default_value[1],
                                     node.outputs['RGBA'].default_value[2],
                                     node.outputs['RGBA'].default_value[3]]])

    elif node.type == 'TEXTURE':

        settings.append([-1, -1, -1])

    elif node.type == 'TIME':

        settings.append([-1, -1, -1])

    elif node.type == 'TRACKPOS':

        settings.append([-1, -1, -1])

    elif node.type == 'VALUE':

        settings.append([2, 'Value', node.outputs['Value'].default_value])



    # OUTPUT



    elif node.type == 'COMPOSITE':

        settings.append([0, 'use_alpha', node.use_alpha])

        settings.append([1, 'Alpha', node.inputs['Alpha'].default_value])
        settings.append([1, 'Z', node.inputs['Z'].default_value])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'OUTPUT_FILE':

        settings.append([0, 'base_path', node.base_path])

    elif node.type == 'LEVELS':

        settings.append([0, 'channel', node.channel])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SPLITVIEWER':

        settings.append([0, 'axis', node.axis])
        settings.append([0, 'factor', node.factor])

        settings.append([10, 0,
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2],
                          node.inputs[0].default_value[3]]])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2],
                          node.inputs[1].default_value[3]]])

    elif node.type == 'VIEWER':

        settings.append([0, 'use_alpha', node.use_alpha])
        settings.append([1, 'Alpha', node.inputs['Alpha'].default_value])
        settings.append([1, 'Z', node.inputs['Z'].default_value])

        settings.append([1, 'Image',
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2],
                          node.inputs[0].default_value[3]]])


    # COLOR



    elif node.type == 'ALPHAOVER':

        settings.append([0, 'use_premultiply', node.use_premultiply])
        settings.append([0, 'premul', node.premul])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2],
                          node.inputs[1].default_value[3]]])

        settings.append([10, 2,
                         [node.inputs[2].default_value[0],
                          node.inputs[2].default_value[1],
                          node.inputs[2].default_value[2],
                          node.inputs[2].default_value[3]]])

    elif node.type == 'BRIGHTCONTRAST':


        settings.append([1, 'Bright', node.inputs['Bright'].default_value])
        settings.append([1, 'Contrast', node.inputs['Contrast'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'COLORBALANCE':

        settings.append([0, 'correction_method', node.correction_method])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([0, 'lift',
                         [node.lift[0],
                          node.lift[1],
                          node.lift[2]]])

        settings.append([0, 'gamma',
                         [node.gamma[0],
                          node.gamma[1],
                          node.gamma[2]]])

        settings.append([0, 'gain',
                         [node.gain[0],
                          node.gain[1],
                          node.gain[2]]])

    elif node.type == 'COLORCORRECTION':

        settings.append([0, 'red', node.red])
        settings.append([0, 'green', node.green])
        settings.append([0, 'blue', node.blue])

        settings.append([0, 'master_saturation', node.master_saturation])
        settings.append([0, 'master_contrast', node.master_contrast])
        settings.append([0, 'master_gamma', node.master_gamma])
        settings.append([0, 'master_gain', node.master_gain])
        settings.append([0, 'master_lift', node.master_lift])

        settings.append([0, 'highlights_saturation', node.highlights_saturation])
        settings.append([0, 'highlights_contrast', node.highlights_contrast])
        settings.append([0, 'highlights_gamma', node.highlights_gamma])
        settings.append([0, 'highlights_gain', node.highlights_gain])
        settings.append([0, 'highlights_lift', node.highlights_lift])

        settings.append([0, 'midtones_saturation', node.midtones_saturation])
        settings.append([0, 'midtones_contrast', node.midtones_contrast])
        settings.append([0, 'midtones_gamma', node.midtones_gamma])
        settings.append([0, 'midtones_gain', node.midtones_gain])
        settings.append([0, 'midtones_lift', node.midtones_lift])

        settings.append([0, 'shadows_saturation', node.shadows_saturation])
        settings.append([0, 'shadows_contrast', node.shadows_contrast])
        settings.append([0, 'shadows_gamma', node.shadows_gamma])
        settings.append([0, 'shadows_gain', node.shadows_gain])
        settings.append([0, 'shadows_lift', node.shadows_lift])

        settings.append([0, 'midtones_start', node.midtones_start])
        settings.append([0, 'midtones_end', node.midtones_end])

        settings.append([1, 'Mask', node.inputs['Mask'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'GAMMA':

        settings.append([1, 'Gamma', node.inputs['Gamma'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'HUECORRECT':

        curve_H = []
        curve_S = []
        curve_V = []

        for H_point in node.mapping.curves[0].points:
            curve_H.append([H_point.location[0], H_point.location[1]])

        for S_point in node.mapping.curves[1].points:
            curve_S.append([S_point.location[0], S_point.location[1]])

        for V_point in node.mapping.curves[2].points:
            curve_V.append([V_point.location[0], V_point.location[1]])

        settings.append([9, 0, curve_H])
        settings.append([9, 1, curve_S])
        settings.append([9, 2, curve_V])


    elif node.type == 'HUE_SAT':

        settings.append([1, 'Hue', node.inputs['Hue'].default_value])
        settings.append([1, 'Saturation', node.inputs['Saturation'].default_value])
        settings.append([1, 'Value', node.inputs['Value'].default_value])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'INVERT':

        settings.append([0, 'invert_rgb', node.invert_rgb])
        settings.append([0, 'invert_alpha', node.invert_alpha])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'MIX_RGB':

        settings.append([0, 'blend_type', node.blend_type])
        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([10, 1,
                         [node.inputs[1].default_value[0],
                          node.inputs[1].default_value[1],
                          node.inputs[1].default_value[2],
                          node.inputs[1].default_value[3]]])

        settings.append([10, 1,
                         [node.inputs[2].default_value[0],
                          node.inputs[2].default_value[1],
                          node.inputs[2].default_value[2],
                          node.inputs[2].default_value[3]]])

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

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Black Level',
                         [node.inputs['Black Level'].default_value[0],
                          node.inputs['Black Level'].default_value[1],
                          node.inputs['Black Level'].default_value[2],
                          node.inputs['Black Level'].default_value[3]]])

        settings.append([1, 'White Level',
                         [node.inputs['White Level'].default_value[0],
                          node.inputs['White Level'].default_value[1],
                          node.inputs['White Level'].default_value[2],
                          node.inputs['White Level'].default_value[3]]])

        #TODO

    elif node.type == 'TONEMAP':

        settings.append([0, 'tonemap_type', node.tonemap_type])
        settings.append([0, 'intensity', node.intensity])
        settings.append([0, 'contrast', node.contrast])
        settings.append([0, 'adaptation', node.adaptation])
        settings.append([0, 'correction', node.correction])

        settings.append([1, 'Image',
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2],
                          node.inputs[0].default_value[3]]])

    elif node.type == 'ZCOMBINE':

        settings.append([0, 'use_alpha', node.use_alpha])
        settings.append([0, 'use_antialias_z', node.use_antialias_z])
        settings.append([1, 'Z1', node.inputs[1].default_value])
        settings.append([1, 'Z2', node.inputs[3].default_value])

        settings.append([10, 0,
                         [node.inputs[0].default_value[0],
                          node.inputs[0].default_value[1],
                          node.inputs[0].default_value[2],
                          node.inputs[0].default_value[3]]])
        settings.append([10, 2,
                         [node.inputs[2].default_value[0],
                          node.inputs[2].default_value[1],
                          node.inputs[2].default_value[2],
                          node.inputs[2].default_value[3]]])



    # CONVERTER

    elif node.type == 'PREMULKEY':

        settings.append([0, 'mapping', node.mapping])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'VALTORGB':

        color_ramp_data = []

        settings.append([7, 'color_mode', node.color_ramp.color_mode])
        settings.append([7, 'interpolation', node.color_ramp.interpolation])
        settings.append([7, 'hue_interpolation', node.color_ramp.hue_interpolation])

        ramp_data = node.color_ramp.elements.values()

        for data in ramp_data:
            color_ramp_data.append([data.position, [data.color[0], data.color[1], data.color[2], data.color[3]]])

        settings.append([8, 'color_ramp', color_ramp_data])

    elif node.type == 'COMBHSVA':

        settings.append([1, 'H', node.inputs['H'].default_value])
        settings.append([1, 'S', node.inputs['S'].default_value])
        settings.append([1, 'V', node.inputs['V'].default_value])
        settings.append([1, 'A', node.inputs['A'].default_value])

    elif node.type == 'COMBRGBA':

        settings.append([1, 'B', node.inputs['B'].default_value])
        settings.append([1, 'G', node.inputs['G'].default_value])
        settings.append([1, 'R', node.inputs['R'].default_value])
        settings.append([1, 'A', node.inputs['A'].default_value])

    elif node.type == 'COMBYCCA':

        settings.append([0, 'mode', node.mode])

        settings.append([1, 'Y', node.inputs['Y'].default_value])
        settings.append([1, 'Cr', node.inputs['Cr'].default_value])
        settings.append([1, 'Cb', node.inputs['Cb'].default_value])
        settings.append([1, 'A', node.inputs['A'].default_value])

    elif node.type == 'COMBYUVA':

        settings.append([1, 'Y', node.inputs['Y'].default_value])
        settings.append([1, 'V', node.inputs['V'].default_value])
        settings.append([1, 'U', node.inputs['U'].default_value])
        settings.append([1, 'A', node.inputs['A'].default_value])

    elif node.type == 'ID_MASK':

        settings.append([0, 'index', node.index])
        settings.append([0, 'use_antialiasing', node.use_antialiasing])

        settings.append([1, 'ID value', node.inputs['ID value'].default_value])

    elif node.type == 'MATH':

        settings.append([0, 'operation', node.operation])
        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([10, 0, node.inputs[0].default_value])
        settings.append([10, 1, node.inputs[1].default_value])

        # TODO need some work because there is no value1 and value2, only value

    elif node.type == 'RGBTOBW':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SEPHSVA':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SEPRGBA':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SEPYCCA':

        settings.append([0, 'mode', node.mode])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SEPYUVA':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SETALPHA':

        settings.append([1, 'Alpha', node.inputs['Alpha'].default_value])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'VIEWSWITCH':

        settings.append([1, 'left',
                         [node.inputs['left'].default_value[0],
                          node.inputs['left'].default_value[1],
                          node.inputs['left'].default_value[2],
                          node.inputs['left'].default_value[3]]])

        settings.append([1, 'right',
                         [node.inputs['right'].default_value[0],
                          node.inputs['right'].default_value[1],
                          node.inputs['right'].default_value[2],
                          node.inputs['right'].default_value[3]]])



    # FILTER

    elif node.type == 'BILATERALBLUR':

        settings.append([0, 'iterations', node.iterations])
        settings.append([0, 'sigma_color', node.sigma_color])
        settings.append([0, 'sigma_space', node.sigma_space])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Determinator',
                         [node.inputs['Determinator'].default_value[0],
                          node.inputs['Determinator'].default_value[1],
                          node.inputs['Determinator'].default_value[2],
                          node.inputs['Determinator'].default_value[3]]])

    elif node.type == 'BLUR':

        settings.append([0, 'filter_type', node.filter_type])
        settings.append([0, 'use_variable_size', node.use_variable_size])
        settings.append([0, 'use_bokeh', node.use_bokeh])
        settings.append([0, 'use_gamma_correction', node.use_gamma_correction])
        settings.append([0, 'use_relative', node.use_relative])
        settings.append([0, 'size_x', node.size_x])
        settings.append([0, 'size_y', node.size_y])
        settings.append([0, 'use_extended_bounds', node.use_extended_bounds])

        settings.append([1, 'Size', node.inputs['Size'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'BOKEHBLUR':

        settings.append([0, 'use_variable_size', node.use_variable_size])
        settings.append([0, 'blur_max', node.blur_max])
        settings.append([0, 'use_extended_bounds', node.use_extended_bounds])

        settings.append([1, 'Size', node.inputs['Size'].default_value])
        settings.append([1, 'Bounding box', node.inputs['Bounding box'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Bokeh',
                         [node.inputs['Bokeh'].default_value[0],
                          node.inputs['Bokeh'].default_value[1],
                          node.inputs['Bokeh'].default_value[2],
                          node.inputs['Bokeh'].default_value[3]]])

    elif node.type == 'DEFOCUS':

        settings.append([0, 'bokeh', node.bokeh])
        settings.append([0, 'angle', node.angle])
        settings.append([0, 'use_gamma_correction', node.use_gamma_correction])
        settings.append([0, 'f_stop', node.f_stop])
        settings.append([0, 'blur_max', node.blur_max])
        settings.append([0, 'threshold', node.threshold])
        settings.append([0, 'use_preview', node.use_preview])
        settings.append([0, 'use_zbuffer', node.use_zbuffer])
        settings.append([0, 'z_scale', node.z_scale])

        settings.append([1, 'Z', node.inputs['Z'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'DESPECKLE':

        settings.append([0, 'threshold', node.threshold])
        settings.append([0, 'threshold_neighbor', node.threshold_neighbor])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'DILATEERODE':

        settings.append([0, 'mode', node.mode])
        settings.append([0, 'distance', node.distance])

        settings.append([1, 'Mask', node.inputs['Mask'].default_value])

    elif node.type == 'BOKEHBLUR':

        settings.append([0, 'iterations', node.iterations])
        settings.append([0, 'use_wrap', node.use_wrap])
        settings.append([0, 'center_x', node.center_x])
        settings.append([0, 'center_y', node.use_center_y])
        settings.append([0, 'distance', node.distance])
        settings.append([0, 'angle', node.angle])
        settings.append([0, 'spin', node.spin])
        settings.append([0, 'zoom', node.zoom])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'FILTER':

        settings.append([0, 'filter_type', node.filter_type])
        settings.append([1, 'Fac', node.inputs['Fac'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'GLARE':

        settings.append([0, 'glare_type', node.glare_type])
        settings.append([0, 'quality', node.quality])
        settings.append([0, 'iterations', node.iterations])
        settings.append([0, 'color_modulation', node.color_modulation])
        settings.append([0, 'mix', node.mix])
        settings.append([0, 'threshold', node.threshold])
        settings.append([0, 'streaks', node.streaks])
        settings.append([0, 'angle_offset', node.angle_offset])
        settings.append([0, 'fade', node.fade])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'INPAINT':

        settings.append([0, 'distance', node.distance])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'PIXELATE':

        settings.append([1, 'Color',
                         [node.inputs['Color'].default_value[0],
                          node.inputs['Color'].default_value[1],
                          node.inputs['Color'].default_value[2],
                          node.inputs['Color'].default_value[3]]])

    elif node.type == 'SUNBEAMS':

        settings.append([0, 'ray_length', node.ray_length])
        settings.append([0, 'source', [node.source[0], node.source[1]]])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'VECBLUR':

        settings.append([0, 'samples', node.samples])
        settings.append([0, 'factor', node.factor])
        settings.append([0, 'speed_min', node.speed_min])
        settings.append([0, 'speed_max', node.speed_max])
        settings.append([0, 'use_curved', node.use_curved])

        settings.append([1, 'Z', node.inputs['Z'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Speed',
                         [node.inputs['Speed'].default_value[0],
                          node.inputs['Speed'].default_value[1],
                          node.inputs['Speed'].default_value[2]]])



    # VECTOR

    elif node.type == 'MAP_RANGE':

        settings.append([0, 'use_clamp', node.use_clamp])

        settings.append([1, 'Value', node.inputs['Value'].default_value])
        settings.append([1, 'From Min', node.inputs['From Min'].default_value])
        settings.append([1, 'From Max', node.inputs['From Max'].default_value])
        settings.append([1, 'To Min', node.inputs['To Min'].default_value])
        settings.append([1, 'To Max', node.inputs['To Max'].default_value])

    elif node.type == 'MAP_VALUE':

        settings.append([0, 'offset', node.offset[0]])
        settings.append([0, 'size', node.size[0]])
        settings.append([0, 'use_min', node.use_min])
        settings.append([0, 'min', node.min[0]])
        settings.append([0, 'use_max', node.use_max])
        settings.append([0, 'max', node.max[0]])

        settings.append([1, 'Value', node.inputs['Value'].default_value])


    elif node.type == 'NORMALIZE':

        settings.append([1, 'Value', node.inputs['Value'].default_value])


    elif node.type == 'NORMAL':

        settings.append([1, 'Normal',
                         [node.inputs['Normal'].default_value[0],
                          node.inputs['Normal'].default_value[1],
                          node.inputs['Normal'].default_value[2]]])

        settings.append([2, 'Normal', [node.outputs['Normal'].default_value[0],
                                     node.outputs['Normal'].default_value[1],
                                     node.outputs['Normal'].default_value[2]]])


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




    # MATTE

    elif node.type == 'BOXMASK':

        settings.append([0, 'x', node.x])
        settings.append([0, 'y', node.y])
        settings.append([0, 'width', node.width])
        settings.append([0, 'height', node.height])
        settings.append([0, 'rotation', node.rotation])
        settings.append([0, 'mask_type', node.mask_type])

        settings.append([1, 'Mask', node.inputs['Mask'].default_value])
        settings.append([1, 'Value', node.inputs['Value'].default_value])

    elif node.type == 'CHANNEL_MATTE':

        settings.append([0, 'color_space', node.color_space])
        settings.append([0, 'matte_channel', node.matte_channel])
        settings.append([0, 'limit_method', node.limit_method])
        settings.append([0, 'limit_max', node.limit_max])
        settings.append([0, 'limit_min', node.limit_min])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'CHROMA_MATTE':

        settings.append([0, 'tolerance', node.tolerance])
        settings.append([0, 'threshold', node.threshold])
        settings.append([0, 'gain', node.gain])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])
        settings.append([1, 'Key Color',
                         [node.inputs['Key Color'].default_value[0],
                          node.inputs['Key Color'].default_value[1],
                          node.inputs['Key Color'].default_value[2],
                          node.inputs['Key Color'].default_value[3]]])

    elif node.type == 'COLOR_MATTE':

        settings.append([0, 'color_hue', node.color_hue])
        settings.append([0, 'color_saturation', node.color_saturation])
        settings.append([0, 'color_value', node.color_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])
        settings.append([1, 'Key Color',
                         [node.inputs['Key Color'].default_value[0],
                          node.inputs['Key Color'].default_value[1],
                          node.inputs['Key Color'].default_value[2],
                          node.inputs['Key Color'].default_value[3]]])

    elif node.type == 'COLOR_SPIL':

        settings.append([0, 'channel', node.channel])
        settings.append([0, 'limit_method', node.limit_method])
        settings.append([0, 'limit_channel', node.limit_channel])
        settings.append([0, 'ratio', node.ratio])
        settings.append([0, 'unspill', node.unspill])

        settings.append([1, 'Fac', node.inputs['Fac'].default_value])
        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'CRYPTOMATTE':

        settings.append([0, 'matte_id', node.matte_id])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Crypto 00',
                         [node.inputs['Crypto 00'].default_value[0],
                          node.inputs['Crypto 00'].default_value[1],
                          node.inputs['Crypto 00'].default_value[2],
                          node.inputs['Crypto 00'].default_value[3]]])

        settings.append([1, 'Crypto 01',
                         [node.inputs['Crypto 01'].default_value[0],
                          node.inputs['Crypto 01'].default_value[1],
                          node.inputs['Crypto 01'].default_value[2],
                          node.inputs['Crypto 01'].default_value[3]]])

        settings.append([1, 'Crypto 02',
                         [node.inputs['Crypto 02'].default_value[0],
                          node.inputs['Crypto 02'].default_value[1],
                          node.inputs['Crypto 02'].default_value[2],
                          node.inputs['Crypto 02'].default_value[3]]])

    elif node.type == 'DIFF_MATTE':

        settings.append([0, 'tolerance', node.tolerance])
        settings.append([0, 'falloff', node.falloff])

        settings.append([1, 'Image 1',
                         [node.inputs['Image 1'].default_value[0],
                          node.inputs['Image 1'].default_value[1],
                          node.inputs['Image 1'].default_value[2],
                          node.inputs['Image 1'].default_value[3]]])

        settings.append([1, 'Image 2',
                         [node.inputs['Image 2'].default_value[0],
                          node.inputs['Image 2'].default_value[1],
                          node.inputs['Image 2'].default_value[2],
                          node.inputs['Image 2'].default_value[3]]])

    elif node.type == 'DIFF_MATTE':

        settings.append([0, 'tolerance', node.tolerance])
        settings.append([0, 'falloff', node.falloff])
        settings.append([0, 'channel', node.channel])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Key Color',
                         [node.inputs['Key Color'].default_value[0],
                          node.inputs['Key Color'].default_value[1],
                          node.inputs['Key Color'].default_value[2],
                          node.inputs['Key Color'].default_value[3]]])

    elif node.type == 'DOUBLEEDGEMASK':

        settings.append([0, 'inner_mode', node.inner_mode])
        settings.append([0, 'edge_mode', node.edge_mode])

        settings.append([1, 'Inner Mask', node.inputs['Inner Mask'].default_value])
        settings.append([1, 'Outer Mask', node.inputs['Outer Mask'].default_value])

    elif node.type == 'ELLIPSEMASK':

        settings.append([0, 'x', node.x])
        settings.append([0, 'y', node.y])
        settings.append([0, 'width', node.width])
        settings.append([0, 'height', node.height])
        settings.append([0, 'rotation', node.rotation])
        settings.append([0, 'mask_type', node.mask_type])

        settings.append([1, 'Mask', node.inputs['Mask'].default_value])
        settings.append([1, 'Value', node.inputs['Value'].default_value])

    elif node.type == 'KEYING':

        settings.append([0, 'blur_pre', node.blur_pre])
        settings.append([0, 'screen_balance', node.screen_balance])
        settings.append([0, 'despill_factor', node.despill_factor])
        settings.append([0, 'despill_balance', node.despill_balance])
        settings.append([0, 'edge_kernel_radius', node.edge_kernel_radius])
        settings.append([0, 'edge_kernel_tolerance', node.edge_kernel_tolerance])
        settings.append([0, 'clip_black', node.clip_black])
        settings.append([0, 'clip_white', node.clip_white])
        settings.append([0, 'dilate_distance', node.dilate_distance])
        settings.append([0, 'feather_falloff', node.feather_falloff])
        settings.append([0, 'feather_distance', node.feather_distance])
        settings.append([0, 'blur_post', node.blur_post])

        settings.append([1, 'Core Matte', node.inputs['Core Matte'].default_value])
        settings.append([1, 'Garbage Matte', node.inputs['Garbage Matte'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Key Color',
                         [node.inputs['Key Color'].default_value[0],
                          node.inputs['Key Color'].default_value[1],
                          node.inputs['Key Color'].default_value[2],
                          node.inputs['Key Color'].default_value[3]]])

    elif node.type == 'LUMA_MATTE':

        settings.append([-1, -1, -1])

    elif node.type == 'DIFF_MATTE':

        settings.append([0, 'limit_max', node.limit_max])
        settings.append([0, 'limit_min', node.limit_min])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'CORNERPIN':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Lower Left',
                         [node.inputs['Lower Left'].default_value[0],
                          node.inputs['Lower Left'].default_value[1],
                          node.inputs['Lower Left'].default_value[2]]])

        settings.append([1, 'Lower Right',
                         [node.inputs['Lower Right'].default_value[0],
                          node.inputs['Lower Right'].default_value[1],
                          node.inputs['Lower Right'].default_value[2]]])

        settings.append([1, 'Upper Left',
                         [node.inputs['Upper Left'].default_value[0],
                          node.inputs['Upper Left'].default_value[1],
                          node.inputs['Upper Left'].default_value[2]]])

        settings.append([1, 'Upper Right',
                         [node.inputs['Upper Right'].default_value[0],
                          node.inputs['Upper Right'].default_value[1],
                          node.inputs['Upper Right'].default_value[2]]])

    elif node.type == 'CROP':

        settings.append([0, 'use_crop_size', node.use_crop_size])
        settings.append([0, 'relative', node.relative])
        settings.append([0, 'min_x', node.min_x])
        settings.append([0, 'min_y', node.min_y])
        settings.append([0, 'max_x', node.max_x])
        settings.append([0, 'max_y', node.max_y])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'DISPLACE':

        settings.append([1, 'X Scale', node.inputs['X Scale'].default_value])
        settings.append([1, 'Y Scale', node.inputs['Y Scale'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'Vector',
                         [node.inputs['Vector'].default_value[0],
                          node.inputs['Vector'].default_value[1],
                          node.inputs['Vector'].default_value[2]]])

    elif node.type == 'FLIP':

        settings.append([0, 'axis', node.axis])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'LENSDIST':

        settings.append([0, 'use_projector', node.use_projector])
        settings.append([0, 'use_jitter', node.use_jitter])
        settings.append([0, 'use_fit', node.use_fit])

        settings.append([1, 'Distort', node.inputs['Distort'].default_value])
        settings.append([1, 'Dispersion', node.inputs['Dispersion'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'MAP_UV':

        settings.append([0, 'alpha', node.alpha])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

        settings.append([1, 'UV',
                         [node.inputs['UV'].default_value[0],
                          node.inputs['UV'].default_value[1],
                          node.inputs['UV'].default_value[2]]])

    elif node.type == 'MOVIEDISTORTION':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'PLANETRACKDEFORM':

        settings.append([0, 'use_motion_blur', node.use_motion_blur])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'ROTATE':

        settings.append([1, 'Degr', node.inputs['Degr'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'SCALE':

        settings.append([0, 'space', node.space])
        settings.append([1, 'X', node.inputs['X'].default_value])
        settings.append([1, 'Y', node.inputs['Y'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'STABILIZE2D':

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'TRANSFORM':

        settings.append([0, 'filter_type', node.filter_type])

        settings.append([1, 'X', node.inputs['X'].default_value])
        settings.append([1, 'Y', node.inputs['Y'].default_value])
        settings.append([1, 'Angle', node.inputs['Angle'].default_value])
        settings.append([1, 'Scale', node.inputs['Scale'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    elif node.type == 'TRANSLATE':

        settings.append([0, 'use_relative', node.use_relative])
        settings.append([0, 'wrap_axis', node.wrap_axis])

        settings.append([1, 'X', node.inputs['X'].default_value])
        settings.append([1, 'Y', node.inputs['Y'].default_value])

        settings.append([1, 'Image',
                         [node.inputs['Image'].default_value[0],
                          node.inputs['Image'].default_value[1],
                          node.inputs['Image'].default_value[2],
                          node.inputs['Image'].default_value[3]]])

    else:
        settings.append([-1,-1,-1]) #  -1 Means that it dosen't have any extra settings


    if main_mode == 'SUB_TREE':

        dict['node'].append({
            'node': node.bl_idname,
            'name': node.name,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': type,
            'parent': nimi,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

    elif main_mode == 'MAIN_TREE':

        dict['nodes'].append({
            'node': node.bl_idname,
            'name': node.name,
            'location': [node.location[0], node.location[1]],
            'hide': node.hide,
            'main_socket_type': "",
            'parent': nimi,
            'height': node.height,
            'width': node.width,
            'extra_settings': settings
        })

    return dict

def readExtraSettings(extra_settings, node):
    for setting in extra_settings:
        if setting[0] == 0:
            setattr(node, setting[1], setting[2])
        elif setting[0] == 1:
            node.inputs[setting[1]].default_value = setting[2]
        elif setting[0] == 2:
            node.outputs[setting[1]].default_value = setting[2]

        # Image loading for image texture node

        elif setting[0] == 3:
            print("Extasetting 3")
            if (setting[2] != '' and node.clip == None):

                use_this_path = ''
                for clip in bpy.data.movieclips:
                    if (clip.filepath == setting[2]):
                        use_this_path = clip
                        break
                if (use_this_path == ''):
                    if (os.path.isfile(setting[2])):
                        node.clip = bpy.data.movieclips.load(setting[2])
                else:
                    node.clip = use_this_path

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

        # COLOR RAMP // 7 and 8

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

        # HUE CORRECT // 9

        elif setting[0] == 9:
            data = setting[2]
            curve = node.mapping.curves[setting[1]]

            if(node.type == 'CURVE_RGB'):

                if(len(data) > 2):
                    while(len(curve.points) < len(data)):
                        curve.points.new(0, 0)
                elif (len(data) < 2):
                    while(len(curve.points) > len(data)):
                        curve.points.remove(curve.points[0])

                for index, loc in enumerate(setting[2]):
                    curve.points[index].location = loc

            else:
                if (len(data) > 8):
                    while (len(curve.points) < len(data)):
                        curve.points.new(0, 0)
                elif (len(data) < 8):
                    while (len(curve.points) > len(data)):
                        curve.points.remove(curve.points[0])

                for index, loc in enumerate(setting[2]):
                    curve.points[index].location = loc



        # Image1 ja Image2 kasittely taalla // 10

        elif setting[0] == 10:
            node.inputs[setting[1]].default_value = setting[2]

        # Group node extra settings
        elif setting[0] == 11:
            node.inputs[setting[1]].default_value = setting[2]
            node.node_tree.inputs[setting[1]].min_value = setting[3]
            node.node_tree.inputs[setting[1]].max_value = setting[4]



