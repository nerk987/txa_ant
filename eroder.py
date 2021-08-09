# ##### BEGIN GPL LICENSE BLOCK #####
#
#  erode.py  -- a script to simulate erosion of height fields
#  (c) 2014 Michel J. Anders (varkenvarken)
#  with some modifications by Ian Huish (nerk)
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

#TXA version v2.91.0
#Based on ANT version v0.1.8


from time import time
import unittest
import sys
import os
from random import random as rand, shuffle
import numpy as np
import bpy
import math
import mathutils.noise

numexpr_available = False



def getmemsize():
    return 0.0


def getptime():
    return time()
    
def SaveImageNodes():
    ntrees = []
    for mat in bpy.data.materials:
        ntrees.append([mat.name,mat.node_tree])
    for ng in bpy.data.node_groups:
        ntrees.append(["", ng])
    # print("SaveImageNodes - number of node trees: ", len(ntrees))
    nodedict = {}
    for prefix, nt in ntrees:
        if nt is not None:
            for node in nt.nodes:
                # if node.type == "TEX_IMAGE" and node.image is None:
                    # print("SaveImageNodes - image already none: ", node.name)
                if node.type == "TEX_IMAGE" and node.image is not None:
                    nkey = prefix + " " + nt.name + "_" + node.name
                    # print("SaveImageNodes -     nkey: ", nkey)
                    nodedict[nkey] = node.image.name
                    # print("SaveImageNodes - image is saved: ", node.name, nodedict[nkey])
    return nodedict

def RestoreImageNodes(nodedict):
    ntrees = []
    for mat in bpy.data.materials:
        ntrees.append([mat.name,mat.node_tree])
    for ng in bpy.data.node_groups:
        ntrees.append(["", ng])
    # print("RetoreImageNodes - number of node trees: ", len(ntrees))
    for prefix, nt in ntrees:
        if nt is not None:
            for node in nt.nodes:
                if node.type == "TEX_IMAGE" and node.image is None:
                    # print("RestoreImageNodes - Image needs restoring: ", node.name)
                    nkey = prefix + " " + nt.name + "_" + node.name
                    # print("RestoreImageNodes -     nkey: ", nkey)
                    # print("RestoreImageNodes -     found: ", nkey in nodedict)
                if node.type == "TEX_IMAGE" and node.image is None and nkey in nodedict:
                    if nodedict[nkey] in bpy.data.images:
                        node.image = bpy.data.images[nodedict[nkey]]
                        # print("RestoreImageNodes - Restored: ", nodedict[nkey])
                    else:
                        print("RestoreImageNodes - Save image not found: ", nodedict[nkey])



