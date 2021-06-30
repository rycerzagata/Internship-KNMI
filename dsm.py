import rioxarray as rxr

import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.crs import CRS
import earthpy as et

fp = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Open the file:
dsm = rxr.open_rasterio(fp2, masked=True).squeeze()

# Check type of the variable 'dsm'
print(type(dsm))

# Check the CRS (now it's 32631)
dsm.rio.crs

# Create a rasterio crs object for RD new
crs_rdnew = CRS.from_string('EPSG:28992')
dsm_proj = dsm.rio.reproject(crs_rdnew)

# Plot your newly converted data
f, ax = plt.subplots(figsize=(10, 4))

dsm_proj.plot.imshow(ax=ax, cmap='Greys')

ax.set(title="Plot")
ax.set_axis_off()
plt.show()

import gdal
Image = gdal.Open('SomeImageName.tif', 1)  # open image in read-write mode
Band = Image.GetRasterBand(1)
gdal.SieveFilter(srcBand=Band, maskBand=None, dstBand=Band, threshold=100, connectedness=8, callback=gdal.TermProgress_nocb)
del Image, Band  # close the datasets.


