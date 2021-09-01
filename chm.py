import os
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

dir = "C:/Users/HP/Documents/Internship/Data"
ahn_fp = "ahn_dem_voorschoten_clip.tif"
dsm_fp = "dsm_voorschoten_RD_clip.tif"
os.chdir(dir)

with open('C:/Users/HP/Documents/Internship/R/compute_chm.R', 'r') as f:
    r_script = f.read()

robjects.r(r_script)
r_f = robjects.r['compute_chm']
print(r_f.r_repr())

# Import R's "utils" package
utils = rpackages.importr('utils')

# Select a mirror for R packages
utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

chm_r = r_f(dir, ahn_fp, dsm_fp)

# Selectively install what needs to be install.
# utils.install_packages('raster')

# Save the CHM to a GTiff file
raster = rpackages.importr('raster')
raster.writeRaster(chm_r, "./Outputs/chm_test.tif", format = "GTiff", overwrite = True)


