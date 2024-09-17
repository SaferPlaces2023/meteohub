import datetime
import os
import time
import rasterio

def sum_geotiffs(folder_path, start_file, n_files, output_file):
    """
    Sum `n_files` GeoTIFFs starting from `start_file` in a folder.

    Parameters:
    - folder_path: The directory where the GeoTIFFs are stored.
    - start_file: The name of the file to start summing from.
    - n_files: The number of files to sum starting from start_file.
    - output_file: The path where the result will be saved.
    """
    # List all files in the folder and sort them
    tiff_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.tif')])

    # Ensure the start_file exists in the folder
    if start_file not in tiff_files:
        raise ValueError(f"{start_file} not found in folder.")

    # Find the index of the start_file
    start_index = tiff_files.index(start_file)

    # Select the n-following files starting from start_file
    selected_files = tiff_files[start_index:start_index + n_files]

    if len(selected_files) < n_files:
        print("Not enough files to sum.")
        return
    # Open the first file to get the metadata and initialize the sum array
    with rasterio.open(os.path.join(folder_path, selected_files[0])) as src:
        sum_data = src.read(1)  # Read first band
        profile = src.profile  # Save profile for the output

    # Loop through the remaining files and sum their values
    for filename in selected_files[1:]:
        end_file = filename
        with rasterio.open(os.path.join(folder_path, filename)) as src:
            data = src.read(1)
            sum_data += data  # Sum the arrays

    # Write the result to a new GeoTIFF file
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(sum_data, 1)

    print(f"Summed {n_files} GeoTIFF files starting from {start_file} to {end_file} and saved to {output_file}")


# Get the current date
current_date = datetime.datetime.now()
current_year_month_day = current_date.strftime('%Y-%m-%d')

# Determine the run time based on the current hour
if current_date.hour < 19:
    current_run = "00:00"
else:
    current_run = "12:00"

# Define the parameters for the meteohub command
dataset = "COSMO-2I"
varname = "tp"

# Create the output directory path
data_folder = f"/home/cmve/meteohub_data/{dataset}_{varname}/{current_year_month_day}/{current_run}/"

out_folder = data_folder+"accumulated_forecasts/"

# Create the output directory if it doesn't exist
os.makedirs(out_folder, exist_ok=True)

tiff_files = sorted([f for f in os.listdir(data_folder) if f.endswith('.tif')])
accumulate_list = [3,6,12]

for n_accum in accumulate_list:
    for file in tiff_files:
        # start_file = "COSMO-2I_tp_2024-08-26_00:00_1-48_fc0 days 01:00:00.tif"  # The name of the first file to start summing from
        # n_files = 24  # Number of files to sum
        start_hour = file.split("COSMO-2I_tp_")[1].split("_fc")[1].replace(".tif","").replace(" ","_").replace(":","-")
        day = int(start_hour[0])
        if day == 1:
            sum_day = 24
        elif day == 2:
            sum_day = 48
        else:
            sum_day = 0
        start_hour_int = int(start_hour.split("days_")[1].split("-")[0])+sum_day
        end_hour_int = start_hour_int + n_accum - 1
        print(f"{file} -> {start_hour_int}:{end_hour_int}")

        date = file.split("COSMO-2I_tp_")[1].split("_")[0]
        output_file = f"{out_folder}forecast_acc_{n_accum}h_{date}_{current_run.replace(':','-')}_{start_hour_int}h-{end_hour_int}h.tif"
        # print(output_file)

        sum_geotiffs(data_folder, file, n_accum, output_file)