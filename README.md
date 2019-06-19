# Random Noise Generation

After failing to find a succient and readable Perlin noise algorithm in Python, I decided to create my own. This goes over the differences between Perlin noise and random noise, as well as document the imporvements I've tried to make to my original algorithm with the power of vectorized functions.

### Using the script

Simply run:

```python
import noise # Both functions output a square array of noisy values normalized from 0-255
noise = noise.Perlin(scale, resolution, seed)
fractal_noise = noise.Octave(resolution, num_of_octaves, major_grid_scale, falloff, seed)
```

Note that when using the octave/fractal noise function, the `major_grid_scale` (formally called lacunarity) determines in part your resolution. The resolution needs to be evenly divisible by <img src="/tex/74920a21ad9ca2304a56637775b57408.svg?invert_in_darkmode&sanitize=true" align=middle width=121.00806959999998pt height=26.085962100000025pt/>. Typically is you make both the lacunarity and resolution powers of 2 there will be no issue.

### Random noise

<p id="img_cont">
    <img src="images/noise.jpg" width="250">
    <img src="images/perlin.png"  width="250">
    <img src="images/octaves.png" width="250">
</p>

_Above: the differences between random/white noise (left), Perlin noise (center), and Perlin noise with multiple octaves (right)._

True random noise is the simplest form of noise, but it's surprisingly useless for many circumstances. It has its moments--[like simulating raindrops in my hydraulic erosion simulation](https://github.com/csaddison/Hydraulic-Erosion-Sim)--but for many applications a better choice of distribution or noise algorithm yields more accurate results.

The problem is that many natural phenomena have smooth, continuous changes. They're well-behaved processes: a small shift in the intput results in a small shift in the output: <img src="/tex/317c428157ea5401d253364efdeab852.svg?invert_in_darkmode&sanitize=true" align=middle width=139.4404638pt height=24.65753399999998pt/>. Random noise usually has large jumps when moving even a single pixel or other unit. However, it is incredibly easy to implement:

``` python
import numpy as np
noise = 255 * np.random.rand(y_dimension, x_dimension)
```

The prefactor of 255 is used as a convention to create a standard 8-bit image (<img src="/tex/ce82da62b6001e63352bd7417ce34dc1.svg?invert_in_darkmode&sanitize=true" align=middle width=62.16892769999999pt height=26.76175259999998pt/>).

### Perlin noise

_Note: all images in this section are created by Matthewslf and taken from the Wikimedia Commons under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0)._

<img src="images/grid.png" width="400">

_Above: the grid structure of gradients._

[Perlin noise](https://en.wikipedia.org/wiki/Perlin_noise) was developed in 1983 by Ken Perlin and takes into account the value of neighboring points to create smooth, undulating patterns. This works by assigning a vector direction to a large underlying grid of lattice points. The number of grid nodes inversely corresponds with the scale of the noise--a higher grid count leads to smaller scaled noise.

<img src="images/dot.png"  width="400">

_Above: dot products of displacement and gradient vectors._

Then, for every pixel in a cell the algorithm creates a displacement vector between the pixel and the nearest node. It then calculates the dot product of this displacement vector with the the gradient vector of the nearest node.

<img src="images/interp.png" width="400">

_Above: values after interpolation._

It then interpolates between adjacent the results, creating smooth transitions between nodes. There are many possible interpolation equations: linear, cubic, sigmoid... the list goes on. The Perlin algorithm uses a quintic interpolation function to avoid artifacts between cells. This is accomplished by requiring the first and second derivatives of the function to vanish at <img src="/tex/06f0fc35b3cd0554a7129a42668d63b8.svg?invert_in_darkmode&sanitize=true" align=middle width=55.05692114999999pt height=21.18721440000001pt/> so that a constant rate of change of value is achieved:

<p align="center"><img src="/tex/c8b1bbc6cdd7bb403b2f77aa67e6c2b6.svg?invert_in_darkmode&sanitize=true" align=middle width=184.68032549999998pt height=18.312383099999998pt/></p>

Taking the first and second derivative of this, it is clear that <img src="/tex/8e22a5cca9f72debe6db460baab1a228.svg?invert_in_darkmode&sanitize=true" align=middle width=245.20536809999996pt height=24.7161288pt/>. That's all that's required to create Perlin noise--one downside of this algorithm is that the node points themselves always have a dot product of zero, which in a range of -1 to 1 means that each node point is always exactly 50% grey. Similar algorithms have been proposed with improvements, most notably [Simplex noise](https://en.wikipedia.org/wiki/Simplex_noise) which is considerably cheaper to render in higher dimensions: <img src="/tex/c5566036dd2bd924fef1c6263072eb45.svg?invert_in_darkmode&sanitize=true" align=middle width=43.570210199999984pt height=26.76175259999998pt/> for Simplex versus <img src="/tex/b6bfbd54b6a9a67666c982b5453df90f.svg?invert_in_darkmode&sanitize=true" align=middle width=53.36289749999998pt height=24.65753399999998pt/> for Perlin.

### Multi-octave noise

Multi-octave Perlin noise, commonly called fractal noise, involves simply rescaling and adding Perlin noise to itself iteratively. Each iteration, called an octave, is rescaled exponentially and added to the previous octave with a reduced weight (called the persistance of the octave). The grid size of the first octave is referred to as the lacunarity and the grid size of subsequent octaves is <img src="/tex/8c44609931889cbb7c6dbc4b4d4a1262.svg?invert_in_darkmode&sanitize=true" align=middle width=33.72354974999999pt height=22.831056599999986pt/> for the <img src="/tex/ae7647a25a2e7d1d8719abc7aa16dc35.svg?invert_in_darkmode&sanitize=true" align=middle width=22.528695749999986pt height=27.91243950000002pt/> octave. Generally, keeping the lacunarity as a power of 2 works well, especially for resolutions common to texture maps (512x512, 1024x1024, etc.).

### The power of vectorization

Originally I had written this program using nested for-loops, looping over every grid point as well as every pixel. This was excruciatingly slow with large grids and high resolutions. After learning about vectorizing functions in numpy I realized this could be sped up considerably. After vectorization the script runs ~30x faster than before.