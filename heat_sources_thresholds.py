# importing the required modules
import matplotlib.pyplot as plt
import os
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

dir = "D:/Documents/Internship_Drones/Outputs2"
fp05 = "heat_sources_heino_0.5sd.tif"
fp10 = "heat_sources_heino_1sd.tif"
fp15 = "heat_sources_heino_1.5sd.tif"
fp20 = "heat_sources_heino_2sd.tif"
fp25 = "heat_sources_heino_2.5sd.tif"
fp30 = "heat_sources_heino_3sd.tif"
fp35 = "heat_sources_heino_3.5sd.tif"
fp40 = "heat_sources_heino_4sd.tif"
os.chdir(dir)

with open('C:/Users/HP/Documents/Internship/R/compute_area_percent.R', 'r') as f:
    r_script = f.read()

robjects.r(r_script)
r_f = robjects.r['compute_area_percent']
print(r_f.r_repr())

# Import R's "utils" package
utils = rpackages.importr('utils')
# Select a mirror for R packages
utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

area05 = r_f(path=fp05, value1=1, value0=0)
area10 = r_f(path=fp10, value1=1, value0=0)
area15 = r_f(path=fp15, value1=1, value0=0)
area20 = r_f(path=fp20, value1=1, value0=0)
area25 = r_f(path=fp25, value1=1, value0=0)
area30 = r_f(path=fp30, value1=1, value0=0)
area35 = r_f(path=fp35, value1=1, value0=0)
area40 = r_f(path=fp40, value1=1, value0=0)

# x axis values
x = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
# corresponding y axis values
y = [area05, area10, area15, area20, area25, area30, area35, area40]

# Plotting
plt.plot(x, y)
# Naming the x and y axis
plt.xlabel('Temperature threshold (x * st dev)')
plt.ylabel('Percent of area of the image taken by heat sources')
# Giving a title to the graph
plt.title('Relationship between area and temperature threshold')
# Function to show the plot
plt.show()