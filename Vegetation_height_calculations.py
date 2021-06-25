import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

fp = r"C:/Users/HP/Documents/Internship/Data/ortho_voorschoten_RD_clip.tif"

# NDVI calculations

import rasterio
from rasterio.plot import show
import numpy as np

raster = rasterio.open(fp)

red = raster.read(3)
nir = raster.read(5)

np.seterr(divide='ignore', invalid='ignore')
ndvi = np.empty(red.shape, dtype=rasterio.float32)
check = np.logical_or(red > 0.0, nir > 0.0)
part1 = nir - red
part2 = nir + red
raster_ndvi = np.divide(part1, part2)
ndvi = np.where(check, ndvi, -999)
show(ndvi)

if os.path.exists('C:/Users/HP/Documents/Internship/Data/Outputs'):
    print('The directory exists!')
else:
    os.makedirs('C:/Users/HP/Documents/Internship/Data/Outputs')

kwargs = raster.meta
with rasterio.open('C:/Users/HP/Documents/Internship/Data/Outputs/ndvi.tiff', 'w', **kwargs) as ff:
    ff.write(ndvi.astype(rasterio.uint16), indexes = 1)

