#
# 4/8/19
# NOISIFY

"""
Easy to understand Perlin noise generator for python.
"""

# Change Log:

# 4/9/19:
# Finished interpolation issues. want to add to class
# fixed grid x-y issues but still have resolution x-y issues
# temp fix is having grid, res only one number (square)
# Also added octave fractal noise

# 4/13/19:
# Vectorized all components, runs abou ~25x faster than before

# 4/4/21:
# Complete re-write to reduce artifacts

# 4/15/21:
# Realized artifacts were cause entirely by PIL.Image.fromarray(..., 'L')
# don't know why that caused it but turns out noiseV1 worked fine
# Still updated to support better scaling
# SUPER USEFUL !!!!!!
# np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})


# Imports
import math
import numpy as np
from itertools import product


class Perlin:
    """
    2D Perlin Noise
    """
    def __init__(self, res_x, res_y, seed=3):
        self._input_resolution = {"x": res_x, "y": res_y}
        self.SetSeed(seed)

    def Smoothify(self, nodes=8, seed=3):
        self._burn = 0.5
        self.SetSeed(seed)
        self._ReducedArtifactPerlin(nodes, self._burn)
        self._Normalize()
        self._Crop()
        return self.noise

    def Cubify(self, scale=100, seed=3):
        self._scale = scale
        self.SetSeed(seed)
        self._CalculateCells()
        self._CreateNodes()
        self._DistributePixels()
        self._GenerateAngles()
        self._CalculateDistances()
        self._CalculateDotProducts()
        self._Interpolation()
        self._Normalize()
        self._Crop()
        return self.noise

    def _CalculateCells(self):
        self._cells = { "x": math.ceil(self._input_resolution["x"] / self._scale),
                        "y": math.ceil(self._input_resolution["y"] / self._scale)}
        # Working resolution to broadcast easily
        self._resolution = {"x": self._scale * self._cells["x"],
                            "y": self._scale * self._cells["y"]}
        # number of gradient nodes
        self._nodes = { "x": self._cells["x"] + 1,
                        "y": self._cells["y"] + 1}

    def SetSeed(self, seed=3):
        # Setting seed
        self.seed = seed
        np.random.seed(self.seed)

    def _Fade(self, t):
        # Interpolation  function
        # quintic for smooth second derivative, thanks Ken
        return 6*t**5 - 15*t**4 + 10*t**3

    def _CreateNodes(self):
        # Creating node grid
        _node_axis = {  "x": np.arange(self._nodes["x"]),
                        "y": np.arange(self._nodes["y"])}
        _node_xx, _node_yy = np.meshgrid(   _node_axis["x"],
                                            _node_axis["y"])
        self._node_grid = { "xx": _node_xx,
                            "yy": _node_yy}

    def _DistributePixels(self):
        # Creating pixel grid
        _start = {  "x": self._cells["x"] / (2 * self._resolution["x"]),
                    "y": self._cells["y"] / (2 * self._resolution["y"])}
        _stop = {   "x": self._cells["x"] - _start["x"],
                    "y": self._cells["y"] - _start["y"]}
        _pixel_axis = { "x": np.linspace(_start["x"], _stop["x"], self._resolution["x"]),
                        "y": np.linspace(_start["y"], _stop["y"], self._resolution["y"])}
        _pix_xx, _pix_yy = np.meshgrid(_pixel_axis["x"], _pixel_axis["y"])
        # pixel grid has 1 element per pixel whose represents which nodes the pixel belongs to via floor and ceil
        self._pixel_grid = {"xx": _pix_xx, "yy": _pix_yy} 

    def _GenerateAngles(self):
        # Generating gradients for each node
        # switched because of mn order for np arrays
        _angles = 2 * math.pi * np.random.rand(self._nodes["y"], self._nodes["x"])
        # Creating gradient matricies
        stride = self._scale
        self._grad = { # each matrix extends the node-size angle matrix to pixel-size map from pixel->corresponding angle
            "top-left": _angles[:-1, :-1].repeat(stride, 0).repeat(stride, 1),
            "top-right": _angles[:-1, 1:].repeat(stride, 0).repeat(stride, 1),
            "bottom-left": _angles[1:, :-1].repeat(stride, 0).repeat(stride, 1),
            "bottom-right": _angles[1:, 1:].repeat(stride, 0).repeat(stride, 1)
        }

    def _CalculateDistances(self):
        # Calculating distances from corners
        self._dx = { # getting horizontal distance
            "left": self._pixel_grid["xx"] - np.floor(self._pixel_grid["xx"]),
            "right": np.ceil(self._pixel_grid["xx"]) - self._pixel_grid["xx"]
        }
        self._dy = { # getting vertical distance
            "top": self._pixel_grid["yy"] - np.floor(self._pixel_grid["yy"]),
            "bottom": np.ceil(self._pixel_grid["yy"]) - self._pixel_grid["yy"]
        }

    def _CalculateDotProducts(self):
        # Calculating dot product
        self._dot = { 
            "top-left": self._dx["left"] * np.cos(self._grad["top-left"]) + self._dy["top"] * np.sin(self._grad["top-left"]),
            "top-right": self._dx["right"] * np.cos(self._grad["top-right"]) + self._dy["top"] * np.sin(self._grad["top-right"]),
            "bottom-left": self._dx["left"] * np.cos(self._grad["bottom-left"]) + self._dy["bottom"] * np.sin(self._grad["bottom-left"]),
            "bottom-right": self._dx["right"] * np.cos(self._grad["bottom-right"]) + self._dy["bottom"] * np.sin(self._grad["bottom-right"])
        }

    def _Interpolation(self):
        # Interlopating weights for each corner
        influence = {
            "top-left": self._Fade(1 - self._dx["left"]) * self._Fade(1 - self._dy["top"]),
            "top-right": self._Fade(1 - self._dx["right"]) * self._Fade(1 - self._dy["top"]),
            "bottom-left": self._Fade(1 - self._dx["left"]) * self._Fade(1 - self._dy["bottom"]),
            "bottom-right": self._Fade(1 - self._dx["right"]) * self._Fade(1 - self._dy["bottom"])
        }
        # Final noise
        self.noise = (  influence["top-left"] * self._dot["top-left"]
                        + influence["top-right"] * self._dot["top-right"]
                        + influence["bottom-left"] * self._dot["bottom-left"]
                        + influence["bottom-right"] * self._dot["bottom-right"]
        )

    def _Normalize(self):
        # Returns between 0 and 1
        self.noise = (self.noise - np.amin(self.noise)) / (np.amax(self.noise) - np.amin(self.noise))

    def _Crop(self):
        # Crops to input resolution
        # switched because of mn numpy ordering
        self.noise = self.noise[0:self._input_resolution["y"], 0:self._input_resolution["x"]]

    def _ReducedArtifactPerlin(self, nodes=2, burn=.5):
        # Old implementation of noise that has less artifacts (don't know why new one does)
        grid_size = (nodes, nodes)
        # Finds next largest power of two since this algorithm struggles with non-divisible sizes
        max_size = math.pow(2, math.ceil(math.log(max(self._input_resolution["x"], self._input_resolution["y"]))/math.log(2)))
        resolution = (int(max_size), int(max_size))
        delta = resolution[0] // grid_size[0]

        # Cordinate grids
        nodes = (grid_size[0] + 1, grid_size[1] + 1)
        samples = (resolution[0] + 1, resolution[1] + 1)
        x_int = [i for i in range(nodes[0])]
        y_int = [i for i in range(nodes[1] - 1, -1, -1)]
        x = np.linspace(0, grid_size[0], samples[0])
        y = np.linspace(grid_size[1], 0, samples[1])
        # Want y = 0 at bottom of grid
        xx, yy = np.meshgrid(x, y)
        XX, YY = np.meshgrid(x_int, y_int)
        print(XX, YY, xx, yy)

        # Generating random gradients
        angs = 2 * math.pi * np.random.rand(nodes[0], nodes[1])

        # Nodal Matricies
        # Calculates which grid node a pixel belongs to

        # Nodal matrix - X
        x_tl = XX[:-1, :-1].repeat(delta, 0).repeat(delta, 1)
        row = x_tl[resolution[0] - 1]
        x_tl = np.insert(x_tl, resolution[0], row, axis = 0)
        col = x_tl[:, resolution[1] - 1]
        x_tl = np.insert(x_tl, resolution[1], col, axis = 1)

        x_tr = XX[:-1, 1:].repeat(delta, 0).repeat(delta, 1)
        row = x_tr[resolution[0] - 1]
        x_tr = np.insert(x_tr, resolution[0], row, axis = 0)
        col = x_tr[:, 0]
        x_tr = np.insert(x_tr, 0, col, axis = 1)

        x_bl = XX[1:, :-1].repeat(delta, 0).repeat(delta, 1)
        row = x_bl[0]
        x_bl = np.insert(x_bl, 0, row, axis = 0)
        col = x_bl[:, resolution[1] - 1]
        x_bl = np.insert(x_bl, resolution[1], col, axis = 1)

        x_br = XX[1:, 1:].repeat(delta, 0).repeat(delta, 1)
        row = x_br[0]
        x_br = np.insert(x_br, 0, row, axis = 0)
        col = x_br[:, 0]
        x_br = np.insert(x_br, 0, col, axis = 1)

        # Nodal matrix - Y
        y_tl = YY[:-1, :-1].repeat(delta, 0).repeat(delta, 1)
        row = y_tl[resolution[0] - 1]
        y_tl = np.insert(y_tl, resolution[0], row, axis = 0)
        col = y_tl[:, resolution[1] - 1]
        y_tl = np.insert(y_tl, resolution[1], col, axis = 1)

        y_tr = YY[:-1, 1:].repeat(delta, 0).repeat(delta, 1)
        row = y_tr[resolution[0] - 1]
        y_tr = np.insert(y_tr, resolution[0], row, axis = 0)
        col = y_tr[:, 0]
        y_tr = np.insert(y_tr, 0, col, axis = 1)

        y_bl = YY[1:, :-1].repeat(delta, 0).repeat(delta, 1)
        row = y_bl[0]
        y_bl = np.insert(y_bl, 0, row, axis = 0)
        col = y_bl[:, resolution[1] - 1]
        y_bl = np.insert(y_bl, resolution[1], col, axis = 1)

        y_br = YY[1:, 1:].repeat(delta, 0).repeat(delta, 1)
        row = y_br[0]
        y_br = np.insert(y_br, 0, row, axis = 0)
        col = y_br[:, 0]
        y_br = np.insert(y_br, 0, col, axis = 1)

        # Calculating distance
        d_tlx, d_tly = (xx - x_tl), (yy - y_tl)
        d_trx, d_try = (xx - x_tr), (yy - y_tr)
        d_blx, d_bly = (xx - x_bl), (yy - y_bl)
        d_brx, d_bry = (xx - x_br), (yy - y_br)

        # Gradient Matricies
        grad_tl = angs[:-1, :-1].repeat(delta, 0).repeat(delta, 1)
        row = grad_tl[resolution[0] - 1]
        grad_tl = np.insert(grad_tl, resolution[0], row, axis = 0)
        col = grad_tl[:, resolution[1] - 1]
        grad_tl = np.insert(grad_tl, resolution[1], col, axis = 1)

        grad_tr = angs[:-1, 1:].repeat(delta, 0).repeat(delta, 1)
        row = grad_tr[resolution[0] - 1]
        grad_tr = np.insert(grad_tr, resolution[0], row, axis = 0)
        col = grad_tr[:, 0]
        grad_tr = np.insert(grad_tr, 0, col, axis = 1)

        grad_bl = angs[1:, :-1].repeat(delta, 0).repeat(delta, 1)
        row = grad_bl[0]
        grad_bl = np.insert(grad_bl, 0, row, axis = 0)
        col = grad_bl[:, resolution[1] - 1]
        grad_bl = np.insert(grad_bl, resolution[1], col, axis = 1)

        grad_br = angs[1:, 1:].repeat(delta, 0).repeat(delta, 1)
        row = grad_br[0]
        grad_br = np.insert(grad_br, 0, row, axis = 0)
        col = grad_br[:, 0]
        grad_br = np.insert(grad_br, 0, col, axis = 1)

        # Calculating dot product
        dot_tl = d_tlx * np.cos(grad_tl) + d_tly * np.sin(grad_tl)
        dot_tr = d_trx * np.cos(grad_tr) + d_try * np.sin(grad_tr)
        dot_bl = d_blx * np.cos(grad_bl) + d_bly * np.sin(grad_bl)
        dot_br = d_brx * np.cos(grad_br) + d_bry * np.sin(grad_br)

        # Interpolation & Normalization
        def interpolate(t):
            f = 6*t**5 - 15*t**4 + 10*t**3
            return f

        ones = np.ones((samples[0], samples[1]))

        influence_tl = interpolate(ones - abs(d_tlx)) * interpolate(ones - abs(d_tly))
        influence_tr = interpolate(ones - abs(d_trx)) * interpolate(ones - abs(d_try))
        influence_bl = interpolate(ones - abs(d_blx)) * interpolate(ones - abs(d_bly))
        influence_br = interpolate(ones - abs(d_brx)) * interpolate(ones - abs(d_bry))

        # Final noise & normalization
        noise_raw = influence_tl * dot_tl + influence_tr * dot_tr + influence_bl * dot_bl + influence_br * dot_br
        burn_mat = np.ones((samples[0], samples[1]))
        indicies = [[np.array([*product(range(0, samples[0], delta), range(0, samples[1], delta))])]]
        burn_mat[indicies,:] = burn
        burn_mat[:, indicies] = burn
        self.noise = burn_mat * noise_raw