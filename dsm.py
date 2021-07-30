import os
os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'
os.chdir("C:/Users/HP/Documents/Internship/Data")

import gdal
import rasterio
from rasterio.features import shapes
from rasterio.mask import mask
import fiona
from fiona.crs import from_epsg
import shapely.geometry as geom

# This is the path to the DSM.
dsm = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"

# Create a rasterio crs object for RD new.
#crs_rdnew = CRS.from_string('EPSG:28992') # That's the correct projection
#dsm_proj = dsm.rio.reproject(crs_rdnew)


# Remove the small clumps of pixels from the map of vegetation.
# The threshold is set to 1000 pixels to make the code execution shorter for now.
fp = r'./Outputs/vegetation.tif'  # Path to the vegetation map
vegetation = gdal.Open(fp, 1)  # open image in read-write mode
band = vegetation.GetRasterBand(1)
gdal.SieveFilter(srcBand=band, maskBand=None, dstBand=band, threshold=1000,
                 connectedness=8, callback=gdal.TermProgress_nocb)
del vegetation, band  # Close the datasets

# Read the map of vegetation as an array and transform it into a list of polygons.
with rasterio.open(fp, driver="GTiff") as src:
    my_array = src.read(1)

img = rasterio.open(fp, driver="GTiff") # will be used to copy the transform argument below

my_vec = []
my_poly = []
for vec in shapes(my_array, transform=img.transform):
    my_vec.append(vec[1])
    my_poly.append(geom.shape(vec[0]))


# Define a polygon feature geometry with one attribute (ideally two attributes: id and value).
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {
        'geometry': '3D Polygon',
        'properties': {'id':'int','value':'int'}
    }
}

# Create a shapefile with the polygons from the list.
fn = r'./Outputs/test_poly.shp'
with fiona.open(fn, mode='w', **opts, crs=from_epsg(28992)) as output:
    for i, poly in enumerate(my_poly):
        output.write({'geometry': geom.mapping(poly),
                      'properties': {'id': i, 'value': my_vec[i]}})

# Apply the features in the shapefile as a mask on the raster.
#with fiona.open("./Outputs/test_poly.shp", "r") as shapefile:
   # polygons = [feature['geometry'] for feature in shapefile]
# ??????? czy to potrzebne^

import geopandas as gp
polygons_gdf = gp.read_file("./Outputs/test_poly.shp")
veg_poly = polygons_gdf[polygons_gdf['value'] > 0]


with rasterio.open(dsm, driver="GTiff") as src:
    out_image, out_transform = mask(src, veg_poly.geometry, invert=False)
    out_meta = src.meta

# Update the metadata of the image.
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

# Save the results to a new raster.
with rasterio.open("./Outputs/dsm_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)


import rioxarray as rxr
dem = rxr.open_rasterio("ahn_dem_voorschoten_clip.tif")
veg_dsm = rxr.open_rasterio("./Outputs/dsm_masked_clip.tif")
veg_dsm.rio.bounds()
dem.rio.bounds()
chm = veg_dsm - dem
from rasterio.plot import show
show(chm)

# ADDITIONAL
# Another way to clip the DSM.
import rioxarray as rxr
dsm_raster = rxr.open_rasterio(dsm)
dsm_clipped = dsm_raster.rio.clip(veg_poly.geometry.apply(geom.mapping))


# You can compute the maximum value of vegetation height using rasterstats package.
from rasterstats import zonal_stats
stats = zonal_stats("./Outputs/test_poly.shp", "dsm_voorschoten_RD_clip.tif",
            stats="count mean max")

