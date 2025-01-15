import json
import random
import requests
from datetime import datetime
from utils import get_date_range, get_average_of_coordinates
import dash
from dash import html
from dash import dcc
import dash_leaflet as dl

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from flask import Flask
from config import TC_URL, GFS_KEY, PARAMS
from terracotta_toolbelt import singleband_url, point_url

from components.granule_data import granule_data
from components.data_controller import data_controller
from components.branding import branding

unit_map = dict(wspd="m/s", temp="°C")
srng_map = dict(wspd=[0, 10], temp=[-89.3, 56.7])

server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.title = "UMBC | Geospatial Data Explorer"
app.layout = html.Div(
    children=[
    dl.Map(id="map", center=[56, 10], zoom=7, children=[
        dl.TileLayer(),
        dl.TileLayer(id="tc", opacity=0.5),
        dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
        dl.LayerGroup(id="layer-group")
    ], style={"width": "100%", "height": "100%"}),
    # granule_data(),
    data_controller(),
    branding()
], style={"display": "grid", "width": "100%", "height": "100vh"})

@app.callback(
    [Output("date-picker", "disabled_days"),
     Output("date-picker", "min_date_allowed"), Output("date-picker", "max_date_allowed"),
     Output("date-picker", "disabled"), Output("date-picker", "placeholder"),
     Output("granules", "options"), Output("granules", "disabled")],
    [Input("date-picker", "display_format"), Input("date-picker", "date")],
)
def disable_nodata_days(_, selected_date):
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

@app.callback(
    [Output("tc", "opacity")],
    [Input("opacity", "value")]
)
def update_opacity(opacity):
    return [opacity]

# @app.callback(
#     [Output("srng", "min"), Output("srng", "max"), Output("srng", "value"), Output("srng", "marks")],
#     [Input("dd_param", "value")]
# )
# def update_stretch_range(param):
#     if not param:
#         return PreventUpdate
#     srng = srng_map[param]
#     return srng[0], srng[1], srng, {v: "{:.1f}".format(v) for v in srng}

@app.callback(
    [Output("tc", "url"), Output("cbar", "colorscale"),
     Output("cbar", "min"), Output("cbar", "max"),
    #  Output("srng", "min"), Output("srng", "max"),
     Output("cbar", "unit"), Output("map", "viewport"),
     Output("srng", "disabled"), Output("srng", "min"),
     Output("srng", "max"), Output("srng", "value"),
     Output("srng", "marks")
    ],
    [Input("date-picker", "date"), Input("granules", "value"), Input("dd_cmap", "value"), Input("srng", "value"),
     State("srng", "min"), State("srng", "max")]
)
def update_url(date, time, cmap, srng, curr_min, curr_max):
    INSTRUMENT = "PACEPAX-AH2MAP-L1C"

    if not date or not cmap or not time:
        raise PreventUpdate

    try:
        formatted_date = f"{date}_{time}"

        result = requests.get(f"{TC_URL}/metadata/{INSTRUMENT}/{formatted_date}")
        metadata = result.json()
        
        value_range = metadata["range"]
        mean = metadata["mean"]
        stdev = metadata["stdev"]

        # TODO: min & max can be accessed via value_range
        #       however large changes in value across dataset
        #       in few areas is ruining the range causing it to
        #       be unecesarily large, fix?
        min, max = 0, mean + stdev

        bounds = metadata["convex_hull"]["coordinates"][0]
        zoom_point = get_average_of_coordinates(bounds)

        temp = zoom_point[0]
        zoom_point[0] = zoom_point[1]
        zoom_point[1] = temp

        viewport_status = {
            "center": zoom_point,
            "transition": "flyTo",
            "zoom": 10
        }

        new_stretch_range = srng

        is_new_range = curr_min != min or curr_max != max

        if is_new_range:
            # just use our own computed min, max
            new_stretch_range = [min, max]

        marks = { v: "{:.1f}".format(v) for v in new_stretch_range }

        url = singleband_url(TC_URL, INSTRUMENT, formatted_date, colormap=cmap.lower(), stretch_range=new_stretch_range)

        # two min-max exports, one for colorbar, one for slider
        return url, cmap, min, max, "radiance", viewport_status, False, min, max, new_stretch_range, marks
    except:
        print(f"center_bounds: failed to retrieve metadata for {INSTRUMENT}/{formatted_date}")
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
