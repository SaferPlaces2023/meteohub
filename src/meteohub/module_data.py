import os
import numpy as np
import xarray as xr
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from meteohub.module_log import Logger
# from rasterio.warp import calculate_default_transform, reproject, Resampling
# from pyproj import CRS, Proj, transform


def get_grib_variable(grib_file, varname, bbox=None):
    ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'stepType': 'accum'})
    try:
        ds = ds[varname]
    except KeyError:
        Logger.error(f"Variable {varname} not found in the grib file. Available varnames: {list(ds.data_vars)}")
        return None

    df = ds.to_dataframe()

    if bbox:
        df = df[(df['longitude'] >= bbox[0]) & (df['longitude'] <= bbox[2])]
        df = df[(df['latitude'] >= bbox[1]) & (df['latitude'] <= bbox[3])]

    return df


def dataframe_to_tiff(df, varname, out_tiff):
    # Define the resolution of the grid
    resolution = 0.02  # Adjust as necessary

    # Generate the grid based on latitude and longitude
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_grid = np.arange(lon_min, lon_max, resolution)
    lat_grid = np.arange(lat_min, lat_max, resolution)
    lon_grid, lat_grid = np.meshgrid(lon_grid, lat_grid)

    # Interpolate the rain_gsp values to the grid
    rain_grid = np.zeros_like(lon_grid)
    for i in range(lon_grid.shape[0]):
        for j in range(lon_grid.shape[1]):
            distances = np.sqrt((df['longitude'] - lon_grid[i, j])**2 + (df['latitude'] - lat_grid[i, j])**2)
            nearest_index = distances.idxmin()
            rain_grid[i, j] = df.loc[nearest_index, varname]

    # print(rain_grid.shape, rain_grid.min(), rain_grid.max())
    # Define the transform
    transform = from_origin(lon_min, lat_max, resolution, resolution)

    # Save the data as a GeoTIFF
    if out_tiff and out_tiff.endswith('.tif'):
        Logger.info(f"File name provided: {out_tiff}")
    else:
        out_tiff = f'out.tif'
        Logger.info(f"No output file name provided, saving file as: {out_tiff}")

    if os.path.exists(out_tiff):
        os.remove(out_tiff)

    with rasterio.open(
        out_tiff, 'w',
        driver='GTiff',
        height=rain_grid.shape[0],
        width=rain_grid.shape[1],
        count=1,
        dtype=rain_grid.dtype,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(rain_grid, 1)

    return out_tiff