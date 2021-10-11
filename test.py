import os

os.chdir("C:/Users/HP/Documents/Internship/Data")

import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

# import R's "utils" package
utils = rpackages.importr('utils')
# select a mirror for R packages
utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

# R package names
packnames = ('raster', 'Rcpp')

# Selectively install what needs to be install.
utils.install_packages('rgdal')

raster = rpackages.importr('raster')
r_dem = raster.raster("ahn_dem_voorschoten_clip.tif")
r_dsm = raster.raster("./Outputs/dsm_masked.tif")
resample = robjects.r["resample"]

r_dem_disaggr = resample(r_dem, r_dsm, "bilinear", filename="./Outputs/ahn_dem_resampled_test.tif")

# Plot the data
import matplotlib.pyplot as plt

f, ax = plt.subplots(figsize=(10, 5))
chm.plot(cmap="Greens")
ax.set(title="Canopy Height Model")
ax.set_axis_off()
plt.show()

dem = rxr.open_rasterio("./Outputs/ahn_masked.tif", masked=True).squeeze()
dem = dem[:232, :232]
veg_dsm = rxr.open_rasterio("./Outputs/dsm_masked.tif", masked=True).squeeze()  # different spatial resolution
veg_dsm = veg_dsm[:1160, :1160]
# Downsample the veg map first (band: 1, y: 1160, x: 1160) to (band: 1, y: 232, x: 232) with window 5x5
veg_dsm = veg_dsm.coarsen(x=5).mean().coarsen(y=5).mean()
# veg_dsm = veg_dsm.clip(dem.rio.bounds())

# Check if the images have the same extent, adjust it if needed
print("Is the spatial extent the same?",
      veg_dsm.rio.bounds() == dem.rio.bounds())
# Check if the resolution is the same
print("Is the resolution the same?",
      veg_dsm.rio.resolution() == dem.rio.resolution())

# Compute CHM (dsm - dem)
# regridding from one grid to another (cdo tools, rasterio, gdal, grass) maybe I can do the regridding in ArcGIS
# multidimensional interpolation in scipy


import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

# import R's "utils" package
utils = rpackages.importr('utils')
# select a mirror for R packages
utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

# R package names
packnames = ('raster')

# Selectively install what needs to be install.
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

sf = rpackages.importr('raster')
r_dem = raster.raster("./Outputs/ahn_masked.tif")
r_dsm = raster.raster("./Outputs/dsm_masked.tif")
resample = robjects.r["resample"]

r_dem_disaggr = resample(r_dem, r_dsm, "bilinear", filename="./Outputs/ahn_dem_resampled_test.tif")

chm = veg_dsm.astype(float) - dem.astype(float)
# if the gradient occurs in the final CHMs maybe try to correct it (first the offsets have to
# be determined for every cell, maybe there is some non-linear curvature)
