import os
import numpy as np
import xarray as xr
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, Resampling
from meteohub.module_log import Logger
import numpy as np
import tempfile

def get_grib_variable(grib_file, varname, bbox=None, start_fc=1, end_fc=None, fc_range=False):
    ds: xr.Dataset = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'stepType': 'accum'})

    # # convert start_forecast to timedelta64[ns]
    # start_timedelta_ns = np.timedelta64(start_fc * 3600000000000, 'ns')
    # end_timedelta_ns = np.timedelta64(end_fc * 3600000000000, 'ns') if end_fc else None
    start_timedelta = np.timedelta64(start_fc, 'h')
    end_timedelta = np.timedelta64(end_fc, 'h') if end_fc else None

    try:
        # Extracting variable 
        ds = ds[varname]
        
    except KeyError:
        Logger.error(f"Variable {varname} not found in the grib file. Available varnames: {list(ds.data_vars)}")
        return None

    try:
        ds = ds.sel(step=slice(start_timedelta, end_timedelta))
        # # if step dimension equals 0 raise error
        if ds['step'].count() == 0:
            raise KeyError
    except KeyError:
        Logger.error(f"Forecast step not found in the grib file. Perhaps the forecast step is not available.")
        return None
    
    Logger.debug(f"DataArray:\n{ds}")
    if not fc_range:
        if "step" in ds.dims:
            # calculate the accumulated value for each step
            ds = ds.sum(dim='step',skipna=True)
    
    # convert xr dataset to pd dataframe
    df = ds.to_dataframe()
    Logger.debug(f"Dataframe description:\n{df.describe()}")
    if bbox:
        df = df[(df['longitude'] >= bbox[0]) & (df['longitude'] <= bbox[2]) & (df['latitude'] >= bbox[1]) & (df['latitude'] <= bbox[3])]
    return df


def dataframe_to_tiff(df, varname, t_srs, out_tiff, fc_range):
    
    if fc_range:
        # for each forecast valid_time create a tiff file
        
        for fc in df.index.get_level_values('step').unique():
            df_fc = df[df.index.get_level_values('step') == fc]
            out_tiff_fc = out_tiff.replace(".tif", f"_fc{fc}.tif")
            create_tiff(df_fc, varname, t_srs, out_tiff_fc)
    else:
        create_tiff(df, varname, t_srs, out_tiff)


def create_tiff(df, varname, t_srs, out_tiff):
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

    # Define the transform
    transform = from_origin(lon_min, lat_min, resolution, -resolution)
    # Save the data as a GeoTIFF in EPSG:4326
    if out_tiff and out_tiff.endswith('.tif'):
        pass
    else:
        out_tiff = f'out.tif'

    if t_srs == 'EPSG:4326':
        temp_tiff = out_tiff
    else:
        temp_tiff = os.path.join(tempfile.gettempdir(), "temp.tif")

    try:
        with rasterio.open(
            temp_tiff, 'w',
            driver='GTiff',
            height=rain_grid.shape[0],
            width=rain_grid.shape[1],
            count=1,
            dtype=np.float32,
            crs='EPSG:4326',
            transform=transform,
            nodata=-9999
        ) as dst:
            dst.write(rain_grid, 1)

        if t_srs != 'EPSG:4326':
                
            # Reproject to t_srs
            with rasterio.open(temp_tiff) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, t_srs, src.width, src.height, *src.bounds)
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': t_srs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })

                with rasterio.open(out_tiff, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=t_srs,
                            resampling=Resampling.nearest
                        )

            # Remove the temporary file
            os.remove(temp_tiff)
    except Exception as e:
        Logger.error(f"Error converting to GTiff, check provided parameters like bbox or t_srs. {e}")
        return False
    return out_tiff
