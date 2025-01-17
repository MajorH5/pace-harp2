
from datetime import datetime
import requests

from dash.dependencies import Output, Input
from utils import get_date_range
from config import TC_URL


def register_ui_callbacks(app):
    @app.callback(
        [
            Output("date-picker", "disabled_days"),
            Output("date-picker", "min_date_allowed"),
            Output("date-picker", "max_date_allowed"),
            Output("date-picker", "disabled"),
            Output("date-picker", "placeholder"),
            Output("granules", "options"),
            Output("granules", "disabled")
        ],
        Input("date-picker", "date"),
    )
    def compute_datepicker_state(selected_date):
        try:
            print("disable_nodata_days: fetching datasets...")
            result = requests.get(f"{TC_URL}/datasets", timeout=10)
            datasets = result.json()["datasets"]
            total_dates = []

            for dataset in datasets:
                # remove "_" used to avoid url encoding space
                # 1997-01-01_00:00:00 -> 1997-01-01 00:00:00
                date = dataset["date"].replace("_", " ")
                total_dates.append(datetime.fromisoformat(date))

            min, max, unavailable = get_date_range(total_dates)

            min = f"{min.year}-{min.month}-{min.day}"
            max = f"{max.year}-{max.month}-{max.day}"

            for i in range(len(unavailable)):
                date = unavailable[i]
                unavailable[i] = f"{date.year}-{date.month}-{date.day}"

            granules_on_date = []

            if selected_date != None:
                for granule in total_dates:
                    if datetime.fromisoformat(selected_date).date() == granule.date():
                        # get time component only
                        time = str(granule).split(" ")[-1]
                        granules_on_date.append(time)

            print("disable_nodata_days: computed new date ranges")
            return unavailable, min, max, False, "Choose Date", granules_on_date, False
        except:
            print("disable_nodata_days: failed to retrieve datasets!")
            return [], "1970-01-01", "1970-01-01", True, "Error getting datasets", [], True

    @app.callback(Output("tc", "opacity"), Input("opacity", "value"))
    def update_tile_opacity(opacity):
        return [opacity]
