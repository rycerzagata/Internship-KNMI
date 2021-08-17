import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

# '@title import BGT
# '@description download BGT dataset to storage memory
# '@param name of AWS or location
# '@param spatialpoint single sf point in RD new coordinates
# '@param radius Default 150. Set radius distance in metres
# '@author Jelle Stuurman

with open('C:/Users/HP/Documents/Internship/R/import_BGT.R', 'r') as f:
    r_script = f.read()

robjects.r(r_script)
r_f = robjects.r['import_single_bgt']

print(r_f.r_repr())

# import R's "utils" package
utils = rpackages.importr('utils')
# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# R package names
packnames = ('raster', 'sf')

# R vector of strings
from rpy2.robjects.vectors import StrVector

# Selectively install what needs to be install.
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

sf = rpackages.importr('sf')
r = robjects.r
coord_vect = robjects.IntVector([89934,461788])
point = robjects.r['st_point'](coord_vect)

bgt_data = r_f(name ='Voorschoten', spatialpoint= point, radius=150))