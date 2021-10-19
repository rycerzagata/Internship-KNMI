# Internship - Evaluating the potential of surveying drones for station inspection and optimizing automated siting classification methods

## Contents:
1. Vegetation height  
   a) find_vegetation.py - a script determining the presence vegetation using vegetation indices  
   b) chm.py - computes the height of the vegetation at the location of the air temperature sensor using the map of vegetation and a DSM  
   c) update_chm.py - mask the non-vegetation areas from CHM using vegetation polygons  
   
2. Shadow angles   
   b) max_elevation_values.py - find the elevation values for every azimuth around the image origin, calculate sun angles and plot the results on a sun chart  
   c) test_max_elevation_values.py - unit tests for the functions in the previous script  
   
3. Presence of heat sources and water bodies  
   a) water_bodies.py - find water bodies using NDWI index applied to a multispectral image  
   b) heat_sources_thresholds.py - plot the relationship between the area of a heat source and the threshold value  
   c) heat_sources_from_temp_map.py - find heat sources using a threshold temperature value  
 
4. R - folder with functions written in R that are called in the abovementioned scripts  
   a) compute_area_percent.R - calculate % of raster area taken by  pixels with particular value in a binary map  
   b) compute_chm.R - calculate a Canopy Height Model by subtracting a DTM from a DSM  
