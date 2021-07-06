import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

import gdal
import rasterio
from rasterio.features import shapes
from rasterio.mask import mask
import fiona
from fiona.crs import from_epsg
import shapely.geometry as geom

# This is the path to the DSM.
# dsm = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Create a rasterio crs object for RD new.
#crs_rdnew = CRS.from_string('EPSG:28992') # That's the correct projection
#dsm_proj = dsm.rio.reproject(crs_rdnew)


# Remove the small clumps of pixels from the map of vegetation.
# The threshold is set to 1000 pixels to make the code execution shorter for now.
fp = r'C:/Users/HP/Documents/Internship/Data/Outputs/vegetation.tif'  # Path to the vegetation map
vegetation = gdal.Open(fp, 1)  # open image in read-write mode
band = vegetation.GetRasterBand(1)
gdal.SieveFilter(srcBand=band, maskBand=None, dstBand=band, threshold=1000,
                 connectedness=8, callback=gdal.TermProgress_nocb)
del vegetation, band  # Close the datasets

# Read the map of vegetation as an array and transform it into a list of polygons.
with rasterio.open(fp, driver="GTiff") as src:
    my_array = src.read(1)

img = rasterio.open(fp, driver="GTiff") # will be used to copy the transform argument below

my_poly = []
for vec in shapes(my_array, transform=img.transform):
    my_poly.append(geom.shape(vec[0]))

# Define a polygon feature geometry with one attribute (ideally two attributes: id and value).
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {
        'geometry': '3D Polygon',
        'properties': {'id':'int'}
    }
}

# Create a shapefile with the polygons from the list.
fn = r'C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp'
with fiona.open(fn, mode='w', **opts, crs=from_epsg(28992)) as output:
    for i, poly in enumerate(my_poly):
        output.write({'geometry': geom.mapping(poly),
                      'properties': {'id': i}})

# Apply the features in the shapefile as a mask on the raster.
with fiona.open("C:/Users/HP/Documents/Internship/Data/Outputs/test_poly.shp", "r") as shapefile:
    polygons = [feature["geometry"] for feature in shapefile]

with rasterio.open("C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif", driver="GTiff") as src:
    out_image, out_transform = mask(src, polygons, invert=True)
    out_meta = src.meta

# Update the metadata of the image.
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

# Save the results to a new raster.
with rasterio.open("C:/Users/HP/Documents/Internship/Data/Outputs/dsm_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)
