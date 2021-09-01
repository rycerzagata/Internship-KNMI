# Internship - Evaluating the potential of surveying drones for station inspection and optimizing automated siting classification methods

## Contents:
1. find_vegetation.py - a script determining the presence vegetation using vegetation indices
2. chm.py - computes the height of the vegetation at the location of the air temperature sensor using the map of vegetation and a DSM
3. update_chm.py - mask the non-vegetation areas from CHM using vegetation polygons
4. sun_angles.py - calculate sun angles 
5. max_elevation_values.py - find the elevation values for every azimuth around the image origin
6. test_max_elevation_values.py - unit tests for the functions in the previous script
7. water_bodies.py - find water bodies using NDWI index applied to a multispectral image
8. heat_sources_thresholds.py - plot the relationship between the area of a heat source and the threshold value
9. heat_sources_from_temp_map.py - find heat sources using a threshold temperature value
10. R - folder with functions written in R that are called in the abovementioned scripts
