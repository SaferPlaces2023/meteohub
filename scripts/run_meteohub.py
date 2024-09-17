import datetime
import os
import time

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
bbox = "10.623676,44.792615,14.129578,46.679835"
start_fc = 1
end_fc = 48

# Create the output directory path
output_dir = f"./meteohub_data/{dataset}_{varname}/{current_year_month_day}/{current_run}/"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Create the output filename
output_filename = f"{output_dir}{dataset}_{varname}_{current_year_month_day}_{current_run}_{start_fc}-{end_fc}.tif"

# Construct the command
command = f"/home/cmve/.local/bin/meteohub --verbose --dataset {dataset} --varname {varname} --bbox {bbox} --date {current_year_month_day} --run {current_run} --start_fc {start_fc} --end_fc {end_fc} --out {output_filename} --fc_range"

attempt = 0
# Execute the command
while not os.path.exists(output_filename):
    attempt += 1
    print(f"Attempt {attempt}")
    os.system(command)
    if attempt > 15:
        break
    for file in os.listdir(output_dir):
        if file.startswith(f"{dataset}_{varname}_{current_year_month_day}_{current_run}_{start_fc}-{end_fc}"):
            output_filename = os.path.join(output_dir, file)
    if not os.path.exists(output_filename):
        time.sleep(1800)