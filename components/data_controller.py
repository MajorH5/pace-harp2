from dash import dcc, html
import dash_leaflet as dl
from config import PARAMS

cmaps = ["Viridis", "Spectral", "Greys"]
lbl_map = dict(wspd="Wind speed", temp="Temperature")
unit_map = dict(wspd="m/s", temp="°C")
srng_map = dict(wspd=[0, 10], temp=[-89.3, 56.7])
param0 = "temp"
cmap0 = "Viridis"
srng0 = srng_map[param0]

def data_controller():
    return html.Div(
        style={"min-width": "200px"},
        children=[
        html.Div("Date"),
        dcc.DatePickerSingle(
            id="date-picker",
            date="2025-01-01",
            display_format="YYYY-MM-DD",
            min_date_allowed="2024-12-01",
            max_date_allowed="2025-12-05",
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center"
            }
        ),
        html.Div(style={"margin-top": "10px", "margin-bottom": "10px", "width": "100%", "height": "2px", "background-color": "rgba(0, 0, 0, 0.15)"}),
        html.Div("Bands"),
        dcc.Dropdown(id="dd_param", options=[dict(value=p, label=lbl_map[p]) for p in PARAMS], value=param0),
        html.Br(),
        html.Div("Colorscale"),
        dcc.Dropdown(id="dd_cmap", options=[dict(value=c, label=c) for c in cmaps], value=cmap0),
        html.Br(),
        html.Div("Opacity"),
        dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
        html.Br(),
        html.Div("Stretch range"),
        dcc.RangeSlider(id="srng", min=srng0[0], max=srng0[1], value=srng0,
                        marks={v: "{:.1f}".format(v) for v in srng0}),
        html.Br(),
        html.Div("Value @ click position"),
        html.P(children="-", id="label"),
    ], className="info")