import json
import random
import urllib.request
import datetime
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

geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-73.97, 40.77],
                        [-73.98, 40.75],
                        [-73.95, 40.74],
                        [-73.96, 40.72],
                        [-73.97, 40.77]
                    ]
                ]
            },
            "properties": {
                "name": "Example Region"
            }
        }
    ]
}

cmaps = ["Viridis", "Spectral", "Greys"]
lbl_map = dict(wspd="Wind speed", temp="Temperature")
unit_map = dict(wspd="m/s", temp="°C")
srng_map = dict(wspd=[0, 10], temp=[-89.3, 56.7])
param0 = "temp"
cmap0 = "Viridis"
srng0 = srng_map[param0]
# App Stuff.
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.title = "UMBC | Geospatial Data Explorer"
app.layout = html.Div(
    children=[
    # Create the map itself.
    dl.Map(id="map", center=[56, 10], zoom=7, children=[
        dl.TileLayer(),
        dl.TileLayer(id="tc", opacity=0.5),
        dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
        dl.LayerGroup(id="layer-group"),
        dl.GeoJSON(
            id="geojson",
            data=geojson_data,
            hoverStyle={
                "color": "#FF0000",  # Change color on hover
                "weight": 5,  # Make the border thicker on hover
                "fillOpacity": 0.5  # Change fill opacity on hover
            },
            children=dl.Tooltip("Hover to see details")
        )
    ], style={"width": "100%", "height": "100%"}),
    granule_data(),
    data_controller(),
    branding()
], style={"display": "grid", "width": "100%", "height": "100vh"})


whitelist_dates = [
    datetime.date(2025, 1, 5),
    datetime.date(2025, 1, 10),
    datetime.date(2025, 1, 15),
    datetime.date(2025, 1, 20),
]

@app.callback(
    Output("date-picker", "is_day_disabled"),
    Input("date-picker", "date"),
)
def disable_non_whitelisted_dates(selected_date):
    def is_disabled(date):
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        return date_obj not in whitelist_dates

    return is_disabled

@app.callback(
    [Output("tc", "opacity")],
    [Input("opacity", "value")]
)
def update_opacity(opacity):
    return [opacity]

@app.callback([Input("geojson", "clickData")])
def on_mouse_event(hoverData):
    print("hover data: ", hoverData)


@app.callback(
    [Output("srng", "min"), Output("srng", "max"), Output("srng", "value"), Output("srng", "marks")],
    [Input("dd_param", "value")]
)
def update_stretch_range(param):
    if not param:
        return PreventUpdate
    srng = srng_map[param]
    return srng[0], srng[1], srng, {v: "{:.1f}".format(v) for v in srng}


@app.callback(
    [Output("tc", "url"), Output("cbar", "colorscale"),
     Output("cbar", "min"), Output("cbar", "max"), Output("cbar", "unit")],
    [Input("dd_param", "value"), Input("dd_cmap", "value"), Input("srng", "value")]
)
def update_url(param, cmap, srng):
    if not param or not cmap:
        raise PreventUpdate
    srng = [float(item) for item in srng]
    url = singleband_url(TC_URL, GFS_KEY, param, colormap=cmap.lower(), stretch_range=srng)
    return url, cmap, float(srng[0]), float(srng[1]), unit_map[param]


# @app.callback(Output("label", "children"), [Input("map", 'click_lat_lng'), Input("dd_param", "value")])
# def update_label(click_lat_lng, param):
#     print(click_lat_lng)
#     if not click_lat_lng:
#         return "-"
#     url = point_url(TC_URL, GFS_KEY, param, lat=click_lat_lng[0], lon=click_lat_lng[1])
#     data = json.load(urllib.request.urlopen(url))
#     return "{:.3f} {}".format(float(data), unit_map[param])

# @app.callback(
#         [Output("layer-group", "children"),
#         Output("marker-store", "children")],
#         [Input('map', 'n_clicks'),
#         State("map", 'clickData'),
#         Input("marker-store", "data")]
# )
# def onclick(total_clicks, click_data, markers):    
#     lat, lon = click_data['latlng']['lat'], click_data['latlng']['lon']
#     marker = dl.Marker(position=[lat, lon], children=dl.Tooltip(f"Lat: {lat}, Lon: {lon}"))
#     markers.append(marker)

#     print('yadda')
#     return markers, markers


@app.callback(
        [Output("label", "children"), Output("layer-group", "children")],
        [Input("dd_param", "value"), Input('map', 'n_clicks')],
        [State("map", 'clickData')]
)
def onclick(param, total_clicks, click_data):
    DUMMY_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    DUMMY_TIME = datetime.datetime.now().strftime("%H:%M:%S")
    DUMMY_AEROSOL_VALUE = 42.3
    DUMMY_TEMPERATURE = 22.5  # in °C
    DUMMY_HUMIDITY = 65  # in %
    
    if click_data == None:
        return "-", dl.Popup()

    lat, lon = click_data['latlng']['lat'], click_data['latlng']['lng']

    url = point_url(TC_URL, GFS_KEY, param, lat=lat, lon=lon)
    # TODO: how to access live data for TC server? there is no "/point" endpoint in the docs as this template suggests
    # data = json.load(urllib.request.urlopen(url))
    data = random.random()
    value_formatted = "{:.3f} {}".format(float(data), unit_map[param])
    
    dash_component = dl.Popup(
        position=[lat, lon],
        children=html.Div(
            style={"width": "200px", "font-family": "Arial", "font-size": "12px"},
            children=[
                html.H4("PACE HARPV2 Measurement Data", style={"margin-bottom": "10px", "text-align": "center"}),
                html.P(f"Date: {DUMMY_DATE}"),
                html.P(f"Time: {DUMMY_TIME}"),
                html.P(f"Lat: {lat:.3f}, Lon: {lon:.3f}"),
                html.P(f"Aerosol Value: {DUMMY_AEROSOL_VALUE} µg/m³"),
                html.P(f"Temperature: {DUMMY_TEMPERATURE} °C"),
                html.P(f"Humidity: {DUMMY_HUMIDITY} %"),
                html.Img(
                    src="/assets/image.png",
                    alt="Map Data",
                    style={"width": "100%", "margin-top": "10px"}
                ),
                html.A(
                    "https://aether.esi-nyx-mobile.cloud/pace-pax/Polarimeter/quicklook-l1c/v0-31-DEC-2024-selected/20240915/PACEPAX-AH2MAP_ER2_20240915T173319_R0_L1C_quicklook.png",
                    target="_blank",
                    href="https://aether.esi-nyx-mobile.cloud/pace-pax/Polarimeter/quicklook-l1c/v0-31-DEC-2024-selected/20240915/PACEPAX-AH2MAP_ER2_20240915T173319_R0_L1C_quicklook.png",
                    style={ "fontSize": "1rem" }
                    )
            ]
        )
    )
    return value_formatted, dash_component


if __name__ == '__main__':
    app.run_server(port=8050)
