import requests
from math import floor

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

from utils import get_average_of_coordinates, combine_url
from terracotta_toolbelt import singleband_url
from config import TC_DEFAULT_URL

RGB_KEYS = ["red", "green", "blue"]

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
            Input("dd_param", "value"),
            Input("campaign_selector", "value"),
            Input("instrument_selector", "value"),
            Input("level_selector", "value"),
            State("selected-granules-list", "children")
        ]
    )
    def configure_map_properties(date, time, cmap, srng, curr_min, curr_max,
        channel, campaign, instrument, level, selected_granules):
        if any(arg == None for arg in [date, cmap, time, campaign, instrument, level]):
            raise PreventUpdate

        query_granules = []

        for view in selected_granules:
            selected_date, selected_time = view["props"]["id"].split(" ")
            query_granules.append((selected_date, selected_time))
        
        if (date, time) not in query_granules:
            query_granules.append((date, time))

        # try:
            query_channel = channel
            is_combined_rgb = channel == "combined (rgb)"

            if is_combined_rgb:
                # since we are combing values from multiple channels
                # it does not make sense to respect stretch range since
                # each channel has its own range. we can default to red
                query_channel = "red"

            formatted_date = f"{date}_{time}"

            result = requests.get(
                f"{TC_DEFAULT_URL}/metadata/{campaign}/{instrument}/{formatted_date}/{level}/{query_channel}")
            metadata = result.json()

            mean = metadata["mean"]
            stdev = metadata["stdev"]

            if is_combined_rgb:
                min, max = 0, 100
            else:
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

            marks = {floor(v): "{:.1f}".format(v) for v in new_stretch_range}

            query_granules = [f"{campaign}/{instrument}/{"_".join(g)}/{level}" for g in query_granules]
            rgb_keys = RGB_KEYS if is_combined_rgb else None

            url = combine_url(TC_DEFAULT_URL, query_granules, rgb_keys)

            # if is_combined_rgb:
            #     url = rgb_url(TC_URL, campaign, instrument, formatted_date, level, red_key="red",
            #                   green_key="green", blue_key="blue", stretch_range=new_stretch_range)
            # else:
            #     url = singleband_url(TC_URL, campaign, instrument, formatted_date, level, channel, colormap=cmap.lower(
            #     ), stretch_range=new_stretch_range)

            # two min-max exports, one for colorbar, one for slider
            return url, cmap, min, max, "radiance", viewport_status, False, min, max, new_stretch_range, marks, is_combined_rgb
        # except Exception as e:
        #     print(f"center_bounds: failed to retrieve metadata for {instrument}/{formatted_date}")
        #     print(e)
        #     raise PreventUpdate
