# TXA_ant - Textured version of A.N.T. Landscape

V4.00.0 For Blender 4.0 - Materials now delivered in a blend file

Addon Download : [txa_ant_4_00_0.zip](https://github.com/nerk987/txa_ant/releases/download/v4.00.0/txa_ant_4_00_0.zip) 

Note, the materials supplied in the add-on are only suitable for Blender 4.0. Use earlier addon versions for earlier versions of Blender.

# Introduction
This add-on is a fork of the A.N.T. Lanscape addon and creates landscapes and planets using various noise types. Unlike ANT, TXA produced simple geometry and generates the landscapes with height and normal maps.

For a quick start introduction:
* Install the addon
* 3D View ‣ Add ‣ Mesh menu ‣ TXA Landscape
* Note that the landscape is a simple plane with subdivision and displace modifiers
* Set Viewport Shading to Material Preview mode
* Locate the Eroder Params panel in the TXA Landscape Sidebar tab
* Change Preferred Material to Volcano
* Click the Landscape Eroder button

# Tutorials
[Tutorial Video](https://youtu.be/bUGkdVrnrug?si=24nhsUpovXV-nQaH)

[PBR Baking Video](https://youtu.be/V8YRMB1_eeM?si=hgsbWjl_TDE341Y7)

[How To Create Terrain and Landscapes in Blender - Tutorial for Blender 4](https://www.youtube.com/watch?v=FOMmvspCcQk)

# Installation
Download the ZIP file the link above. Open Blender and go to Preferences then the Add-ons tab.
Use the Install Addon button to select the txa_ant.zip file. Once installed, enable the TXA Landscape addon.

# Interface

Located in the 3D View ‣ Add ‣ Mesh menu.

Located in the 3D View ‣ Sidebar ‣ TXA Landscape tab.

# Instructions
After creating your landscape mesh there’s three main areas in the Adjust Last Operation panel to design your mesh.

Main Settings: Object and mesh related settings like size and texture resolution.
Noise Settings: Noise related settings that give shape to your terrain.
Displace Settings: Settings for terrain height and edge falloff.
Landscape Panel
Landscape
Landscape will create the mesh and add several panels and tools to the Sidebar.
Landscape Tools
Mesh Displace
Displace selected mesh vertices along normal or X, Y, Z direction.
Weight From Slope
Generates a weighted vertex group slope map based on the Z normal value.
Landscape Eroder
Apply various kinds of erosion to an A.N.T. Landscape grid, also available in the Weights menu in Weight Paint Mode.
Landscape Main
Here we can adjust the main settings and regenerate the mesh.

Smooth the mesh, Triangulate the mesh, Rename and add materials that you have in your blend-file.

Landscape Noise
Here we can adjust the noise settings and refresh only those settings.

There are many settings and noise types here which allow you to customize your landscape.

Landscape Displace
Here we can adjust the displacement settings and refresh only those settings.

Adjust Height, Falloff and Strata in this section.
