import os
import rasterio
from rasterio.plot import show
import numpy
from xrspatial import convolution
from xrspatial import focal
import xarray
import gdal

os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

# Set working directory
dir = "C:/Users/HP/Documents/Internship/Data"
os.chdir(dir)

# Path to the multispectral othophoto
fp = r"./ortho_multispectral_heino.tif"

# Load RED and NIR bands
with rasterio.open(fp) as src:
    band_red = src.read(1)

with rasterio.open(fp) as src:
    band_green = src.read(2)

with rasterio.open(fp) as src:
    band_blue = src.read(3)

with rasterio.open(fp) as src:
    band_nir = src.read(5)

# Allow division by zero
numpy.seterr(divide='ignore', invalid='ignore')

# Calculate Excess Green Red (ExGR) index: ExGR=(2×G−R−B)−(1.4×R−G)
exgr = (2 * band_green - band_red - band_blue) - (1.4 * band_red - band_green)
print(numpy.amax(exgr), numpy.amin(exgr))
exgr[numpy.isnan(exgr)] = float('NaN')
exgr[numpy.isinf(exgr)] = float('NaN')
exgr_arr = xarray.DataArray(exgr)
cellsize_x, cellsize_y = convolution.calc_cellsize(exgr_arr)

# Use an annulus kernel with a ring at a distance of 25-30 cells away from focal point to smoothen the image
outer_radius = cellsize_x * 25
inner_radius = cellsize_x * 1
kernel = convolution.circle_kernel(cellsize_x, cellsize_y, outer_radius)
exgr_focal = focal.apply(exgr_arr, kernel)

veg_map = exgr_focal.copy()
veg_map.values[veg_map.values > 0] = 1
veg_map.values[veg_map.values <= 0] = 0
show(veg_map)

## Calculate NDVI ##
ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)
# ndvi[ndvi > 1] = float('NaN')
# ndvi[ndvi < -1] = float('NaN')
ndvi[ndvi > 1] = 1
ndvi[ndvi < -1] = -1
ndvi[numpy.isnan(ndvi)] = float('NaN')
ndvi[numpy.isinf(ndvi)] = float('NaN')
# print(numpy.amax(ndvi), numpy.amin(ndvi))
show(ndvi)

ndvi_arr = xarray.DataArray(ndvi)
cellsize_x, cellsize_y = convolution.calc_cellsize(ndvi_arr)

# Use an annulus kernel with a ring at a distance of 25-30 cells away from focal point to smoothen the image
outer_radius = cellsize_x * 10
inner_radius = cellsize_x * 1
kernel = convolution.circle_kernel(cellsize_x, cellsize_y, outer_radius)
ndvi_focal = focal.apply(ndvi_arr, kernel)

veg_map = ndvi_focal.copy()
veg_map.values[veg_map.values > 0.22] = 1
veg_map.values[veg_map.values <= 0.22] = 0

# Set spatial characteristics of the output object to mirror the input
kwargs = src.meta
kwargs.update(
    dtype=rasterio.float32,
    count=1)

# Create the file
veg = r'C:/Users/HP/Documents/Internship/Data/Outputs/veg_map_ndvi_test.tif'
with rasterio.open(veg, 'w', **kwargs) as dst:
    dst.write_band(1, veg_map.astype(rasterio.float32))

# Remove the small clumps of pixels from the map of vegetation.
# The threshold is set to 1000 pixels to make the code execution shorter for tests.
vegetation = gdal.Open(veg, 1)  # open image in read-write mode
band = vegetation.GetRasterBand(1)
gdal.SieveFilter(srcBand=band, maskBand=None, dstBand=band, threshold=1000,
                 connectedness=8, callback=gdal.TermProgress_nocb)
del vegetation, band  # Close the datasets
