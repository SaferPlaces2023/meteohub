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

from meteohub.module_data import dataframe_to_tiff, get_grib_variable

from .module_request import download_file
from .module_logo import logo
from .module_log import *
from .module_version import get_version


@click.command()
@click.option('--dataset',  type=click.STRING, required=False, default="COSMO-2I-RUC" ,help="The dataset to download. Default is 'COSMO-2I-RUC'.")
@click.option('--date', type=click.STRING, required=False,  help="The datetime to download. Default is latest datetime available.")
@click.option('--out', type=click.Path(exists=False), required=False, default="", help="The output file name.")
@click.option('--varname', type=click.STRING, required=False, default="rain_gsp", help="The variable name to extract from the grib file. Default is 'tp'.")
@click.option('--bbox', type=click.STRING, required=False, default=None, help="The bounding box to extract the data. Default is None.")
@click.option('--version', is_flag=True, required=False, default=False, help="Print the version.")
@click.option('--debug', is_flag=True, required=False, default=False,   help="Debug mode.")
@click.option('--verbose', is_flag=True, required=False, default=False, help="Print some words more about what is doing.")
def main(dataset, date, out, varname, bbox, version, debug ,verbose):
    """
    meteohub is as client downloader for https://meteohub.mistralportal.it portal
    """
    set_log_level(verbose, debug)

    # parse bbox
    if bbox:
        bbox = bbox.split(',')
        bbox = [float(x) for x in bbox]
        if len(bbox) != 4:
            Logger.error("The bbox must be a list of 4 elements.")
            return False
        
    if debug:
        click.echo(logo())
    if version:
        click.echo(f"v{get_version()}")
        return True
    # do something with args
    # 

    # check args
    if not date:
        # search the latest datetime available for download
        date = datetime.now()
        # floor the datetime to the nearest 3hour
        date = date.replace(minute=0, second=0, microsecond=0)
        date = date.replace(hour=date.hour - date.hour % 3)
        Logger.info(f"Searching the latest datetime available for download:{date}")
        # TODO:
        # try to download the dataset if not available try the previous datetime
        # counter = 0
        # while counter < 12:
        #     try:
        #         # download the dataset
        #         file_grib = download_file(dataset)
        #         # raise Exception("Not available")
        #         break
        #     except:
        #         counter += 1
        #         if date.hour-3 < 0:
        #             date = date.replace(day=date.day - 1)
        #             date = date.replace(hour=21)
        #         else:
        #             date = date.replace(hour=date.hour - 3)
        #         Logger.info(f"Searching the latest datetime available for download:{date}")
    
    try:
        file_grib = download_file(dataset)
    except Exception as e:
        Logger.error(f"Error downloading the file:{e}")
        return False
    Logger.info(f"Grib file name:{file_grib}")

    df = get_grib_variable(file_grib, varname, bbox)

    if not out:
        out_tiff = file_grib.replace('.grib', '.tif')

    Logger.info(f"Output tif file name:{out_tiff}")
    try:
        dataframe_to_tiff(df, varname, out_tiff)
    except Exception as e:
        Logger.error(f"Error converting the file:{e}")
        return False
    
    Logger.info(f"Output tif file name:{out_tiff}")


    # click.echo(click.style(f"Hello world!", fg="bright_green", bold=True))
    return True