import os
import rasterio
from rasterio.plot import show
import numpy

# Set working directory
os.chdir("C:/Users/HP/Documents/Internship/Data")

# Load the data
with rasterio.open("./temp_heino_RD_clip_feb2020.tif") as src:
    temp = src.read(1)
    temp_meta = src.meta

# Calculate the temperature threshold ( 1,2 or 3 x st. deviation of the temperature)
min = numpy.amin(temp)
avg = numpy.mean(temp)
st_dev = numpy.std(temp)
thr = avg + 2.5 * st_dev

# Apply the temperature threshold on the data. Assign 1 to the heat sources and 0 to the background area.
temp[temp >= thr] = 1
temp[temp < thr] = 0
temp[numpy.isnan(temp)] = float('NaN')
temp[numpy.isinf(temp)] = float('NaN')
show(temp)

# Set spatial characteristics of the output object to mirror the input
temp_meta.update(
    dtype=rasterio.float32,
    count=1)

# Save the results to a new raster.
# Resolution : 0.06597553, 0.06597553
with rasterio.open("D:/Documents/Internship_Drones/Outputs2/heat_sources_heino_2.5sd.tif", "w", **temp_meta) as dest:
    dest.write_band(1, temp.astype(rasterio.float32))




