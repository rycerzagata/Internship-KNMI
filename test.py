

import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

# NDVI calculations

import rasterio
from rasterio.plot import show
import numpy

fp2 = r"C:/Users/HP/Documents/Internship/Data/ortho_voorschoten_RD_clip.tif"

# Load red and NIR bands
with rasterio.open(fp2) as src:
    band_red = src.read(3)

with rasterio.open(fp2) as src:
    band_nir = src.read(5)

# Allow division by zero
numpy.seterr(divide='ignore', invalid='ignore')

# Calculate NDVI
ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

# Set spatial characteristics of the output object to mirror the input
kwargs = src.meta
kwargs.update(
    dtype=rasterio.float32,
    count = 1)

# Create the file
with rasterio.open('C:/Users/HP/Documents/Internship/Data/Outputs/ndvi.tif', 'w', **kwargs) as dst:
        dst.write_band(1, ndvi.astype(rasterio.float32))

