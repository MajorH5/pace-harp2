import os
import numpy as np
import rasterio

from rasterio.transform import from_gcps, from_origin, xy
from rasterio.control import GroundControlPoint as GCP
from pyresample import image, geometry, kd_tree
from netCDF4 import Dataset
from nasa_pace_data_reader import L1, plot

def resampleData(source_lats, source_lons, target_lats, target_lons,
                 source_data, max_radius, method = 'kd_tree_gauss',
                 *args):
    '''
   

    Parameters
    ----------
    source_lats : TYPE
        Source latitude.
    source_lons : TYPE
        Source longitude.
    target_lats : TYPE
        Target latitude.
    target_lons : TYPE
        Target longitude.
    source_data : TYPE
        Source data for resampling.
    max_radius : TYPE
        The radius around each grid pixel in meters to search for neighbours in the swath..
    *args : TYPE
        DESCRIPTION.
    method : TYPE, optional
        Method for resampling ['nearest_neighbor' or 'kd_tree_guass']. The default is 'nearest_neighbor'.
    *args : TYPE
        DESCRIPTION.

    Returns
    -------
    result : TYPE
        Resampled data.

    '''
   
    # define the swath of the source instrument
    swath_def = geometry.SwathDefinition(lons = source_lons, lats = source_lats)
   
    # (using nearest neighbour resampling)
    if method == 'nearest_neighbor':
   
        # Define the swath of the target instrument
        swath_def2 = geometry.SwathDefinition(lons = target_lons, lats = target_lats)
       
        # Define the image grid and resample (using nearest neighbour resampling)
        swath_con = image.ImageContainerNearest(source_data, swath_def, radius_of_influence = max_radius)
        area_con = swath_con.resample(swath_def2)
       
        # data in the target grid
        result = area_con.image_data
   
    # Function for resampling using nearest Gussian weighting.
    # The Gauss weigh function is defined as exp(-dist^2/sigma^2).
    # Note the pyresample sigma is not the standard deviation of the gaussian.
    elif method == 'kd_tree_gauss':
   
        # Define a new grid
        grid_def = geometry.GridDefinition(lons=target_lons, lats=target_lats)
       
        # resampling
        result = kd_tree.resample_gauss(swath_def, source_data, grid_def, radius_of_influence=max_radius, sigmas = max_radius/3)
       
    # flaging the unknown data points to nans
    result[result < 1e-5] = np.nan
   
    return result

import_file = "./PACE_HARP2.20240523T003106.L1C.V2.5km.nc"
export_file = "result.tiff"

l1_reader = L1.L1C()
l1_data = l1_reader.read(import_file)

# extract all related netcdf data
original_latitude = l1_data["latitude"]
original_longitude = l1_data["longitude"]
width = original_latitude.shape[0]
height = original_latitude.shape[1]
image_data = l1_data['i'][:, :, 0, 0]

# use an array of Ground Control Points to create "anchors"
# by which we can reproject the data by
gcps = [
    # top-left corner
    GCP(row=0, col=0, x=original_longitude[0, 0], y=original_latitude[0, 0]),
    # top-right corner
    GCP(row=0, col=width - 1, x=original_longitude[0, -1], y=original_latitude[0, -1]),
    # bottom-left corner
    GCP(row=height - 1, col=0, x=original_longitude[-1, 0], y=original_latitude[-1, 0]),
    # bottom-right corner
    GCP(row=height - 1, col=width - 1, x=original_longitude[-1, -1], y=original_latitude[-1, -1]),
]
transform = from_gcps(gcps)

rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
xs, ys = xy(transform, rows.flatten(), cols.flatten())

transformed_latitude = np.array(xs).reshape((height, width))
transformed_longitude = np.array(ys).reshape((height, width))

metadata = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": image_data.dtype,
    "crs": "EPSG:4326",
    "transform": transform,
}

with rasterio.open(export_file, "w", **metadata) as dataset:

    image_data = resampleData(original_latitude, original_longitude, 
                              transformed_latitude, transformed_longitude,
                              image_data, max_radius=8000, method='kd_tree_gauss')

    try:
        dataset.write(image_data, 1)
        print("File has been successfully exported as: %s" % export_file)
    except Exception as e:
        print("An error occured while writing to file:\n\t%s" % e)