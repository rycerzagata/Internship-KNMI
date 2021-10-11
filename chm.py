import os
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

dir = "D:/Documents/Internship_Drones/Data2"
ahn_fp = "AHN_DTM_Heino.tif"
dsm_fp = "DSM_Heino_feb2021.tif"
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

# Selectively install what needs to be installed.
# utils.install_packages('raster')

# Save the CHM to a GTiff file
raster = rpackages.importr('raster')
raster.writeRaster(chm_r, "D:/Documents/Internship_Drones/Outputs2/chm_heino.tif", format="GTiff", overwrite=True)
