from dash import dcc, html

COLOR_MAPS = ["Viridis", "Spectral", "Greys"]
CHANNELS = ["Combined (RGB)", "Red", "Green", "Blue", "Infrared"]
GEO_LAYERS = {
    "Light": "light_nolabels",
    "Dark": "dark_nolabels",
    "Voyager": "voyager_no_labels_no_buildings"
}

def create_data_controller():
    return html.Div(
        style={"min-width": "200px", "right": "10px"},
        children=[
            html.H4("Parameters", style={
                    "margin-bottom": "10px", "text-align": "center"}),
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
                disabled=True
            ),
            html.Div("Granule"),
            dcc.Dropdown(id="granules", disabled=True),
            html.Div(style={"margin-top": "10px", "margin-bottom": "10px", "width": "100%",
                     "height": "2px", "background-color": "rgba(0, 0, 0, 0.15)"}),
            html.Div("Channels"),
            dcc.Dropdown(id="dd_param", options=[
                         dict(value=c.lower(), label=c) for c in CHANNELS], value=CHANNELS[0].lower()),
            html.Br(),
            html.Div("Colorscale"),
            dcc.Dropdown(id="dd_cmap", options=[
                         dict(value=c, label=c) for c in COLOR_MAPS], value=COLOR_MAPS[0]),
            html.Br(),
            html.Div("Geographical Layer"),
            dcc.Dropdown(
                id="geolayer_selector",
                options=[{"value": GEO_LAYERS[display_name], "label": display_name} for display_name in GEO_LAYERS.keys()],
                value=GEO_LAYERS["Light"],
            ),
            html.Br(),
            html.Div("Opacity"),
            dcc.Slider(id="opacity", min=0, max=1, value=0.5,
                       step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
            html.Br(),
            html.Div("Stretch range"),
            dcc.RangeSlider(id="srng", min=0, max=0, value=[0, 0], disabled=True)
        ], className="info")
