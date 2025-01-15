from dash import dcc, html
import dash_leaflet as dl
import datetime
from config import PARAMS

cmaps = ["Viridis", "Spectral", "Greys"]
chnls = ["Combined (RGB)", "Red", "Green", "Blue", "Infrared"]

def data_controller():
    return html.Div(
        style={"min-width": "200px", "right": "10px"},
        children=[
        html.H4("Parameters", style={"margin-bottom": "10px", "text-align": "center"}),
        html.Div("Date"),
        dcc.DatePickerSingle(
            id="date-picker",
            placeholder="Loading Datasets...",
            display_format="YYYY-MM-DD",
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center"
            },
            # disabled=True
        ),
        html.Div("Granule"),
        dcc.Dropdown(id="granules", disabled=True),
        html.Div(style={"margin-top": "10px", "margin-bottom": "10px", "width": "100%", "height": "2px", "background-color": "rgba(0, 0, 0, 0.15)"}),
        html.Div("Channels"),
        dcc.Dropdown(id="dd_param", options=[dict(value=c.lower(), label=c) for c in chnls], value=chnls[0].lower()),
        html.Br(),
        html.Div("Colorscale"),
        dcc.Dropdown(id="dd_cmap", options=[dict(value=c, label=c) for c in cmaps], value=cmaps[0]),
        html.Br(),
        html.Div("Opacity"),
        dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
        html.Br(),
        html.Div("Stretch range"),
        dcc.RangeSlider(id="srng", min=0, max=0, value=[0,0], disabled=True),
        html.Br(),
        html.Div("Value @ click position"),
        html.P(children="-", id="label"),
    ], className="info")
