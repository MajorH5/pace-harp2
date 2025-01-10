import os

import terracotta
from terracotta.server import create_app
from terracotta import update_settings
from utils import extract_granule_metadata
from l1_to_tiff import l1_to_tiff

AH2_PARAMS = ["instrument", "date",]
DB_NAME = "tc_db.sqlite"
DB_PATH = "example"
SAMPLES_PATH = "granules"
HOST = "localhost"
PORT = "5000"
ANGLE_INDEX = 40

# apply global settings update
# to terracotta
update_settings(DRIVER_PATH=os.path.join(DB_PATH, DB_NAME), REPROJECTION_METHOD="nearest")

class PACEHARP2TCServer:
    def __init__(self, driver_path, nuke=True):
        if not driver_path:
            raise Exception("paceharp2tcserver: No driver path has been specified.")

        os.makedirs(driver_path, exist_ok=True)
        database_file = os.path.join(driver_path, DB_NAME)
        if nuke and os.path.isfile(database_file):
            os.remove(database_file)

        self._driver_path = driver_path
        self._files = []
        self._driver = terracotta.get_driver(database_file)
        self._server = create_app()
            
        if not os.path.isfile(database_file):
            self._driver.create(keys=AH2_PARAMS)

    def run(self, port, host):
        self._server.run(port=port, host=host, threaded=False)

    def load_from_directory(self, data_path):
        for entry in os.listdir(data_path):
            if entry.split(".")[-1] == "nc":
                path = os.path.join(data_path, entry)
                tc_server.serve_granule(path)

    def serve_granule(self, nc_path):
        filename = os.path.basename(nc_path)
        print(f"serve_granule: loading data from {filename}")

        # convert netCDF -> GeoTIFF
        prefix, _ = os.path.splitext(filename)
        tiff_path = os.path.join(self._driver_path, prefix + ".tiff")

        print(f"serve_granule: converting {filename} netCDF -> GeoTIFF")
        l1_to_tiff(nc_path, tiff_path)

        metadata = extract_granule_metadata(filename)

        if metadata == None:
            raise Exception(f"paceharp2tcserver.serve_granule: File '{filename}' has an invalid naming convention.")
        
        # place into tc driver
        with self._driver.connect():
            self._driver.insert(metadata, tiff_path)
            print(f"serve_granule: {filename} has been successfully inserted", metadata, tiff_path)

if __name__ == "__main__":
    tc_server = PACEHARP2TCServer(DB_PATH)
    tc_server.load_from_directory(SAMPLES_PATH)
    tc_server.run(PORT, HOST)


# TODO: fix yellow coloring in projection (no-data areas) 