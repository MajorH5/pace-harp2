import os

import terracotta
from terracotta.server import create_app
from terracotta import update_settings
from utils import extract_granule_metadata
from geospatial_data.l1_to_tiff import l1_to_tiff, read_l1_data

CHANNEL_INDEXES = {
    "red": 40, "green": 4,
    "blue": 84, "infrared": 74
}
AH2_PARAMS = ["instrument", "date", "channel"]
DB_NAME = "tc_db.sqlite"
DB_PATH = "geospatial_data/database"
SAMPLES_PATH = "geospatial_data/granules"
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
        if not os.path.isdir(data_path):
            raise Exception("")

        entries = [e for e in os.listdir(data_path) if e.split(".")[-1] == "nc"]

        print(f"PACEHARP2TCServer.load_from_directory: loading {len(entries)} files from {data_path}")

        for i in range(len(entries)):
            print(f"PACEHARP2TCServer.load_from_directory: file {i} of {len(entries)}")
            entry = entries[i]
            path = os.path.join(data_path, entry)
            tc_server.serve_granule(path)

    def serve_granule(self, nc_path):
        filename = os.path.basename(nc_path)

        # convert netCDF -> GeoTIFF
        prefix, _ = os.path.splitext(filename)
        os.makedirs(os.path.join(self._driver_path, prefix), exist_ok=True)

        channels = CHANNEL_INDEXES.keys()

        # TODO: change l1c constant to be based upon file name
        #       once we are sure file naming is consistent
        l1_data = read_l1_data(nc_path, "l1c")
        l1_meta = extract_granule_metadata(filename)

        for channel in channels:
            tiff_path = os.path.join(self._driver_path, prefix, f"{channel}-channel.tiff")

            l1_to_tiff(l1_data, tiff_path, CHANNEL_INDEXES[channel])

            metadata = l1_meta.copy()
            metadata["channel"] = channel

            if metadata == None:
                raise Exception(f"PACEHARP2TCServer.serve_granule: File '{
                                filename}' has an unexpected naming convention.")

            # place into tc driver
            with self._driver.connect():
                self._driver.insert(metadata, tiff_path)


if __name__ == "__main__":
    tc_server = PACEHARP2TCServer(DB_PATH)
    tc_server.load_from_directory(SAMPLES_PATH)
    tc_server.run(PORT, HOST)