class Grid:

    def __init__(self, dim_x=10, dim_y=10, dtype=np.single):
        # print("Init Grid")
        self.center = np.zeros([dim_x, dim_y], dtype)
        self.water = None
        self.sediment = None
        self.scour = None
        self.flowrate = None
        self.sedimentpct = None
        self.gradient = None
        # self.sedimentpct = None
        self.capacity = None
        self.avalanced = None
        self.noise = None
        self.beach = None
        self.foam = None
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None
        self.zscale = 1
        self.maxrss = 0.0
        self.sequence = [0, 1, 2, 3]
        self.watermax = 1.0
        self.flowratemax = 1.0
        self.scourmax = 1.0
        self.sedmax = 1.0
        self.scourmin = 1.0


    def init_water_and_sediment(self):
        if self.water is None:
            self.water = np.zeros(self.center.shape, dtype=np.single)
        if self.sediment is None:
            self.sediment = np.zeros(self.center.shape, dtype=np.single)
        if self.scour is None:
            self.scour = np.zeros(self.center.shape, dtype=np.single)
        if self.flowrate is None:
            self.flowrate = np.zeros(self.center.shape, dtype=np.single)
        if self.sedimentpct is None:
            self.sedimentpct = np.zeros(self.center.shape, dtype=np.single)
        if self.capacity is None:
            self.capacity = np.zeros(self.center.shape, dtype=np.single)
        # print("Init_water capacity shape: ", self.capacity.shape)
        if self.avalanced is None:
            self.avalanced = np.zeros(self.center.shape, dtype=np.single)
        if self.gradient is None:
            self.gradient = np.zeros(self.center.shape, dtype=np.single)
        if self.noise is None:
            self.noise = np.zeros(self.center.shape, dtype=np.single)


    def __str__(self):
        return ''.join(self.__str_iter__(fmt="%.3f"))


    def __str_iter__(self, fmt):
        for row in self.center[::]:
            values=[]
            for v in row:
                values.append(fmt%v)
            yield  ' '.join(values) + '\n'


        
        
    def shrink(self, a, S=2): # S : shrink factor
        new_shp = np.vstack((np.array(a.shape)//S,[S]*a.ndim)).ravel('F')
        return a.reshape(new_shp).mean(tuple(1+2*np.arange(a.ndim)))
        
    def upscale(self, A, B, k):     # fill A with B scaled by k
        Y = A.shape[0]
        X = A.shape[1]
        for y in range(0, k):
            for x in range(0, k):
                A[y:Y:k, x:X:k] = B
                
    def blur(self, a):
        kernel = np.array([[1.0,2.0,1.0], [2.0,4.0,2.0], [1.0,2.0,1.0]])
        kernel = kernel / np.sum(kernel)
        arraylist = []
        for y in range(3):
            temparray = np.copy(a)
            temparray = np.roll(temparray, y - 1, axis=0)
            for x in range(3):
                temparray_X = np.copy(temparray)
                temparray_X = np.roll(temparray_X, x - 1, axis=1)*kernel[y,x]
                arraylist.append(temparray_X)

        arraylist = np.array(arraylist)
        arraylist_sum = np.sum(arraylist, axis=0)
        return arraylist_sum
   
        
                
    @staticmethod
    def fromImage(image):
        # print("FromImage")
        g = Grid(dim_x=image.size[1], dim_y=image.size[0])
        # g.center = np.zeros([image.size[0], image.size[0]], np.single)
        HMap = np.array(image.pixels)
        # print("fromImage - Image size: ", image.size[0], image.size[1])
        HMap.shape = (image.size[1], image.size[0], 4)
        g.center = HMap[:,:,0]
        # print("FromImage Finished")
        g.rainmap = np.copy(g.center)
        g.sedimentcalc(1.0)
        return g
        
    def CreateImage(self, ImageName, size_x, size_y):
        if ImageName not in bpy.data.images.keys():
            bpy.data.images.new(ImageName, size_x, size_y, alpha=True, float_buffer=True)
        else:
            bpy.data.images[ImageName].generated_width = size_x
            bpy.data.images[ImageName].generated_height = size_y
        outputImg = bpy.data.images[ImageName]
        outputImg.colorspace_settings.name = 'Linear'
        return outputImg
    
    
        
    def toImage(self, mesh_size_x, mesh_size_y, mesh_size_z, name):
        dim_x = self.center.shape[0]
        dim_y = self.center.shape[1]
        # print("Max Height: ", np.amax(self.center))
        
        #Save image names in texture nodes in all materials just in case the images change
        #- eg resolution change
        nodedict = SaveImageNodes()
        
        #Normal Map
        if name+"_normal" in bpy.data.images:
            NormalMapImg = bpy.data.images[name+"_normal"]
            bpy.data.images.remove(NormalMapImg)
        NormalMapImg = self.CreateImage(name+"_normal", dim_y, dim_x)
        pixels = np.zeros((dim_x,dim_y,4), dtype = np.float16)
        pixels[:,:,-1:] = 1.0
        # calculate normals
        zy, zx = np.gradient(self.center)  
        # You may also consider using Sobel to get a joint Gaussian smoothing and differentation
        # to reduce noise
        #zx = cv2.Sobel(d_im, cv2.CV_64F, 1, 0, ksize=5)     
        #zy = cv2.Sobel(d_im, cv2.CV_64F, 0, 1, ksize=5)

        normal = np.dstack((-zx/mesh_size_x, -zy*self.center.shape[0]/(mesh_size_y*self.center.shape[1]), np.ones_like(self.center)/(mesh_size_z*self.center.shape[0])))
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
        
        #do smooth gradient using normal while we're here
        # print("Normal Shape: ", normal[:,:,2].shape)
        self.gradient = self.blur(normal[:,:,2])
        
        NormalMapImg.pixels = pixels.ravel()
        NormalMapImg.pack()
        NormalMapImg.update()
        
        #Avalanche Maps
        if name+"_avalanche" in bpy.data.images:
            AvalancheImg = bpy.data.images[name+"_avalanche"]
            bpy.data.images.remove(AvalancheImg)
        AvalancheImg = self.CreateImage(name+"_avalanche", dim_y, dim_x)
        pixels = np.zeros((dim_x,dim_y,4), dtype = np.float16)
        pixels[:,:,-1:] = 1.0
        ava_max = np.amax(self.avalanced)
        ava_min = np.amin(self.avalanced)
        ava_span = max(ava_max, math.fabs(ava_min))/1.0+.00005
        # pixels[:,:,0] = self.avalanced/ava_span + 0.5
        pixels[:,:,0] = self.avalanced
        grad_max = np.amax(self.gradient)
        pixels[:,:,1] = self.gradient/(grad_max + 0.000001)
        
        scour_max = np.amax(self.scour)
        scour_min = np.amin(self.scour)
        scour_span = max(scour_max, math.fabs(scour_min))/1.0+.00005
        pixels[:,:,2] = self.scour/scour_span + 0.5
        AvalancheImg.pixels = pixels.ravel()
        AvalancheImg.pack()
        AvalancheImg.update()
        
        # Water Maps
        if name+"_water" in bpy.data.images:
            WaterImg = bpy.data.images[name+"_water"]
            bpy.data.images.remove(WaterImg)
        WaterImg = self.CreateImage(name+"_water", dim_y, dim_x)
        pixels = np.zeros((dim_x,dim_y,4), dtype = np.float16)
        pixels[:,:,-1:] = 1.0
        flow_max = np.amax(self.flowrate)
        pixels[:,:,0] = self.flowrate/flow_max
        # sediment_max = np.amax(self.noise)
        # pixels[:,:,1] = self.noise/sediment_max
        sediment_max = np.amax(self.sediment)+0.000001
        pixels[:,:,1] = self.sediment/sediment_max
        water_max = np.amax(self.water)
        pixels[:,:,2] = self.water/water_max
        # water_max = np.amax(self.capacity)
        # pixels[:,:,2] = self.capacity/water_max

        WaterImg.pixels = pixels.ravel()
        WaterImg.pack()
        WaterImg.update()
        # New Height Map
        if name+"_erodedheight" in bpy.data.images:
            ErodedHeightImg = bpy.data.images[name+"_erodedheight"]
            bpy.data.images.remove(ErodedHeightImg)
        ErodedHeightImg = self.CreateImage(name+"_erodedheight", dim_y, dim_x)
        pixels = np.zeros((dim_x,dim_y,4), dtype = np.float16)
        pixels[:,:,-1:] = 1.0
        # center_max = np.amax(self.center) + .000000000001
        pixels[:,:,0] = self.center#/center_max
        pixels[:,:,1] = pixels[:,:,0]
        pixels[:,:,2] = pixels[:,:,0]
        ErodedHeightImg.pixels = pixels.ravel()
        ErodedHeightImg.pack()
        ErodedHeightImg.update()

        # Beach Map if it was generated
        if self.beach is not None:
            if name+"_beach" in bpy.data.images:
                BeachImg = bpy.data.images[name+"_beach"]
                bpy.data.images.remove(BeachImg)
            BeachImg = self.CreateImage(name+"_beach", dim_y, dim_x)
            pixels = np.zeros((dim_x,dim_y,4), dtype = np.float16)
            pixels[:,:,-1:] = 1.0
            pixels[:,:,0] = self.beach
            pixels[:,:,1] = self.foam
            pixels[:,:,2] = pixels[:,:,0]
            BeachImg.pixels = pixels.ravel()
            BeachImg.pack()
            BeachImg.update()

        #Restore any lost image references in materials
        RestoreImageNodes(nodedict)
        

    


    def setrainmap(self, rainmap):
        self.rainmap = rainmap


    def _verts(self, surface):
        a = surface / self.zscale
        minx = 0.0 if self.minx is None else self.minx
        miny = 0.0 if self.miny is None else self.miny
        maxx = 1.0 if self.maxx is None else self.maxx
        maxy = 1.0 if self.maxy is None else self.maxy
        dx = (maxx - minx) / (a.shape[0] - 1)
        dy = (maxy - miny) / (a.shape[1] - 1)
        for row in range(a.shape[0]):
            row0 = miny + row * dy
            for col in range(a.shape[1]):
                col0 = minx + col * dx
                yield (row0 ,col0 ,a[row  ][col  ])


    def _faces(self):
        nrow, ncol = self.center.shape
        for row in range(nrow-1):
            for col in range(ncol-1):
              vi = row * ncol + col
              yield (vi, vi+ncol, vi+1)
              yield (vi+1, vi+ncol, vi+ncol+1)


    def toBlenderMesh(self, me):
        # pass me as argument so that we don't need to import bpy and create a dependency
        # the docs state that from_pydata takes iterators as arguments but it will fail with generators because it does len(arg)
        me.from_pydata(list(self._verts(self.center)),[],list(self._faces()))


    def toWaterMesh(self, me):
        # pass me as argument so that we don't need to import bpy and create a dependency
        # the docs state that from_pydata takes iterators as arguments but it will fail with generators because it does len(arg)
        me.from_pydata(list(self._verts(self.water)),[],list(self._faces()))


    def peak(self, value=1):
        nx,ny = self.center.shape
        self.center[int(nx/2),int(ny/2)] += value


    def shelf(self, value=1):
        nx,ny = self.center.shape
        self.center[:nx/2] += value


    def mesa(self, value=1):
        nx,ny = self.center.shape
        self.center[nx/4:3*nx/4,ny/4:3*ny/4] += value


    def random(self, value=1):
        self.center += np.random.random_sample(self.center.shape)*value


    def neighborgrid(self):
        self.up = np.roll(self.center,-1,0)
        self.down = np.roll(self.center,1,0)
        self.left = np.roll(self.center,-1,1)
        self.right = np.roll(self.center,1,1)


    def zeroedge(self, quantity=None):
        c = self.center if quantity is None else quantity
        c[0,:] = 0
        c[-1,:] = 0
        c[:,0] = 0
        c[:,-1] = 0
        
    # def makegradient(self):
        # c = self.center
        # cc = self.center[1:-1,1:-1]
        # maxs = np.maximum.reduce([c[:-2, 1:-1], c[1:-1, 2:], c[2:, 1:-1], c[1:-1,:-2]]) - cc
        # self.gradient[1:-1,1:-1] = np.absolute(maxs)
        # self.gradient = np.gradient(c)
        
    def smoothedge(self, param, width):
        rx = np.arange(param.shape[0])
        ry = np.arange(param.shape[1])
        dx = np.minimum(rx,rx[::-1])
        dy = np.minimum(ry,ry[::-1])
        p = np.minimum.outer(dx,dy).astype('float16')
        np.clip(p,0,width, out=p)
        return np.multiply(param,p)/width
        
   
        
    def sedimentcalc(self, Kc):
        # print("Kc: ", Kc)
        spct = np.ones(self.center.shape, dtype=np.float16) - self.center/np.amax(self.center)
        spct2 = self.smoothedge(spct, min(self.center.shape[0],self.center.shape[1])/30.0)
        self.sedimentpct = np.zeros(self.center.shape, dtype=np.float16)
        self.noise = np.zeros(self.center.shape, dtype=np.float16)
        height_max = np.amax(self.center)        
        for i in range(self.center.shape[0]):
            for j in range(self.center.shape[1]):
                x = self.center[i,j]/height_max
                self.sedimentpct[i,j] = (-13.054*x**4+34.542*x**3-30.84*x**2+9.41*x-0.0484 + spct2[i,j]) * (1.0 - Kc)
                #This doesn't really belong here, just convenient
                self.noise[i,j] = mathutils.noise.noise((50.0*i/self.center.shape[0],50.0*j/self.center.shape[0],0.0))*0.5+0.5


    def diffuse(self, Kd, IterDiffuse, numexpr):
        self.zeroedge()
        c = self.center[1:-1,1:-1]
        up = self.center[ :-2,1:-1]
        down = self.center[2:  ,1:-1]
        left = self.center[1:-1, :-2]
        right = self.center[1:-1,2:  ]
        if(numexpr and numexpr_available):
            self.center[1:-1,1:-1] = ne.evaluate('c + Kd * (up + down + left + right - 4.0 * c)')
        else:
            self.center[1:-1,1:-1] = c + (Kd/IterDiffuse) * (up + down + left + right - 4.0 * c)
        self.maxrss = max(getmemsize(), self.maxrss)
        return self.center


    def avalanche(self, delta, delta_river, iterava, river_sense, noise_effect, numexpr, mesh_size_x, mesh_size_y, mesh_size_z):
        self.zeroedge()
        c     = self.center[1:-1,1:-1]
        flow = self.flowrate[c.shape]
        up    = self.center[ :-2,1:-1]
        down  = self.center[2:  ,1:-1]
        left  = self.center[1:-1, :-2]
        right = self.center[1:-1,2:  ]
        where = np.where
        # A flow value of 1 moves all the rock in one go, 2 does half etc.
        # Use the high flow near the bottom of the hill and low at the top to stabilise the flow
        # hi_flow = 2.0
        # lo_flow = 4.0
        # hi_flow = 4.0
        # lo_flow = 2.0
        in_factor = 0.2
        out_factor = 0.1
        
        cap = self.flowrate[1:-1,1:-1]
        max_cap = np.amax(cap)
        cap_inv = np.ones(c.shape, dtype = np.float16) - cap*(1.0-river_sense)/max_cap
        ne = self.noise[1:-1,2:]
        cap_inv = cap_inv - ne * noise_effect
        # cap_inv2 = np.clip(cap_inv * 2 - 0.5, 0., 1.)
        cap_inv2 = np.clip(cap_inv, 0., 1.)
        
        # delta_array = cap_inv
        # delta_array = np.multiply(cap_inv, delta)
        delta_array = np.multiply((np.ones(c.shape, dtype = np.float16) - cap_inv2), delta_river) + np.multiply(cap_inv2, delta)
        # delta_array = where((cap/max_cap) > river_sense or (cap/max_cap) > noise_effect, delta_river, delta)
        # print("Delta Array: ", delta_array.size)
        delta_y = delta_array * mesh_size_y / (c.shape[0] * mesh_size_z * 1.0)
        delta_x = delta_array * mesh_size_x / (c.shape[1] * mesh_size_z * 1.0)
        
        # print("Avalanche - delta: ", delta)

        if(numexpr and numexpr_available):
            self.center[1:-1,1:-1] = ne.evaluate('c + where((up   -c) > delta ,(up   -c -delta)/2, 0) \
                 + where((down -c) > delta ,(down -c -delta)/2, 0)  \
                 + where((left -c) > delta ,(left -c -delta)/2, 0)  \
                 + where((right-c) > delta ,(right-c -delta)/2, 0)  \
                 + where((up   -c) < -delta,(up   -c +delta)/2, 0)  \
                 + where((down -c) < -delta,(down -c +delta)/2, 0)  \
                 + where((left -c) < -delta,(left -c +delta)/2, 0)  \
                 + where((right-c) < -delta,(right-c +delta)/2, 0)')
        else:
            sa_in = (
                # incoming
                   where((up   -c) > delta_y ,(up   -c -delta_y) * in_factor, 0)
                 + where((down -c) > delta_y ,(down -c -delta_y) * in_factor, 0)
                 + where((left -c) > delta_x ,(left -c -delta_x) * in_factor, 0)
                 + where((right-c) > delta_x ,(right-c -delta_x) * in_factor, 0)
                 )
            sa_out = (
                # outgoing
                   where((up   -c) < -delta_y,(up   -c +delta_y) * out_factor, 0)
                 + where((down -c) < -delta_y,(down -c +delta_y) * out_factor, 0)
                 + where((left -c) < -delta_x,(left -c +delta_x) * out_factor, 0)
                 + where((right-c) < -delta_x,(right-c +delta_x) * out_factor, 0)
                 )
            sa = sa_in + sa_out
        # else:
            # sa = (
                # # incoming
                   # where((up   -c) > delta_y ,(up   -c -delta_y)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((down -c) > delta_y ,(down -c -delta_y)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((left -c) > delta_x ,(left -c -delta_x)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((right-c) > delta_x ,(right-c -delta_x)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                # # outgoing
                 # + where((up   -c) < -delta_y,(up   -c +delta_y)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((down -c) < -delta_y,(down -c +delta_y)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((left -c) < -delta_x,(left -c +delta_x)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # + where((right-c) < -delta_x,(right-c +delta_x)/(c * (lo_flow-hi_flow)+lo_flow), 0)
                 # )

      #Original random code  
        # randarray = np.random.randint(0,100,sa.shape) *0.01
        # sa = where(randarray < prob, sa, 0)
        # print("Avalance noise Min 1: ", np.amin(ne), np.amax(ne))
        # ne = ne * noise_effect
        # print("Avalance noise Min 3: ", np.amin(ne), np.amax(ne))
        # ne = np.ones(sa.shape, dtype=np.single) - ne
        # print("Avalance noise Min 4: ", np.amin(ne), np.amax(ne))
        # np.clip(ne*3.0-2.0, 0.0, 1.0, out=ne)
        # print("Avalance noise Min 5: ", np.amin(ne), np.amax(ne))
        # sa = np.multiply(sa, ne, out=sa)

        #Multiply effect by scour map  
        # sa2 = np.multiply(sa, scour2/max_scour)
        # self.avalanced[1:-1,1:-1] = self.avalanced[1:-1,1:-1] + sa2/iterava
        
        # Normal addition of sa 
        # self.avalanced[1:-1,1:-1] = cap_inv
        self.avalanced[1:-1,1:-1] = where(sa_in > 0 , 1, 0)
        
        self.center[1:-1,1:-1] = c + sa

        self.maxrss = max(getmemsize(), self.maxrss)
        return self.center


    def rain(self, amount=1, variance=0, userainmap=False):
        self.water += (1.0 - np.random.random(self.water.shape) * variance) * (amount if ((self.rainmap is None) or (not userainmap)) else self.rainmap * amount)
        # print("Max Rain: ", np.amax(self.rainmap), amount)


    def spring(self, amount, px, py, radius):
        # px, py and radius are all fractions
        nx, ny = self.center.shape
        rx = max(int(nx*radius),1)
        ry = max(int(ny*radius),1)
        px = int(nx*px)
        py = int(ny*py)
        self.water[px-rx:px+rx+1,py-ry:py+ry+1] += amount


    def river(self, Ks, Kdep, Ka, Kev, numexpr):
        zeros = np.zeros
        where = np.where
        min = np.minimum
        max = np.maximum
        abs = np.absolute
        arctan = np.arctan
        sin = np.sin

        center = (slice(   1,   -1,None),slice(   1,  -1,None))
        up     = (slice(None,   -2,None),slice(   1,  -1,None))
        down   = (slice(   2, None,None),slice(   1,  -1,None))
        left   = (slice(   1,   -1,None),slice(None,  -2,None))
        right  = (slice(   1,   -1,None),slice(   2,None,None))

        water = self.water
        rock = self.center
        sediment = self.sediment
        height = rock + water

        # !! this gives a runtime warning for division by zero
        verysmallnumber = 0.0000000001
        water += verysmallnumber
        sc = where(water > verysmallnumber, sediment / water, 0)

        sdw = zeros(water[center].shape)
        # print("River sdw shape: ", sdw.shape)
        svdw = zeros(water[center].shape)
        sds = zeros(water[center].shape)
        angle = zeros(water[center].shape)
        for d in (up,down,left,right):
            if(numexpr and numexpr_available):
                hdd = height[d]
                hcc = height[center]
                dw = ne.evaluate('hdd-hcc')
                inflow = ne.evaluate('dw > 0')
                wdd = water[d]
                wcc = water[center]
                dw = ne.evaluate('where(inflow, where(wdd<dw, wdd, dw), where(-wcc>dw, -wcc, dw))/4.0') # nested where() represent min() and max()
                sdw  = ne.evaluate('sdw + dw')
                scd  = sc[d]
                scc  = sc[center]
                rockd= rock[d]
                rockc= rock[center]
                sds  = ne.evaluate('sds + dw * where(inflow, scd, scc)')
                svdw = ne.evaluate('svdw + abs(dw)')
                angle= ne.evaluate('angle + arctan(abs(rockd-rockc))')
            else:
                # Potential change in water is height of neighbour water - current height of water (+ or -)
                dw = (height[d]-height[center])
                #Inflow is true if change is positive
                inflow = dw > 0
                #If Inflow is true, WaterDelta = Min( Potential change in water, Neighbours water) (eg. Height difference, but not more than neighbour has)
                #If not Inflow, WaterDelta = Max(Potential change in water, Water in current cell)
                #Note that the '4' should not be required, except for damping and for svdw (flowrate) calc
                dw = where(inflow, min(water[d], dw), max(-water[center], dw))/4.0
                #Total change in water over all neighbours
                sdw  = sdw + dw
                #Sediment total over all neighbours using water change * sediment fraction of origin
                sds  = sds + dw * where(inflow, sc[d], sc[center])
                #Total Flowrate both in and out of all neighbours 
                svdw = svdw + abs(dw)
                #Total amount of variation in height
                angle= angle + np.arctan(abs(rock[d]-rock[center]))

        if(numexpr and numexpr_available):
            wcc = water[center]
            scc = sediment[center]
            rcc = rock[center]
            water[center] = ne.evaluate('wcc + sdw')
            sediment[center] = ne.evaluate('scc + sds')
            sc = ne.evaluate('where(wcc>0, scc/wcc, 2000*Kc)')
            fKc = ne.evaluate('Kc*sin(Ka*angle)*svdw')
            ds = ne.evaluate('where(sc > fKc, -Kd * scc, Ks * svdw)')
            rock[center] = ne.evaluate('rcc - ds')
            # there isn't really a bottom to the rock but negative values look ugly
            rock[center] = ne.evaluate('where(rcc<0,0,rcc)')
            sediment[center] = ne.evaluate('scc + ds')
        else:
            wcc = water[center]
            scc = sediment[center]
            rcc = rock[center]
            #Water = Water * (1 - Evaporation) + WaterDelta
            water[center] = wcc * (1-Kev) + sdw
            #SedimentFraction is now set to the inverse of height, as an assumption rather than simulation
            # sc = np.ones(water[center].shape)
            rcc_max = np.amax(rcc)
            # sc = sc - rcc/rcc_max
            sc = self.sedimentpct[center]
            #Scouring:
            #If sediment carrying capacity exceeds sediment fraction, scouring is the difference times solubility factor
            #Else it's the difference times the deposit factor
            # ds = where(fKc > sc, (fKc - sc) * Ks, (fKc - sc) * Kdep) * wcc
            # ds = where(fKc > sc, (fKc - sc) * Ks, (fKc - sc) * Kdep) * wcc
            self.flowrate[center] = svdw
            #This could be a slow step?
            flow_max = np.amax(self.flowrate)
            #Total % Flowrate * Carrying Capacity
            #If this is higher than the associated sediment fraction, then scour, else deposit
            fKc = svdw/flow_max

            self.scour[center] = where(fKc > sc, (fKc - sc) * Ks, -water[center] * Kdep)
            # self.sedimentpct[center] = sc
            # self.capacity[center] = fKc
            sediment[center] = wcc * sc

        # #Original version
            # wcc = water[center]
            # scc = sediment[center]
            # rcc = rock[center]
            # #Water = Water * (1 - Evaporation) + WaterDelta
            # water[center] = wcc * (1-Kev) + sdw
            # #Sediment = Sediment + SedimentDelta
            # sediment[center] = scc + sds
            # #SedimentFraction = Sediment/Water (Unless no water, then 2 * Capacity)
            # sc = where(wcc > 0, scc / wcc, 2 * Kc)
            # #Total Flowrate * Carrying Capacity
            # fKc = Kc*svdw
            # #Scouring:
            # #If sediment carrying capacity exceeds sediment fraction, scouring is the difference times solubility factor
            # #Else it's the difference times the deposit factor
            # # ds = where(fKc > sc, (fKc - sc) * Ks, (fKc - sc) * Kdep) * wcc
            # ds = where(fKc > sc, (fKc - sc) * Ks, (fKc - sc) * Kdep) * wcc
            # self.flowrate[center] = svdw
            # self.scour[center] = ds
            # self.sedimentpct[center] = sc
            # self.capacity[center] = fKc
            # sediment[center] = scc + ds + sds


    def flow(self, Ks, Kz, Ka, Kdep, numexpr, water_plane, water_level, beach_height, beach_erosion):
        zeros = np.zeros
        where = np.where
        min = np.minimum
        max = np.maximum
        abs = np.absolute
        arctan = np.arctan
        sin = np.sin
        
        # A flow value of 1 moves all the rock in one go, 2 does half etc.
        # Use the high flow near the bottom of the hill and low at the top to stabilise the flow
        hi_flow = 4.0
        lo_flow = 2.0


        center = (slice(   1,   -1,None),slice(   1,  -1,None))
        rock = self.center
        # ds = self.scour[center]
        self.flowratemax = np.max(self.flowrate)
        ds = self.flowrate[center]/self.flowratemax
        dsed = self.flowrate[center]
        rcc = rock[center]
        #reduce fluvial erosion effects as the beach starts till there is no erosion at water level
        beach = np.clip((rcc - water_level)/beach_height, 0., 1.) * (1. - beach_erosion) + np.ones(rcc.shape) * beach_erosion
        # print("Kz: ", Kz, Kdep)
        #Simple Method (Don't delete)
        # rock[center] = rcc - ds * Kz/(rcc * (lo_flow-hi_flow)+lo_flow)
        #Scour Method
        rock[center] = rcc - np.multiply(self.scour[center], beach) * Kz
        rock[center] = rcc + dsed * Kdep/(rcc * (lo_flow-hi_flow)+lo_flow)
        # there isn't really a bottom to the rock but negative values look ugly
        rock[center] = where(rcc<0,0,rcc)


    def rivergeneration(self, rainamount, rainvariance, userainmap, Ks, Kdep, Ka, Kev, Kspring, Kspringx, Kspringy, Kspringr, numexpr):
        # print("rivergeneration - init_water")
        self.init_water_and_sediment()
        # print("rivergeneration - rain amount: ", rainamount/np.size(self.center))
        self.rain(rainamount/np.size(self.center), rainvariance, userainmap)
        self.zeroedge(self.water)
        self.zeroedge(self.sediment)
        # print("rivergeneration - river")
        self.river(Ks, Kdep, Ka, Kev, numexpr)
        self.watermax = np.max(self.water)


    def fluvial_erosion(self, rainamount, rainvariance, userainmap, Ks, Kz, Ka, Kdep, Kspring, Kspringx, Kspringy, Kspringr, numexpr, water_plane, water_level, beach_height, beach_erosion):
        self.flow(Ks, Kz, Ka, Kdep, numexpr, water_plane, water_level, beach_height, beach_erosion)
        # self.flowratemax = np.max(self.flowrate)
        # self.scourmax = np.max(self.scour)
        # self.scourmin = np.min(self.scour)
        # self.sedmax = np.max(self.sediment)
        
    def beach_erosion(self, water_level, beach_height, beach_slope, foam_depth):
        start = water_level + beach_height
        center = self.center
        self.center = np.where(center < start, start * beach_slope + center * (1.0 - beach_slope), center)
        self.beach = np.clip(np.negative(np.absolute((self.center - water_level)/max(beach_height, 0.00001)))+1.0, 0., 1.)
        self.foam = (self.center - water_level)/max(foam_depth, 0.00001)+1.0
        # self.foam = np.where(self.foam > 1., 2.-self.foam, self.foam)
        self.foam = np.clip(self.foam, 0., 1000.)
        self.center = np.clip(self.center, water_level + 0.0001, 10000.0)
        
    def analyze(self):
        self.neighborgrid()
        # just looking at up and left to avoid needless double calculations
        slopes=np.concatenate((np.abs(self.left - self.center),np.abs(self.up - self.center)))
        return '\n'.join(["%-15s: %.3f"%t for t in [
                ('height average', np.average(self.center)),
                ('height median', np.median(self.center)),
                ('height max', np.max(self.center)),
                ('height min', np.min(self.center)),
                ('height std', np.std(self.center)),
                ('slope average', np.average(slopes)),
                ('slope median', np.median(slopes)),
                ('slope max', np.max(slopes)),
                ('slope min', np.min(slopes)),
                ('slope std', np.std(slopes))
                ]]
            )


class TestGrid(unittest.TestCase):

    def test_diffuse(self):
        g = Grid(5)
        g.peak(1)
        self.assertEqual(g.center[2,2],1.0)
        g.diffuse(0.1, numexpr=False)
        for n in [(2,1),(2,3),(1,2),(3,2)]:
            self.assertAlmostEqual(g.center[n],0.1)
        self.assertAlmostEqual(g.center[2,2],0.6)


    def test_diffuse_numexpr(self):
        g = Grid(5)
        g.peak(1)
        g.diffuse(0.1, numexpr=False)
        h = Grid(5)
        h.peak(1)
        h.diffuse(0.1, numexpr=True)
        self.assertEqual(list(g.center.flat),list(h.center.flat))


    def test_avalanche_numexpr(self):
        g = Grid(5)
        g.peak(1)
        g.avalanche(0.1, numexpr=False)
        h = Grid(5)
        h.peak(1)
        h.avalanche(0.1, numexpr=True)
        # print(g)
        # print(h)
        np.testing.assert_almost_equal(g.center,h.center)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Erode a terrain while assuming zero boundary conditions.')
    parser.add_argument('-I', dest='iterations', type=int, default=1, help='the number of iterations')
    parser.add_argument('-Kd', dest='Kd', type=float, default=0.01, help='Diffusion constant')
    parser.add_argument('-Kh', dest='Kh', type=float, default=6, help='Maximum stable cliff height')
    parser.add_argument('-Kp', dest='Kp', type=float, default=0.1, help='Avalanche probability for unstable cliffs')
    parser.add_argument('-Kr', dest='Kr', type=float, default=0.1, help='Average amount of rain per iteration')
    parser.add_argument('-Kspring', dest='Kspring', type=float, default=0.0, help='Average amount of wellwater per iteration')
    parser.add_argument('-Kspringx', dest='Kspringx', type=float, default=0.5, help='relative x position of spring')
    parser.add_argument('-Kspringy', dest='Kspringy', type=float, default=0.5, help='relative y position of spring')
    parser.add_argument('-Kspringr', dest='Kspringr', type=float, default=0.02, help='radius of spring')
    parser.add_argument('-Kdep', dest='Kdep', type=float, default=0.1, help='Sediment deposition constant')
    parser.add_argument('-Ks', dest='Ks', type=float, default=0.1, help='Soil softness constant')
    parser.add_argument('-Kc', dest='Kc', type=float, default=1.0, help='Sediment capacity')
    parser.add_argument('-Ka', dest='Ka', type=float, default=2.0, help='Slope dependency of erosion')
    parser.add_argument('-ri', action='store_true', dest='rawin', default=False, help='use Blender raw format for input')
    parser.add_argument('-ro', action='store_true', dest='rawout', default=False, help='use Blender raw format for output')
    parser.add_argument('-i',  action='store_true', dest='useinputfile', default=False, help='use an inputfile (instead of just a synthesized grid)')
    parser.add_argument('-t',  action='store_true', dest='timingonly', default=False, help='do not write anything to an output file')
    parser.add_argument('-infile', type=str, default="-", help='input filename')
    parser.add_argument('-outfile', type=str, default="-", help='output filename')
    parser.add_argument('-Gn', dest='gridsize', type=int, default=20, help='Gridsize (always square)')
    parser.add_argument('-Gp', dest='gridpeak', type=float, default=0, help='Add peak with given height')
    parser.add_argument('-Gs', dest='gridshelf', type=float, default=0, help='Add shelve with given height')
    parser.add_argument('-Gm', dest='gridmesa', type=float, default=0, help='Add mesa with given height')
    parser.add_argument('-Gr', dest='gridrandom', type=float, default=0, help='Add random values between 0 and given value')
    parser.add_argument('-m', dest='threads', type=int, default=1, help='number of threads to use')
    parser.add_argument('-u', action='store_true', dest='unittest', default=False, help='perform unittests')
    parser.add_argument('-a', action='store_true', dest='analyze', default=False, help='show some statistics of input and output meshes')
    parser.add_argument('-d', action='store_true', dest='dump', default=False, help='show sediment and water meshes at end of run')
    parser.add_argument('-n', action='store_true', dest='usenumexpr', default=False, help='use numexpr optimizations')

    args = parser.parse_args()
    # print("\nInput arguments:")
    # print("\n".join("%-15s: %s"%t for t in sorted(vars(args).items())), file=sys.stderr)

    if args.unittest:
        unittest.main(argv=[sys.argv[0]])
        sys.exit(0)

    if args.useinputfile:
        if args.rawin:
            grid = Grid.fromRaw(args.infile)
        else:
            grid = Grid.fromFile(args.infile)
    else:
        grid = Grid(args.gridsize)

    if args.gridpeak > 0 : grid.peak(args.gridpeak)
    if args.gridmesa > 0 : grid.mesa(args.gridmesa)
    if args.gridshelf > 0 : grid.shelf(args.gridshelf)
    if args.gridrandom > 0 : grid.random(args.gridrandom)

    if args.analyze:
        print('\nstatistics of the input grid:\n\n', grid.analyze(), file=sys.stderr, sep='' )
    t = getptime()
    for g in range(args.iterations):
        if args.Kd > 0:
            grid.diffuse(args.Kd, args.usenumexpr)
        if args.Kh > 0 and args.Kp > rand():
            grid.avalanche(args.Kh, args.usenumexpr)
        if args.Kr > 0 or args.Kspring > 0:
            grid.fluvial_erosion(args.Kr, args.Kc, args.Ks, args.Kdep, args.Ka, args.Kspring, args.Kspringx, args.Kspringy, args.Kspringr, args.usenumexpr)
    t = getptime() - t
    # print("\nElapsed time: %.1f seconds, max memory %.1f Mb.\n"%(t,grid.maxrss), file=sys.stderr)
    if args.analyze:
        print('\nstatistics of the output grid:\n\n', grid.analyze(), file=sys.stderr, sep='')

    if not args.timingonly:
        if args.rawout:
            grid.toRaw(args.outfile, vars(args))
        else:
            grid.toFile(args.outfile)

    if args.dump:
        print("sediment\n", np.array_str(grid.sediment,precision=3), file=sys.stderr)
        print("water\n", np.array_str(grid.water,precision=3), file=sys.stderr)
        print("sediment concentration\n", np.array_str(grid.sediment/grid.water,precision=3), file=sys.stderr)
