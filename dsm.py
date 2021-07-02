import rioxarray as rxr

import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

import matplotlib.pyplot as plt
from rasterio.crs import CRS

fp = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Open the file:
#dsm = rxr.open_rasterio(fp, masked=True).squeeze()

# Check the CRS (now it's 32631)
#print(dsm.rio.crs)

# Create a rasterio crs object for RD new
#crs_rdnew = CRS.from_string('EPSG:28992')
#dsm_proj = dsm.rio.reproject(crs_rdnew)
fp2 = r'C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif'
import gdal
Image = gdal.Open(fp2, 1)  # open image in read-write mode
Band = Image.GetRasterBand(1)
gdal.SieveFilter(srcBand=Band, maskBand=None, dstBand=Band, threshold=8000, connectedness=8, callback=gdal.TermProgress_nocb)
del Image, Band  # close the datasets.


import rasterio
veg_map = rasterio.open("C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif", driver="GTiff")

from shapely.geometry import shape
import rasterio.features

myarray=veg_map.read(1)
mypoly=[]
for vec in rasterio.features.shapes(myarray):
    mypoly.append(shape(vec[0]))

import shapely.geometry as geom
multi_poly = geom.MultiPolygon(mypoly)

from shapely.geometry import mapping, MultiPolygon
import fiona

# Define a polygon feature geometry with one attribute

fn = '/tmp/test_mp.shp'
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {'geometry': 'MultiPolygon', 'properties': {}}
}

with fiona.open(fn, mode='w', **opts) as c:
    c.write({'geometry': {'type': 'MultiPolygon', 'coordinates': multi_poly}, 'properties': {}})

import rasterio.mask

with fiona.open("C:/Users/HP/Documents/Internship/Data/Outputs/water_polygon.shp", "r") as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]

with rasterio.open("C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif", driver="GTiff") as src:
    out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
    out_meta = src.meta

