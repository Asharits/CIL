#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ccpi.framework import ImageData, TestData, ImageGeometry, AcquisitionGeometry, AcquisitionData, BlockDataContainer

from ccpi.optimisation.functions import L2NormSquared, ZeroFunction, L1Norm, BlockFunction, MixedL21Norm, IndicatorBox, FunctionOperatorComposition
from ccpi.optimisation.operators import Gradient, BlockOperator
from ccpi.optimisation.algorithms import PDHG, SIRT, CGLS

from ccpi.astra.operators import AstraProjectorSimple, AstraProjector3DSimple
from ccpi.astra.processors import FBP, AstraForwardProjector, AstraBackProjector

import tomophantom
from tomophantom import TomoP2D
import os, sys, time

import matplotlib.pyplot as plt


import numpy as np
#import islicer, link_islicer, psnr, plotter2D
from ccpi.utilities.display import show

from ccpi.optimisation.algorithms import Algorithm, GradientDescent   
import numpy


from ccpi.optimisation.functions import Norm2Sq
from ccpi.utilities.display import plotter2D


# stochastic imports

from ccpi.optimisation.algorithms import StochasticGradientDescent
#from ccpi.optimisation.functions import StochasticNorm2Sq
from ccpi.framework import AcquisitionGeometrySubsetGenerator

# get_ipython().magic(u'matplotlib inline')


# In[4]:


model = 12 # select a model number from the library
N = 1024 # set dimension of the phantom
device = 'gpu'
path = os.path.dirname(tomophantom.__file__)
path_library2D = os.path.join(path, "Phantom2DLibrary.dat")

phantom = TomoP2D.Model(model, N, path_library2D) 

# Define image geometry.
ig = ImageGeometry(voxel_num_x = N, voxel_num_y = N, 
                   voxel_size_x = 0.1,
                   voxel_size_y = 0.1)
im_data = ig.allocate()
im_data.fill(phantom)

# show(im_data, title = 'TomoPhantom', cmap = 'inferno')
# Create AcquisitionGeometry and AcquisitionData 
detectors = N
angles = np.linspace(0, np.pi, 180, dtype='float32')
ag = AcquisitionGeometry('parallel','2D', angles, detectors,
                        pixel_size_h = 0.1)

# Create projection operator using Astra-Toolbox. Available CPU/CPU
A = AstraProjectorSimple(ig, ag, device = device)
data = A.direct(im_data)

data_no_subset = data.copy()


# In[ ]:




class AstraSubsetProjectorSimple(AstraProjectorSimple):
    
    def __init__(self, geomv, geomp, device, **kwargs):
        kwargs = {'indices':None, 
                  'subset_acquisition_geometry':None,
                  #'subset_id' : 0,
                  #'number_of_subsets' : kwargs.get('number_of_subsets', 1)
                  }
        # This does not forward to its parent class :(
        super(AstraSubsetProjectorSimple, self).__init__(geomv, geomp, device)
        number_of_subsets = kwargs.get('number_of_subsets',1)
        # self.sinogram_geometry.generate_subsets(number_of_subsets, 'random')
        if geomp.number_of_subsets > 1:
            self.notify_new_subset(0, geomp.number_of_subsets)
        
    def notify_new_subset(self, subset_id, number_of_subsets):
        # print ('AstraSubsetProjectorSimple notify_new_subset')
        # updates the sinogram geometry and updates the projectors
        self.subset_id = subset_id
        self.number_of_subsets = number_of_subsets

        # self.sinogram_geometry.subset_id = subset_id

        #self.indices = self.sinogram_geometry.subsets[subset_id]
        device = self.fp.device
        # this will only copy the subset geometry
        ag = self.sinogram_geometry.copy()
        #print (ag.shape)
        
        self.fp = AstraForwardProjector(volume_geometry=self.volume_geometry,
                                        sinogram_geometry=ag,
                                        proj_id = None,
                                        device=device)

        self.bp = AstraBackProjector(volume_geometry = self.volume_geometry,
                                        sinogram_geometry = ag,
                                        proj_id = None,
                                        device = device)
    

    
# In[ ]:


# Create projection operator using Astra-Toolbox. Available CPU/CPU


#%%
nsubs = 10
step_rate = 0.0002328

data.geometry.generate_subsets(nsubs,'uniform')

OS_A = AstraSubsetProjectorSimple(ig, data.geometry, device = 'gpu')
### Check single steps

# GD does A.adjoint(A.direct(x) - b)
print (data.geometry.subset_id)

x = OS_A.domain_geometry().allocate(0)
tmp = OS_A.domain_geometry().allocate(0)

#%%
inline0 = time.time()
for j in range(100):
    for i in range(nsubs):
        data.geometry.subset_id = i
        OS_A.notify_new_subset(i, nsubs)
        #print(numpy.where(data.geometry.subsets[i]>0))
        axmb = OS_A.direct(x)
        # print (data.geometry.angles)
        # print (axmb.geometry.angles)
    #    print (axmb.shape)
        numpy.testing.assert_array_equal(data.geometry.angles[data.geometry.subsets[i]], axmb.geometry.angles)
        axmb -= data
        
    #    print (diff.geometry.angles)
    #    print (diff.shape)
        
        OS_A.adjoint(axmb, out=tmp)
        tmp *= -step_rate
        
        x+=tmp
inline1 = time.time()
    
plotter2D(x)


#%%

# use the whole dataset -> reset to 1 subset.
data.geometry.generate_subsets(1, 'random')
l2 = Norm2Sq(A=A, b=data)
gd = GradientDescent(x_init=im_data*0., objective_function=l2, step_size=None , 
     update_objective_interval=10, max_iteration=100)
tgd0 = time.time()
gd.run(100)
tgd1 = time.time()
print (gd.step_size)

plotter2D([x, gd.get_output(), x - gd.get_output()], titles=['stochastic', 'GD', 'diff'], cmap='viridis')
#%%


class StochasticNorm2Sq(Norm2Sq):
    def __init__(self, A, b, c=1.0):
        super(StochasticNorm2Sq, self).__init__(A, b, c)
        
    def notify_new_subset(self, subset_id, number_of_subsets):
        self.b.geometry.subset_id = subset_id
        self.A.notify_new_subset(subset_id, number_of_subsets)
        

nsubs = 10
data.generate_subsets(nsubs, 'uniform')

sl2 = StochasticNorm2Sq(A=OS_A, b=data)

sgd = StochasticGradientDescent(x_init=im_data*0., 
                                objective_function=sl2, alpha=1e6,
                                update_objective_interval=10, max_iteration=1000, 
                                number_of_subsets=nsubs)

#b = OS_A.direct(im_data)
#
#print ('direct ->' , b.shape)
#b.subtract(data, out=b)
#
#x = OS_A.adjoint(b)
#print (x.shape)

tsgd0 = time.time()
sgd.run(100)
tsgd1 = time.time()
#%%
plotter2D([im_data, 
           gd.get_output(), 
           gd.get_output()-sgd.get_output(), 
           sgd.get_output() ,
           #x
           ], titles=\
          ['ground truth', 
           'GD {}'.format(tgd1- tgd0), 
           'GD - SGD',
           'stochastic GD {}'.format(tsgd1 - tsgd0),
           #'inline GD {}'.format(inline1-inline0)
           ],
          cmap='viridis')
#
# , titles=['ground truth', 
#           'gd {} {}'.format(tgd1-tgd0, l2(gd.get_output())), 'sgd {} {}'.format(tsgd1-tsgd0, sl2(sgd.get_output())) ])





    

