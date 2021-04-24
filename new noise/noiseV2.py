#
# 4/8/19
# NOISE GENERATORS
"""
Generating perlin and fractal noise.
"""
# Change Log:
#
# 4/9/19:
# Finished interpolation issues. want to add to class
# fixed grid x-y issues but still have resolution x-y issues
# temp fix is having grid, res only one number (square)
# Also added octave fractal noise
#
# 4/13/19:
# Vectorized all components, runs abou ~25x faster than before
#
# 4/4/21:
# Complete re-write to reduce artifacts

# Imports
import math
import numpy as np
from PIL import Image
# from itertools import product

# 2D Perlin Noise
# def Perlin(nodes, resolution, seed = 1):

# SUPER USEFUL !!!!!!
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

nodes = 64 # 2 nodes is one cell ==> cells = (nodes-1)
resolution = 256
seed = 3

# Setting seed
np.random.seed(seed)

# Cells between nodes
cells_between = resolution / nodes
cell_size = (nodes - 1) / (resolution + 1) # nodes-1 since cells=nodes-1, res+1 to ensure cutoff before 0/integer value


# Creating node grid
node_axis = np.arange(nodes)
node_xx, node_yy = np.meshgrid(node_axis, node_axis)
node_grid = {"xx": node_xx, "yy": node_yy}

# Creating pixel grid
pixel_axis = np.linspace(cell_size, (nodes-1)-cell_size, resolution)
# pixel_axis = np.arange(start=cell_size, stop=nodes,)
# pixel_axis = np.linspace(0, nodes-1, resolution) # nodes-1 since indexing starts at 0, ends at (nodes-1) inclusive
res_xx, res_yy = np.meshgrid(pixel_axis, pixel_axis)
pixel_grid = {"xx": res_xx, "yy": res_yy} # pixel grid has 1 element per pixel whose represents which nodes the pixel belongs to via floor and ceil

# Generating gradients for each node
# to generate enough for clean edges at the correct resolution we need one more node layer around the outside -> nodes+2
angles = 2 * math.pi * np.random.rand(nodes + 1, nodes + 1)

# Calculating distances from corners
dx = { # getting horizontal distance
    "left": pixel_grid["xx"] - np.floor(pixel_grid["xx"]),
    "right": np.ceil(pixel_grid["xx"]) - pixel_grid["xx"]
}

dy = { # getting vertical distance
    "top": pixel_grid["yy"] - np.floor(pixel_grid["yy"]),
    "bottom": np.ceil(pixel_grid["yy"]) - pixel_grid["yy"]
}

# Shaping gradients
# fixes mismatching shapes of gradients

# Creating gradient matricies
grad = { # each matrix extends the node-size angle matrix to pixel-size map from pixel->corresponding angle
    "top-left": angles[:-1, :-1].repeat(cells_between, 0).repeat(cells_between, 1), # delta+1 because [a].repeat(2)=[a,a]
    "top-right": angles[:-1, 1:].repeat(cells_between, 0).repeat(cells_between, 1),
    "bottom-left": angles[1:, :-1].repeat(cells_between, 0).repeat(cells_between, 1),
    "bottom-right": angles[1:, 1:].repeat(cells_between, 0).repeat(cells_between, 1)
}

# Calculating dot product
dot = { 
    "top-left": dx["left"] * np.cos(grad["top-left"]) + dy["top"] * np.sin(grad["top-left"]),
    "top-right": dx["right"] * np.cos(grad["top-right"]) + dy["top"] * np.sin(grad["top-right"]),
    "bottom-left": dx["left"] * np.cos(grad["bottom-left"]) + dy["bottom"] * np.sin(grad["bottom-left"]),
    "bottom-right": dx["right"] * np.cos(grad["bottom-right"]) + dy["bottom"] * np.sin(grad["bottom-right"])
}

# Interpolation  function
def interpolate(t):
    fade = 6*t**5 - 15*t**4 + 10*t**3 # quintic for smooth second derivative, thanks Ken
    return fade

# Interlopating weights for each corner
influence = {
    "top-left": interpolate(1 - np.absolute(dx["left"])) * interpolate(1 - np.absolute(dy["top"])),
    "top-right": interpolate(1 - np.absolute(dx["right"])) * interpolate(1 - np.absolute(dy["top"])),
    "bottom-left": interpolate(1 - np.absolute(dx["left"])) * interpolate(1 - np.absolute(dy["bottom"])),
    "bottom-right": interpolate(1 - np.absolute(dx["right"])) * interpolate(1 - np.absolute(dy["bottom"]))
}

# Final noise and normalization
noise = (influence["top-left"] * dot["top-left"]
        + influence["top-right"] * dot["top-right"]
        + influence["bottom-left"] * dot["bottom-left"]
        + influence["bottom-right"] * dot["bottom-right"]
)

noise = influence["top-left"]
noise = 255 * np.absolute(noise)
img = Image.fromarray(noise)
img.show()