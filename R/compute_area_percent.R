#'@title compute_area_percent
#'@description calculate % of raster area taken by  pixels with particular value in a binary raster
#'@param path path to the raster
#'@param value1 value in the pixels that is equivalent to binary 1
#'@param value0 value in the pixels that is equivalent to binary 0


compute_area_percent <- function(path, value1, value0) {
  
  library(raster)
  library(sp)
  r = raster(path)
  proj4string(r) <- CRS('+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs ')
  
  a_1 = sum(r[]==value1) * res(r)[1]^2
  a_0 = sum(r[]==value0) * res(r)[1]^2
  
  areas = a_1 / (a_1 + a_0) * 100
  
  
  return(areas)
}

