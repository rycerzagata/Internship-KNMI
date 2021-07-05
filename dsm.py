import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

# This is the path to the DSM.
dsm = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Create a rasterio crs object for RD new
#crs_rdnew = CRS.from_string('EPSG:28992') --- that's the correct projection
#dsm_proj = dsm.rio.reproject(crs_rdnew)

# Remove the small clumps of pixels from the map of vegetation. The threshold is set to 1000 pixels just for the testing phase.
fp2 = r'C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif' # path to the vegetation map derived using a threshold on NDVI values
import gdal
Image = gdal.Open(fp2, 1)  # open image in read-write mode
Band = Image.GetRasterBand(1)
gdal.SieveFilter(srcBand=Band, maskBand=None, dstBand=Band, threshold=1000, connectedness=8, callback=gdal.TermProgress_nocb)
del Image, Band  # close the datasets.

# Read the map of vegetation anf transform it into a list of polygons.
import rasterio
with rasterio.open(fp2, driver="GTiff") as src:
    myarray = src.read(1)

veg = rasterio.open(fp2, driver="GTiff")

from shapely.geometry import shape
import rasterio.features
mypoly=[]
for vec in rasterio.features.shapes(myarray, transform= veg.transform):
    mypoly.append(shape(vec[0]))

#
import fiona
from fiona.crs import from_epsg
import shapely.geometry as geom

# Define a polygon feature geometry with one attribute
fn = r'C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp'
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {'geometry': '3D Polygon', 'properties': {'test':'int'}}
}

# Create a shapefile
with fiona.open(fn, mode='w', **opts, crs=from_epsg(28992)) as output:
    for i,poly in enumerate(mypoly):
        output.write({'geometry': geom.mapping(poly), 'properties':{'test':i}})

# Apply the features in the shapefile as a mask on the raster.
import rasterio.mask
with fiona.open("C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp", "r") as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]

with rasterio.open("C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif", driver="GTiff") as src:
    out_image, out_transform = rasterio.mask.mask(src, shapes, invert=True)
    out_meta = src.meta

# Update the metadata of the image.
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

# Save the results to a new raster.
with rasterio.open("C:/Users/HP/Documents/Internship/Data/Outputs/dsm_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)


