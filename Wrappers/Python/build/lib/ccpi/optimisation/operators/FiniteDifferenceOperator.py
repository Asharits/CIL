#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 22:51:17 2019

@author: evangelos
"""

from ccpi.optimisation.operators import LinearOperator
from ccpi.optimisation.ops import PowerMethodNonsquare
from ccpi.framework import ImageData, BlockDataContainer
import numpy as np

class FiniteDiff(LinearOperator):
    
    # Works for Neum/Symmetric &  periodic boundary conditions
    # TODO add central differences???
    # TODO not very well optimised, too many conditions
    # TODO add discretisation step, should get that from imageGeometry
    
    # Grad_order = ['channels', 'direction_z', 'direction_y', 'direction_x']
    # Grad_order = ['channels', 'direction_y', 'direction_x']
    # Grad_order = ['direction_z', 'direction_y', 'direction_x']
    # Grad_order = ['channels', 'direction_z', 'direction_y', 'direction_x']
    
    def __init__(self, gm_domain, gm_range=None, direction=0, bnd_cond = 'Neumann'):
        ''''''
        super(FiniteDiff, self).__init__() 
        '''FIXME: domain and range should be geometries'''
        self.gm_domain = gm_domain
        self.gm_range = gm_range
        
        self.direction = direction
        self.bnd_cond = bnd_cond
        
        # Domain Geometry = Range Geometry if not stated
        if self.gm_range is None:
            self.gm_range = self.gm_domain
        # check direction and "length" of geometry
        if self.direction + 1 > len(self.gm_domain.shape):
            raise ValueError('Gradient directions more than geometry domain')      
        
        #self.voxel_size = kwargs.get('voxel_size',1)
        # this wrongly assumes a homogeneous voxel size
        self.voxel_size = self.gm_domain.voxel_size_x


    def direct(self, x, out=None):
        
        x_asarr = x.as_array()
        x_sz = len(x.shape)
        
        if out is None:        
            out = np.zeros_like(x_asarr)
        else:
            out = out.as_array()
            out[:]=0

                  

        ######################## Direct for 2D  ###############################
        if x_sz == 2:
            
            if self.direction == 1:
                
                np.subtract( x_asarr[:,1:], x_asarr[:,0:-1], out = out[:,0:-1] )
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,0], x_asarr[:,-1], out = out[:,-1] )
                else: 
                    raise ValueError('No valid boundary conditions')
                
            if self.direction == 0:
                
                np.subtract( x_asarr[1:], x_asarr[0:-1], out = out[0:-1,:] )

                if self.bnd_cond == 'Neumann':
                    pass                                        
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[0,:], x_asarr[-1,:], out = out[-1,:] ) 
                else:    
                    raise ValueError('No valid boundary conditions') 
                    
        ######################## Direct for 3D  ###############################                        
        elif x_sz == 3:
                    
            if self.direction == 0:  
                
                np.subtract( x_asarr[1:,:,:], x_asarr[0:-1,:,:], out = out[0:-1,:,:] )
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[0,:,:], x_asarr[-1,:,:], out = out[-1,:,:] ) 
                else:    
                    raise ValueError('No valid boundary conditions')                      
                                                             
            if self.direction == 1:
                
                np.subtract( x_asarr[:,1:,:], x_asarr[:,0:-1,:], out = out[:,0:-1,:] ) 
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,0,:], x_asarr[:,-1,:], out = out[:,-1,:] )
                else:    
                    raise ValueError('No valid boundary conditions')                      
                                
             
            if self.direction == 2:
                
                np.subtract( x_asarr[:,:,1:], x_asarr[:,:,0:-1], out = out[:,:,0:-1] ) 
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,:,0], x_asarr[:,:,-1], out = out[:,:,-1] )
                else:    
                    raise ValueError('No valid boundary conditions')  
                    
        ######################## Direct for 4D  ###############################
        elif x_sz == 4:
                    
            if self.direction == 0:                            
                np.subtract( x_asarr[1:,:,:,:], x_asarr[0:-1,:,:,:], out = out[0:-1,:,:,:] )
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[0,:,:,:], x_asarr[-1,:,:,:], out = out[-1,:,:,:] )
                else:    
                    raise ValueError('No valid boundary conditions') 
                                                
            if self.direction == 1:
                np.subtract( x_asarr[:,1:,:,:], x_asarr[:,0:-1,:,:], out = out[:,0:-1,:,:] ) 
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,0,:,:], x_asarr[:,-1,:,:], out = out[:,-1,:,:] )
                else:    
                    raise ValueError('No valid boundary conditions')                 
                
            if self.direction == 2:
                np.subtract( x_asarr[:,:,1:,:], x_asarr[:,:,0:-1,:], out = out[:,:,0:-1,:] ) 
                
                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,:,0,:], x_asarr[:,:,-1,:], out = out[:,:,-1,:] )
                else:    
                    raise ValueError('No valid boundary conditions')                   
                
            if self.direction == 3:
                np.subtract( x_asarr[:,:,:,1:], x_asarr[:,:,:,0:-1], out = out[:,:,:,0:-1] )                 

                if self.bnd_cond == 'Neumann':
                    pass
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,:,:,0], x_asarr[:,:,:,-1], out = out[:,:,:,-1] )
                else:    
                    raise ValueError('No valid boundary conditions')                   
                                
        else:
            raise NotImplementedError                
         
#        res = out #/self.voxel_size 
        return type(x)(out)

                    
    def adjoint(self, x, out=None):
        
        x_asarr = x.as_array()
        x_sz = len(x.shape)
        
        if out is None:        
            out = np.zeros_like(x_asarr)
        else:
            out = out.as_array()        
            out[:]=0

        
        ######################## Adjoint for 2D  ###############################
        if x_sz == 2:        
        
            if self.direction == 1:
                
                np.subtract( x_asarr[:,1:], x_asarr[:,0:-1], out = out[:,1:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[:,0], 0, out = out[:,0] )
                    np.subtract( -x_asarr[:,-2], 0, out = out[:,-1] )
                    
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,0], x_asarr[:,-1], out = out[:,0] )                                        
                    
                else:   
                    raise ValueError('No valid boundary conditions') 
                                    
            if self.direction == 0:
                
                np.subtract( x_asarr[1:,:], x_asarr[0:-1,:], out = out[1:,:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[0,:], 0, out = out[0,:] )
                    np.subtract( -x_asarr[-2,:], 0, out = out[-1,:] ) 
                    
                elif self.bnd_cond == 'Periodic':  
                    np.subtract( x_asarr[0,:], x_asarr[-1,:], out = out[0,:] ) 
                    
                else:   
                    raise ValueError('No valid boundary conditions')     
        
        ######################## Adjoint for 3D  ###############################        
        elif x_sz == 3:                
                
            if self.direction == 0:          
                  
                np.subtract( x_asarr[1:,:,:], x_asarr[0:-1,:,:], out = out[1:,:,:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[0,:,:], 0, out = out[0,:,:] )
                    np.subtract( -x_asarr[-2,:,:], 0, out = out[-1,:,:] )
                elif self.bnd_cond == 'Periodic':                     
                    np.subtract( x_asarr[0,:,:], x_asarr[-1,:,:], out = out[0,:,:] )
                else:   
                    raise ValueError('No valid boundary conditions')                     
                                    
            if self.direction == 1:
                np.subtract( x_asarr[:,1:,:], x_asarr[:,0:-1,:], out = out[:,1:,:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[:,0,:], 0, out = out[:,0,:] )
                    np.subtract( -x_asarr[:,-2,:], 0, out = out[:,-1,:] )
                elif self.bnd_cond == 'Periodic':                     
                    np.subtract( x_asarr[:,0,:], x_asarr[:,-1,:], out = out[:,0,:] )
                else:   
                    raise ValueError('No valid boundary conditions')                                 
                
            if self.direction == 2:
                np.subtract( x_asarr[:,:,1:], x_asarr[:,:,0:-1], out = out[:,:,1:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[:,:,0], 0, out = out[:,:,0] ) 
                    np.subtract( -x_asarr[:,:,-2], 0, out = out[:,:,-1] ) 
                elif self.bnd_cond == 'Periodic':                     
                    np.subtract( x_asarr[:,:,0], x_asarr[:,:,-1], out = out[:,:,0] )
                else:   
                    raise ValueError('No valid boundary conditions')                                 
        
        ######################## Adjoint for 4D  ###############################        
        elif x_sz == 4:                
                
            if self.direction == 0:                            
                np.subtract( x_asarr[1:,:,:,:], x_asarr[0:-1,:,:,:], out = out[1:,:,:,:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[0,:,:,:], 0, out = out[0,:,:,:] )
                    np.subtract( -x_asarr[-2,:,:,:], 0, out = out[-1,:,:,:] )
                    
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[0,:,:,:], x_asarr[-1,:,:,:], out = out[0,:,:,:] )
                else:    
                    raise ValueError('No valid boundary conditions') 
                                
            if self.direction == 1:
                np.subtract( x_asarr[:,1:,:,:], x_asarr[:,0:-1,:,:], out = out[:,1:,:,:] )
                
                if self.bnd_cond == 'Neumann':
                   np.subtract( x_asarr[:,0,:,:], 0, out = out[:,0,:,:] )
                   np.subtract( -x_asarr[:,-2,:,:], 0, out = out[:,-1,:,:] )
                    
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,0,:,:], x_asarr[:,-1,:,:], out = out[:,0,:,:] )
                else:    
                    raise ValueError('No valid boundary conditions') 
                    
                
            if self.direction == 2:
                np.subtract( x_asarr[:,:,1:,:], x_asarr[:,:,0:-1,:], out = out[:,:,1:,:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[:,:,0,:], 0, out = out[:,:,0,:] ) 
                    np.subtract( -x_asarr[:,:,-2,:], 0, out = out[:,:,-1,:] ) 
                    
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,:,0,:], x_asarr[:,:,-1,:], out = out[:,:,0,:] )
                else:    
                    raise ValueError('No valid boundary conditions')                 
                
            if self.direction == 3:
                np.subtract( x_asarr[:,:,:,1:], x_asarr[:,:,:,0:-1], out = out[:,:,:,1:] )
                
                if self.bnd_cond == 'Neumann':
                    np.subtract( x_asarr[:,:,:,0], 0, out = out[:,:,:,0] ) 
                    np.subtract( -x_asarr[:,:,:,-2], 0, out = out[:,:,:,-1] )   
                    
                elif self.bnd_cond == 'Periodic':
                    np.subtract( x_asarr[:,:,:,0], x_asarr[:,:,:,-1], out = out[:,:,:,0] )
                else:    
                    raise ValueError('No valid boundary conditions')                  
                              
        else:
            raise NotImplementedError
            
        out *= -1 #/self.voxel_size
        return type(x)(out)
            
    def range_geometry(self):
        '''Returns the range geometry'''
        return self.gm_range
    
    def domain_geometry(self):
        '''Returns the domain geometry'''
        return self.gm_domain
       
    def norm(self):
        x0 = self.gm_domain.allocate('random_int')
        self.s1, sall, svec = PowerMethodNonsquare(self, 25, x0)
        return self.s1
    
    
if __name__ == '__main__':
    
    from ccpi.framework import ImageGeometry
    import numpy
    
    N, M = 2, 3

    ig = ImageGeometry(N, M)


    FD = FiniteDiff(ig, direction = 1, bnd_cond = 'Neumann')
    u = FD.domain_geometry().allocate('random_int')
        
    res = FD.domain_geometry().allocate()
    res1 = FD.range_geometry().allocate()
    FD.direct(u, out=res)

    z = FD.direct(u)    
#    print(z.as_array(), res.as_array())

    for i in range(10):
#        
        z1 = FD.direct(u) 
        FD.direct(u, out=res)
        
        u = ig.allocate('random_int')
        res = u
        z1  = u
        numpy.testing.assert_array_almost_equal(z1.as_array(), \
                                                res.as_array(), decimal=4)
        
#        print(z1.as_array(), res.as_array())
        z2 = FD.adjoint(z1) 
        FD.adjoint(z1, out=res1)  
        numpy.testing.assert_array_almost_equal(z2.as_array(), \
                                                res1.as_array(), decimal=4)        
        
        
        

        
        
        
    
#    w = G.range_geometry().allocate('random_int')
    

    
    