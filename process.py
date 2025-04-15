import os
import re
from geospatial_data.l1_to_tiff import l1_to_tiff, read_l1_data

pattern = r"PACEPAX-AH2MAP-L1C_ER2_.*_R.*\.nc"
base_path = "/mnt/pace-pax/L1Data/L1BC2"
export_path = "export"
CHANNEL_INDEXES = {
    "red": 40, "green": 4,
    "blue": 84, "infrared": 74
}

def process_granule(abs_granule_path):
    channels = CHANNEL_INDEXES.keys()

    granule_name = abs_granule_path.split("/")[-1].replace(".nc", "")
    tiff_directory = os.path.join(export_path, granule_name)

    if os.path.exists(tiff_directory):
        # assumed to already been created
        print(f"process_graunle: skipping \"{granule_name}\" because a path for it already existed.")
        return
    else:
        os.makedirs(tiff_directory)

    l1_data = read_l1_data(abs_granule_path)
    for channel in channels:
        tiff_filename = os.path.join(tiff_directory, f"{channel}-channel.tif")
        l1_to_tiff(l1_data, tiff_filename, CHANNEL_INDEXES[channel])

def process_directory(path):
    sub_directories = os.listdir(path)

    for directory in sub_directories:
        if not os.path.isdir(os.path.join(base_path, directory)):
            continue

        files = os.listdir(os.path.join(base_path, directory))

        for granule_filename in files:
            if re.match(pattern, granule_filename):
                process_granule(os.path.join(base_path, directory, granule_filename))

if __name__ == "__main__":
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    process_directory(base_path)