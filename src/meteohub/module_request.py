import requests
import pandas as pd 
from .module_log import *
import os
from datetime import datetime, timedelta


def download_file(dataset, date=None, time_delta=3):

    url = f"https://meteohub.mistralportal.it/api/datasets/{dataset}/opendata"
    res = requests.get(url)
    files = pd.DataFrame(res.json())
    Logger.debug(f"Files: {files}")
    
    if not date:
        files = files[files['date'] == files['date'].max()]
        # search the latest datetime available for download
        # date = datetime.now()
        # # floor the datetime to the nearest time_delta hours
        # date = date.replace(minute=0, second=0, microsecond=0)
        # date = date.replace(hour=date.hour - date.hour % time_delta)
        # Logger.info(f"Searching the latest datetime available for download:{date}")
    else:
        
        # convert date to datetime
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            date_start = date
            Logger.debug(f"Searching files from {date_start}, Type: {type(date_start)}")
            date_end = date + timedelta(hours=time_delta)
            Logger.debug(f"Searching files to {date_end}")
            files['date'] = pd.to_datetime(files['date'])
            Logger.debug(f"Searching files from {date_start} to {date_end}")
            files = files[(files['date'] >= date_start) & (files['date'] <= date_end)]
        except ValueError:
            Logger.error("Incorrect date format, should be YYYY-MM-DDTHH:MM:SS")
            return False
        Logger.info(f"DATE: {date}")
    
    

    # Logger.info(f"Searching files from {date_start} to {date_end}")
    
    
        
        
    Logger.debug(f"Found {len(files)} files: {files['filename'].values}")
    out_grib = files['filename'].values[0]
    Logger.info(f"Downloading {out_grib}")
    # if os.path.exists(out_grib):
    #     Logger.info(f"File already exists: {out_grib}")
    #     return out_grib
    
    for filename in files['filename']:
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
        Logger.info(f"Downloaded {url}")

    return out_grib
