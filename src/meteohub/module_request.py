import requests
import pandas as pd 
from .module_log import *
import os
from datetime import datetime, timedelta
import tempfile

def download_file(dataset, date, run, debug=False):

    url = f"https://meteohub.mistralportal.it/api/datasets/{dataset}/opendata"
    res = requests.get(url)
    files = pd.DataFrame(res.json())
    # Logger.debug(f"Files: {files}")
    
    if not date:
        files = files[files['date'] == files['date'].max()]
        Logger.debug(f"Searching the latest date and run pair {files['date'].values[0]} {files['run'].values[0]}")
    else:
        # check if the date and run are in the correct format
        try:
            datetime.strptime(date, '%Y-%m-%d')
            datetime.strptime(run, '%H:%M')
        except ValueError:
            Logger.error("Incorrect date or run format. Date should be YYYY-MM-DD, run should be HH:MM")
            return False
    try:
        Logger.debug(f"Searching the date and run pair {date} {run}")
        sel_files = files[(files['date'] == date) & (files['run'] == run)]
        if sel_files.empty:
            raise KeyError
    except KeyError:
        # create a list of tuples with date and run columns
        dates = files[['date', 'run']].apply(tuple, axis=1)
        Logger.error(f"Date {date} not found in the available dates and runs pairs: \n{dates.values}")
        return False
        
    Logger.debug(f"Found {len(sel_files)} files: {sel_files['filename'].values}, date: {date}, run: {run}")
    # save outgrib in a temporary folder
    out_grib = os.path.join(tempfile.gettempdir(), sel_files['filename'].values[0])
    Logger.info(f"Downloading {out_grib}")
    
    if debug:
        Logger.debug(f"Downloading {sel_files['filename'].values[0]}")
        if os.path.exists(out_grib):
            Logger.info(f"File {out_grib} already exists. Skipping download.")
            return out_grib
    
    for filename in sel_files['filename']:
        url = f"https://meteohub.mistralportal.it/api/opendata/{filename}"
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(out_grib, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)

    return out_grib