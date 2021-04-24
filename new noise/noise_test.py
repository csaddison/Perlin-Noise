# Fixing broken noise
# 4/4/21

import numpy as np
from PIL import Image
import noiseV1
import noisify

# perl = noiseV1.Perlin(8,256)
# img = Image.fromarray(perl)
# # img.save('noise.png')
# img.show()

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

###############################################################

def generate_perlin_noise_2d(shape, res):
    def f(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1,1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:,1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0], grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)


# perl = generate_perlin_noise_2d([128,128], [64,64])
# img = Image.fromarray(perl)
# # img.save('noise.png')
# img.show()
# print(perl)


# import noise
# import numpy as np
# from scipy.misc import toimage

# shape = (1024,1024)
# scale = 100.0
# octaves = 1
# persistence = 0.5
# lacunarity = 2.0

# world = np.zeros(shape)
# for i in range(shape[0]):
#     for j in range(shape[1]):
#         world[i][j] = noise.pnoise2(i/scale, 
#                                     j/scale, 
#                                     octaves=octaves, 
#                                     persistence=persistence, 
#                                     lacunarity=lacunarity, 
#                                     repeatx=1024, 
#                                     repeaty=1024, 
#                                     base=0)
        
# toimage(world).show()



# var = {"x": , "y": }