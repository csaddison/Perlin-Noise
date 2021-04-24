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
#
# 4/15/21:
# Realized artifacts were cause entirely by PIL.Image.fromarray(..., 'L')
# don't know why that caused it but turns out noiseV1 worked fine
# Still updated to support better scaling

# Imports
import math
import numpy as np
from PIL import Image
# from itertools import product

# 2D Perlin Noise
# def Perlin(nodes, resolution, seed = 1):

# SUPER USEFUL !!!!!!
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

scale = 100
res_in = (720, 480)
cells = {   "x": math.ceil(res_in[0] / scale),
            "y": math.ceil(res_in[1] / scale)
}
resolution = {"x": scale * cells["x"], "y": scale * cells["y"]} # x,y

# Setting seed
seed = 3
np.random.seed(seed)

# Creating node grid
#number of gradient nodes
nodes = {"x": cells["x"] + 1, "y": cells["y"] + 1}
node_axis = {"x": np.arange(nodes["x"]), "y": np.arange(nodes["y"])}
node_xx, node_yy = np.meshgrid(node_axis["x"], node_axis["y"])
node_grid = {"xx": node_xx, "yy": node_yy}

# Creating pixel grid
start = {"x": cells["x"] / (2 * resolution["x"]),
        "y": cells["y"] / (2 * resolution["y"])}
stop = {"x": cells["x"] - start["x"],
        "y": cells["y"] - start["y"]}

pixel_axis = {  "x": np.linspace(start["x"], stop["x"], resolution["x"]),
                "y": np.linspace(start["y"], stop["y"], resolution["y"])}
pix_xx, pix_yy = np.meshgrid(pixel_axis["x"], pixel_axis["y"])
pixel_grid = {"xx": pix_xx, "yy": pix_yy} # pixel grid has 1 element per pixel whose represents which nodes the pixel belongs to via floor and ceil

# Generating gradients for each node
angles = 2 * math.pi * np.random.rand(nodes["y"], nodes["x"]) # switched because of mn order for np arrays

# Calculating distances from corners
dx = { # getting horizontal distance
    "left": pixel_grid["xx"] - np.floor(pixel_grid["xx"]),
    "right": np.ceil(pixel_grid["xx"]) - pixel_grid["xx"]
}

dy = { # getting vertical distance
    "top": pixel_grid["yy"] - np.floor(pixel_grid["yy"]),
    "bottom": np.ceil(pixel_grid["yy"]) - pixel_grid["yy"]
}

# Creating gradient matricies
delta = scale
grad = { # each matrix extends the node-size angle matrix to pixel-size map from pixel->corresponding angle
    "top-left": angles[:-1, :-1].repeat(delta, 0).repeat(delta, 1),
    "top-right": angles[:-1, 1:].repeat(delta, 0).repeat(delta, 1),
    "bottom-left": angles[1:, :-1].repeat(delta, 0).repeat(delta, 1),
    "bottom-right": angles[1:, 1:].repeat(delta, 0).repeat(delta, 1)
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
    "top-left": interpolate(1 - dx["left"]) * interpolate(1 - dy["top"]),
    "top-right": interpolate(1 - dx["right"]) * interpolate(1 - dy["top"]),
    "bottom-left": interpolate(1 - dx["left"]) * interpolate(1 - dy["bottom"]),
    "bottom-right": interpolate(1 - dx["right"]) * interpolate(1 - dy["bottom"])
}

# Final noise and normalization
noise = (influence["top-left"] * dot["top-left"]
        + influence["top-right"] * dot["top-right"]
        + influence["bottom-left"] * dot["bottom-left"]
        + influence["bottom-right"] * dot["bottom-right"]
)

# noise = influence["top-left"]
noise = (noise - np.amin(noise)) / (np.amax(noise) - np.amin(noise))
noise = 255 * noise[0:res_in[1], 0:res_in[0]]
img = Image.fromarray(noise).convert("L")

# img.save('noise.png')
img.show()