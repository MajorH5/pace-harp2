import os
import numpy as np
import rasterio
from rasterio.transform import from_gcps, from_origin, xy
from rasterio.control import GroundControlPoint as GCP
try:
    from pyresample import image, geometry, kd_tree
except:
    print('Pyresample package not installed')
from netCDF4 import Dataset

# from nasa_pace_data_reader import L1, plot
from nasa_pace_data_reader import L1_AH2 as L1

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Local definitions

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

def readOCI_l1b(fileName):
    '''
    Read the OCI L1B data

    Args:
        fileName: str: The file name of the OCI L1B data

    Returns:
        lat: np.array: The latitude data
        lon: np.array: The longitude data
        rhot: np.array: The reflectance data
        solar_irradiance: np.array: The solar irradiance data
        wavelength: np.array: The wavelength data

    '''
    # Read the OCI L1B data
    OCI_L1B = Dataset(fileName)

    # define the groups
    geo = OCI_L1B.groups['geolocation_data']
    obs = OCI_L1B.groups['observation_data']
    sensor = OCI_L1B.groups['sensor_band_parameters']

    # read the data
    lat = geo['latitude'][:]
    lon = geo['longitude'][:]

    # read the reflectance
    # rhot_blue
    rhot_blue = obs['rhot_blue'][:]
    # blue_solar_irradiance
    blue_solar_irradiance = sensor['blue_solar_irradiance'][:]
    blue_wavelength = sensor['blue_wavelength'][:]

    # rhot_red
    rhot_red = obs['rhot_red'][:]
    # red_solar_irradiance
    red_solar_irradiance = sensor['red_solar_irradiance'][:]
    red_wavelength = sensor['red_wavelength'][:]

    # stich the data
    rhot = np.concatenate((rhot_blue, rhot_red), axis=0)
    solar_irradiance = np.concatenate((blue_solar_irradiance, red_solar_irradiance), axis=0)
    wavelength = np.concatenate((blue_wavelength, red_wavelength), axis=0)

    return lat, lon, rhot, solar_irradiance, wavelength

# Location of the file
fileName = './PACEPAX-AH2MAP-L1C_ER2_20240910T175007_RA.nc'

# Instrument
instrument = 'HARP2'

# verbose to print the more information
verbose = True

# reflectance image
if instrument == 'HARP2':
    # Read the file
    l1b = L1.L1C()
    l1b_dict = l1b.read(fileName)
    var2plot = 'i'
    angleIdx = 35
    # TODO: combine rgb values into single image
    # angleIndex(40) - Red
    # angleIndex(4) - Green
    # angleIndex(84) - Blue
    # angleIndex(74) - Near Infrared
    im_data = l1b_dict[var2plot][:,:,40,0] # For L1C there are 3-dimensions, select 1 band
    im_lat = l1b_dict['latitude'][:,:]
    im_lon = l1b_dict['longitude'][:,:]

elif instrument == 'OCI':
    # Read the OCI L1B data
    '''
    lat, lon, rhot, solar_irradiance, wavelength = readOCI_l1b(fileName)
    oci_angle_idx = [53, 97, 160, 271 ]    # OCI
    im_data = rhot[oci_angle_idx[2],:,:]
    im_lat = lat
    im_lon = lon
    angleIdx = oci_angle_idx[2]
    '''
    # Read the file
    l1c = L1.L1C(instrument='OCI')
    l1c_dict = l1c.read(fileName)
    var2plot = 'i'
    iAng = 1
    angleIdx = iAng
    im_data = l1c_dict[var2plot][:, :, iAng,271]
    im_lat = l1c_dict['latitude'][:, :]
    im_lon = l1c_dict['longitude'][:, :]


# Define the desired width and height of the raster
width = im_data.shape[1]
height = im_data.shape[0]

# Generate GCPs from the lat/lon arrays
gcps = []
# If desired, include the corner points to ensure coverage
gcps = [
    GCP(row=0, col=0, x=im_lon[0, 0], y=im_lat[0, 0]),
    GCP(row=0, col=width - 1, x=im_lon[0, -1], y=im_lat[0, -1]),
    GCP(row=height - 1, col=0, x=im_lon[-1, 0], y=im_lat[-1, 0]),
    GCP(row=height - 1, col=width - 1, x=im_lon[-1, -1], y=im_lat[-1, -1]),
]

# Derive the transform from GCPs
transform = from_gcps(gcps)

# new lat-lon grid
# Generate arrays of row and column indices
rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

# Flatten the row and column indices
rows_flat = rows.flatten()
cols_flat = cols.flatten()

# Use the transform to get x (longitude) and y (latitude) coordinates
xs, ys = xy(transform, rows_flat, cols_flat)

# Reshape the coordinates back to 2D arrays
lon_grid = np.array(xs).reshape((height, width))
lat_grid = np.array(ys).reshape((height, width))

lat_diff = im_lat - lat_grid
lon_diff = im_lon - lon_grid

# Print the statistics of the difference
# If your original latitude and longitude arrays (im_lat, im_lon) have irregular spacing or distortions, this method may not perfectly match them.
# You can compare the generated grids with your original im_lat and im_lon to assess the accuracy:
print('Latitude difference statistics:')
print('Min:', np.min(lat_diff), 'Max:', np.max(lat_diff))

print('Longitude difference statistics:')
print('Min:', np.min(lon_diff), 'Max:', np.max(lon_diff))

# Use the transform to create or open a raster dataset
fileName_tiff = os.path.splitext(fileName)[0] + '_%s' % angleIdx + '.tiff'

# metadata for the raster
metadata = {
    'driver': 'GTiff',
    'height': height,
    'width': width,
    'count': 1,
    'dtype': im_data.dtype,
    'crs': 'EPSG:4326',
    'transform': transform,
    # 'gcps': (gcps, rasterio.crs.CRS.from_epsg(4326))
}


with rasterio.open(fileName_tiff, 'w', **metadata) as dst:

    # interpolate im_data to geTiff lat-lon grid using pyresample
    im_data_new = resampleData(im_lat, im_lon, lat_grid, lon_grid, im_data, max_radius=8000, method='nearest_neighbor')

    # Write your data to the raster
    try:
        # TODO: check second argument of dst.write
        dst.write(im_data_new, 1)

        # file written successfully
        print('Raster file written successfully: %s' %fileName_tiff)

    except Exception as e:
        print('Error writing the data to the raster: %s' %e)
        raise