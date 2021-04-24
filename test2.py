import noisify
from PIL import Image

noiseA = noisify.Perlin(400, 300).Cubify(100)
noiseB = noisify.Perlin(400, 300).Smoothify(8)

imgA = Image.fromarray(255*noiseA).convert("L")
imgB = Image.fromarray(255*noiseB).convert("L")

imgA.show()
imgB.show()

# img.save()