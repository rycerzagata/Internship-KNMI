#'@title compute_chm
#'@description calculate a Canopy Height Model by subtracting a DTM from a DSM
#'@param dir directory path
#'@param ahn_name filename of the input DTM (derived from AHN3)
#'@param dsm_name filename of the input DSM (derived from drone data)


compute_chm <- function(dir, ahn_name, dsm_name) {
  # params:
  # dir - directory path
  #ahn_name, dsm_name - filenames of the input images
  
  library(raster)
  library(sp)
  setwd(dir)
  r_dtm = raster(ahn_name)
  proj4string(r_dtm) <- CRS('+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs ')
  
  r_dsm = raster(dsm_name)
  proj4string(r_dsm) <- CRS('+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs')
  
  e <- r_dsm@extent
  r_dtm <- extend(r_dtm, e)
  
  r_dsm_resampled <- resample(r_dsm, r_dtm, "bilinear")
  r_dsm_masked <- mask(r_dsm_resampled, r_dtm)
  
  chm = r_dsm_masked - r_dtm
  
  return(chm)
}

