import os
import rasterio
from rasterio.features import shapes
from rasterio.mask import mask
from rasterio.plot import show
import fiona
import geopandas as gp
from fiona.crs import from_epsg
import shapely.geometry as geom
import rioxarray as rxr

os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'
os.chdir("C:/Users/HP/Documents/Internship/Data")

# Set a path to the CHM (created using script chm.py) and vegetation map
chm = r"./Outputs/chm_test.tif"
veg = r'./Outputs/vegetation.tif'  # Path to the vegetation map

# Create a rasterio crs object for RD new.
rd_new = from_epsg(28992)  # That's the correct projection
#chm_proj = chm.rio.reproject(rd_new)

# Read the map of vegetation as an array and transform it into a list of polygons
with rasterio.open(veg, driver="GTiff") as src:
    my_array = src.read(1)

img = rasterio.open(veg, driver="GTiff")  # img will be used to copy the transform argument (see below)

my_vec = []
my_poly = []

for vec in shapes(my_array, transform=img.transform):
    my_vec.append(vec[1])
    my_poly.append(geom.shape(vec[0]))

# Define a polygon feature geometry with two attributes: polygon id and value.
opts = {
    'driver': 'ESRI Shapefile',
    'schema': {
        'geometry': '3D Polygon',
        'properties': {'id':'int','value':'int'}
    }
}

# Create a shapefile with the polygons from the list
fn = r'./Outputs/test_poly.shp'
with fiona.open(fn, mode='w', **opts, crs=rd_new) as output:
    for i, poly in enumerate(my_poly):
        output.write({'geometry': geom.mapping(poly),
                      'properties': {'id': i, 'value': my_vec[i]}})

polygons_gdf = gp.read_file("./Outputs/test_poly.shp")
veg_poly = polygons_gdf[polygons_gdf['value'] > 0]

with rasterio.open(chm, driver="GTiff") as src:
    out_image, out_transform = mask(src, veg_poly.geometry, invert=False, crop=True)
    out_meta = src.meta

out_image = out_image.squeeze()

# Update the metadata of the image.
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[0],
                 "width": out_image.shape[1],
                 "transform": out_transform})

# Save the results to a new raster.
with rasterio.open("./Outputs/chm_masked.tif", "w", **out_meta) as dest:
    dest.write_band(1, out_image.astype(rasterio.float32))

#show(out_image)

# change the values in dsm to remove the offsets, mask the chm instead of dsm

# ADDITIONAL
# Another way to clip the CHM.
chm_raster = rxr.open_rasterio(chm)
chm_clipped = chm_raster.rio.clip(veg_poly.geometry.apply(geom.mapping))

# You can compute the maximum value of vegetation height using rasterstats package.
from rasterstats import zonal_stats
stats = zonal_stats("./Outputs/test_poly.shp", chm, stats="count mean max")

