# -------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2024 Saferplaces
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Name:        main.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     17/06/2024
# -------------------------------------------------------------------------------
import click
from datetime import datetime
import os
from meteohub.module_data import dataframe_to_tiff, get_grib_variable

from .module_request import download_file
from .module_logo import logo
from .module_log import *
from .module_version import get_version


@click.command()
@click.option('--dataset',  type=click.STRING, required=False, default="COSMO-2I-RUC" ,help="The dataset to download. Default is 'COSMO-2I-RUC'.")
@click.option('--date', type=click.STRING, required=False,  help="The datetime to download with format %Y-%m-%d. Default is latest datetime available.")
@click.option('--run', type=click.STRING, required=False, default="00:00", help="The hour of forecast run to download in format %H:%M. Default is 00:00.")
@click.option('--start_fc', type=click.INT, required=False, default=1, help="The hour at which the accumulation starts. Default is 1.")
@click.option('--end_fc', type=click.INT, required=False, default=None, help="The hour at which the accumulation ends. Default is None.")
@click.option('--out', type=click.Path(exists=False), required=False, default="", help="The output file name.")
@click.option('--fc_range', is_flag=True, required=False, default=False, help="If True the output will be multiple tif files, one for each forecast hour. Default is False")
@click.option('--varname', type=click.STRING, required=False, default="rain_gsp", help="The variable name to extract from the grib file. Default is 'tp'.")
@click.option('--bbox', type=click.STRING, required=False, default=None, help="The bounding box to extract the data. Default is None.")
@click.option('--t_srs', type=click.STRING, required=False, default="EPSG:4326", help="The target spatial reference system. Default is 'EPSG:4326'.")
@click.option('--version', is_flag=True, required=False, default=False, help="Print the version.")
@click.option('--debug', is_flag=True, required=False, default=False,   help="Debug mode.")
@click.option('--verbose', is_flag=True, required=False, default=False, help="Print some words more about what is doing.")
def main(dataset, date, run, start_fc, end_fc, out, fc_range, varname, bbox, t_srs, version, debug ,verbose):
    """
    meteohub is as client downloader for https://meteohub.mistralportal.it portal
    """
    run_meteohub(dataset, date, run, start_fc, end_fc, out, fc_range, varname, bbox, t_srs, version, debug, verbose)
    
def run_meteohub(dataset, date, run, start_fc, end_fc, out, varname, bbox, fc_range=False, t_srs="EPSG:4326", version=False, debug=False, verbose=False):
    set_log_level(verbose, debug)

    if debug:
        click.echo(logo())
    if version:
        click.echo(f"v{get_version()}")
        return True

    # checl out extension
    if out and not out.endswith(".tif"):
        Logger.error("The output file must be a tif file.")
        return False
    # check bbox format
    if bbox:
        bbox = bbox.split(",")
        bbox = [float(x) for x in bbox]
        if len(bbox) != 4:
            Logger.error("The bbox must be a list of 4 elements.")
            return False
        if bbox[0] > bbox[2] or bbox[1] > bbox[3]:
            Logger.error("The bbox must be in the format min_lon, min_lat, max_lon, max_lat")
            return False
    
    try:
        file_grib = download_file(dataset, date=date, run=run)
        if file_grib:
            Logger.info(f"Downloaded {file_grib}")
        else:
            raise Exception("Error downloading the file")
    except Exception as e:
        Logger.error(f"Error downloading the file: {e}")
        return False

    df = get_grib_variable(file_grib, varname, bbox, start_fc, end_fc, fc_range)

    if df is not None:

        if not out:
            out = file_grib.replace('.grib', '.tif').split('/')[-1]
        try:
            dataframe_to_tiff(df, varname, t_srs, out, fc_range)
        except Exception as e:
            Logger.error(f"Error converting the file: {e}")
            return False
        
        Logger.info(f"Output tif file name: {out}")

        # delete file grib
        os.remove(file_grib)

        return True
    else:
        return False