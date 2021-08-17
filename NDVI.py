# Set environmental variables if necessary
import os

os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

import rasterio
from rasterio.plot import show
import numpy
from xrspatial import convolution
from xrspatial import focal
import xarray

fp2 = r"C:/Users/HP/Documents/Internship/Data/ortho_voorschoten_RD_clip.tif"

# Load RED and NIR bands
with rasterio.open(fp2) as src:
    band_red = src.read(3)

with rasterio.open(fp2) as src:
    band_nir = src.read(5)

# Allow division by zero
numpy.seterr(divide='ignore', invalid='ignore')

# Calculate NDVI
ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)
ndvi[ndvi > 1] = 1
ndvi[ndvi < -1] = -1
ndvi[numpy.isnan(ndvi)] = float('NaN')
ndvi[numpy.isinf(ndvi)] = float('NaN')
print(numpy.amax(ndvi), numpy.amin(ndvi))
# show(ndvi)

ndvi_arr = xarray.DataArray(ndvi)
cellsize_x, cellsize_y = convolution.calc_cellsize(ndvi_arr)

# Use an annulus kernel with a ring at a distance of 25-30 cells away from focal point
outer_radius = cellsize_x * 25
kernel = convolution.circle_kernel(cellsize_x, cellsize_y, outer_radius)
ndvi_focal = focal.apply(ndvi_arr, kernel)
show(ndvi_focal)

# Create a binary map of vegetation, where vegetation areas are specified with NDVI higher than 0.22.
veg_map = ndvi_focal.copy()
veg_map.values[veg_map.values > 0.22] = 1
veg_map.values[veg_map.values <= 0.22] = 0

# Set spatial characteristics of the output object to mirror the input
kwargs = src.meta
kwargs.update(
    dtype=rasterio.float32,
    count=1)

# Create the file
with rasterio.open('C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif', 'w', **kwargs) as dst:
    dst.write_band(1, veg_map.astype(rasterio.float32))


# add the comments why I'm using certain functions etc., put a reference to some literature from this field
# perhaps generate a map with some results (check ipyleaflet package - only for jupyter, cartopy)
