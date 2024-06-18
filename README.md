# meteohub
https://meteohub.mistralportal.it/ downloader

# Install GDAL
Check if the os has GDAL included by running 
```
gdalinfo --version
```
In case not installed 
```
sudo apt install gdal-bin python3-gdal
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL=="`gdal-config --version`.*"
```

# Install meteohub
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.ubu.txt
pip install .
```

# Check installation is succesfull
```
meteohub --help
```
