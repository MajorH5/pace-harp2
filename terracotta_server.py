import os

import terracotta
from terracotta.server import create_app
from terracotta import update_settings
from utils import extract_granule_metadata
from l1_to_tiff import l1c_to_tiff

AH2_PARAMS = {
    "date": "The date when the granule data was sourced.",
    "instrument": "The instrument that used for collecting the data."
}
DB_NAME = "tc_db.sqlite"
PORT = "5000"
HOST = "localhost"

# apply global settings update
# to terracotta
update_settings(REPROJECTION_METHOD="nearest")

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
            self._driver.create(keys=AH2_PARAMS.keys(), key_descriptions=AH2_PARAMS)

    def run(self):
        self._server.run(port=PORT, host=HOST, threaded=False)

    def serve_granule(self, nc_path):
        filename = os.path.basename(nc_path)

        # convert netCDF -> GeoTIFF
        tiff_path = os.path.join(self._driver_path, filename)
        l1c_to_tiff(nc_path, tiff_path)

        metadata = extract_granule_metadata(filename)

        if metadata == None:
            raise Exception(f"paceharp2tcserver.serve_granule: File '{filename}' has an invalid naming convention.")
        
        # place into tc driver
        with self._driver.connect():
            self._driver.insert(metadata, tiff_path)

tc_server = PACEHARP2TCServer("example")
tc_server.run()