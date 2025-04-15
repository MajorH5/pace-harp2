
from datetime import datetime
import requests

from layouts.data_controller import create_granule_view
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from utils import get_date_range, is_granule_selected
from config import TC_LOCAL


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
            result = requests.get(f"{TC_LOCAL}/datasets?limit=10000", timeout=10)
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
                    # get time component only
                    time = str(granule).split(" ")[-1]

                    if datetime.fromisoformat(selected_date).date() == granule.date() and time not in granules_on_date:
                        granules_on_date.append(time)

            print("disable_nodata_days: computed new date ranges")
            return unavailable, min, max, False, "Choose Date", granules_on_date, False
        except:
            print("disable_nodata_days: failed to retrieve datasets!")
            return [], "1970-01-01", "1970-01-01", True, "Error getting datasets", [], True

    @app.callback(Output("tc", "opacity"), Input("opacity", "value"))
    def update_tile_opacity(opacity):
        return [opacity]

    @app.callback(Output("geolayer", "url"), Input("geolayer_selector", "value"))
    def update_geolayer_tiles(value):
        # fstring would bloat the template
        prefix, postfix = "https://{s}.basemaps.cartocdn.com/rastertiles/", "/{z}/{x}/{y}{r}.png"
        return prefix + value + postfix

    @app.callback(
        Output("add-granule-btn", "disabled"),
        Input("granules", "value")
    )
    def update_selected_granules(selected_granule):
        return selected_granule == None
    
    @app.callback(
        [Output("tile-layers", "children", allow_duplicate=True), Output("selected-granules-list", "children", allow_duplicate=True)],
        [
            Input("add-granule-btn", "n_clicks"),
            State("tile-layers", "children"),
            State("selected-granules-list", "children"),
            State("date-picker", "date"),
            State("granules", "value"),
        ],
        prevent_initial_call=True
    )
    def add_selected_granule(_, tile_layers, selected_granules, date, time):
        if is_granule_selected(selected_granules, date, time):
            # this granule being added already exists
            raise PreventUpdate

        view = create_granule_view(f"{date} {time}")
        selected_granules.append(view)
       
        return tile_layers, selected_granules
    
    
    def remove_selected_granule(_, uuid):
        print("was clicked: ", uuid)
        pass
