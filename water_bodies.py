import os
import rasterio
from rasterio.plot import show
import numpy

os.chdir("C:/Users/HP/Documents/Internship/Data")

fp = r"./ortho_multispectral_heino.tif"

# Load GREEN and NIR bands
with rasterio.open(fp) as src:
    band_green = src.read(2)

with rasterio.open(fp) as src:
    band_nir = src.read(5)

with rasterio.open(fp) as src:
    band_red = src.read(1)

# NDWI = (Green - NIR) / (Green + NIR)
# or... NDWI = (Red - NIR) / (Red + NIR)

# Allow division by zero
numpy.seterr(divide='ignore', invalid='ignore')

# Calculate NDWI
ndwi = (band_red.astype(float) - band_nir.astype(float)) / (band_nir + band_red)
#print(numpy.amax(ndwi), numpy.amin(ndwi))
ndwi[numpy.isnan(ndwi)] = float('NaN')
ndwi[numpy.isinf(ndwi)] = float('NaN')

ndwi[ndwi >= 0.3] = 1
ndwi[ndwi < 0.3] = 0

show(ndwi)

# Set spatial characteristics of the output object to mirror the input
kwargs = src.meta
kwargs.update(
    dtype=rasterio.float32,
    count=1)

# Create the file
with rasterio.open('C:/Users/HP/Documents/Internship/Data/Outputs/water_bodies_heino_red.tif', 'w', **kwargs) as dst:
    dst.write_band(1, ndwi.astype(rasterio.float32))