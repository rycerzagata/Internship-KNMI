import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

fp = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Create a rasterio crs object for RD new
#crs_rdnew = CRS.from_string('EPSG:28992')
#dsm_proj = dsm.rio.reproject(crs_rdnew)

fp2 = r'C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif'
import gdal
Image = gdal.Open(fp2, 1)  # open image in read-write mode
Band = Image.GetRasterBand(1)
gdal.SieveFilter(srcBand=Band, maskBand=None, dstBand=Band, threshold=1000, connectedness=8, callback=gdal.TermProgress_nocb)
del Image, Band  # close the datasets.

import rasterio
with rasterio.open(fp2, driver="GTiff") as src:
    myarray = src.read(1)

veg = rasterio.open(fp2, driver="GTiff")



from shapely.geometry import shape
import rasterio.features
mypoly=[]
for vec in rasterio.features.shapes(myarray, transform= veg.transform):
    mypoly.append(shape(vec[0]))

import shapely.geometry as geom
multi_poly = geom.MultiPolygon(mypoly)



import fiona
from fiona.crs import from_epsg
# Define a polygon feature geometry with one attribute
fn = r'C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp'
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {'geometry': 'MultiPolygon', 'properties': {}}
}

with fiona.open(fn, mode='w', **opts, crs=from_epsg(28992)) as c:
    c.write({'geometry': geom.mapping(multi_poly), 'properties': {}})

import rasterio.mask

with fiona.open("C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp", "r") as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]


with rasterio.open("C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif", driver="GTiff") as src:
    out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
    out_meta = src.meta

out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

with rasterio.open("C:/Users/HP/Documents/Internship/Data/Outputs/dsm_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)


