import requests

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

from utils import get_average_of_coordinates, rgb_url
from terracotta_toolbelt import singleband_url
from config import TC_URL

INSTRUMENT = "PACEPAX-AH2MAP-L1C"


def register_map_callbacks(app):
    @app.callback(
        [
            Output("tc", "url"),
            Output("cbar", "colorscale"),
            Output("cbar", "min"),
            Output("cbar", "max"),
            Output("cbar", "unit"),
            Output("map", "viewport"),
            Output("srng", "disabled"),
            Output("srng", "min"),
            Output("srng", "max"),
            Output("srng", "value"),
            Output("srng", "marks"),
            Output("dd_cmap", "disabled")
        ],
        [
            Input("date-picker", "date"),
            Input("granules", "value"),
            Input("dd_cmap", "value"),
            Input("srng", "value"),
            State("srng", "min"),
            State("srng", "max"),
            Input("dd_param", "value")
        ]
    )
    def configure_map_properties(date, time, cmap, srng, curr_min, curr_max, channel):
        if not date or not cmap or not time:
            raise PreventUpdate

        try:
            query_channel = channel
            is_combined_rgb = channel == "combined (rgb)"

            if is_combined_rgb:
                # since we are combing values from multiple channels
                # it does not make sense to respect stretch range since
                # each channel has its own range. we can default to red
                query_channel = "red"

            formatted_date = f"{date}_{time}"

            result = requests.get(
                f"{TC_URL}/metadata/{INSTRUMENT}/{formatted_date}/{query_channel}")
            metadata = result.json()

            mean = metadata["mean"]
            stdev = metadata["stdev"]

            if is_combined_rgb:
                min, max = 0, 100
            else:
                # TODO: min & max can be accessed via value_range
                #       however large changes in value across dataset
                #       in few areas is ruining the range causing it to
                #       be unecesarily large, fix?
                min, max = 0, mean + stdev

            bounds = metadata["convex_hull"]["coordinates"][0]
            zoom_point = get_average_of_coordinates(bounds)

            # swap lat, long
            zoom_point[0], zoom_point[1] = zoom_point[1], zoom_point[0]

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

            marks = {v: "{:.1f}".format(v) for v in new_stretch_range}

            if is_combined_rgb:
                url = rgb_url(TC_URL, INSTRUMENT, formatted_date, red_key="red",
                              green_key="green", blue_key="blue", stretch_range=new_stretch_range)
            else:
                url = singleband_url(TC_URL, INSTRUMENT, formatted_date, channel, colormap=cmap.lower(
                ), stretch_range=new_stretch_range)

            # two min-max exports, one for colorbar, one for slider
            return url, cmap, min, max, "radiance", viewport_status, False, min, max, new_stretch_range, marks, is_combined_rgb
        except:
            print(f"center_bounds: failed to retrieve metadata for {
                  INSTRUMENT}/{formatted_date}")
            raise PreventUpdate
