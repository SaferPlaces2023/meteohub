import requests
import pandas as pd 
from .module_log import *
import os


def download_file(dataset, date=None, out=None, time_delta=3):
    url = f"https://meteohub.mistralportal.it/api/datasets/{dataset}/opendata"
    res = requests.get(url)
    files = pd.DataFrame(res.json())

    date_start = date
    date_end = date + pd.Timedelta(hours=time_delta)
    files['date'] = pd.to_datetime(files['date'])
    
    # filter files
    # if no date is provided, download the latest file
    if date is None:
        files = files[files['date'] == files['date'].max()]
    else:
        files = files[(files['date'] >= date_start) & (files['date'] <= date_end)]
        
    out = out if out else files['filename'].values[0]

    if os.path.exists(out):
        Logger.info(f"File already exists: {out}")
        return out
    
    for filename in files['filename']:
        url = f"https://meteohub.mistralportal.it/api/opendata/{filename}"
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(out, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        Logger.info(f"Downloaded {url}")

    return out
