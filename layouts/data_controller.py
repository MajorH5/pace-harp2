from dash import dcc, html

COLOR_MAPS = ["Viridis", "Spectral", "Greys"]
CHANNELS = ["Combined (RGB)", "Red", "Green", "Blue", "Infrared"]
GEO_LAYERS = {
    "Light": "light_nolabels",
    "Dark": "dark_nolabels",
    "Voyager": "voyager_no_labels_no_buildings"
}


def create_granule_view(time):
    return html.Div(
        style={"display": "flex", "alignItems": "center", "marginBottom": "5px"},
        children=[
            html.Span(time, style={"flex": "1"}),
            html.Button("X", id={"type": "remove-granule", "index": 1}, n_clicks=0, className="button",
                        style={"backgroundColor": "rgba(255,0,0,0.10)"})
        ]
    )


def create_data_controller():
    return html.Div(
        style={"minWidth": "200px", "right": "10px"},
        children=[
            html.H4("Parameters", style={
                "marginBottom": "10px", "textAlign": "center"}),
            html.Div("Date"),
            dcc.DatePickerSingle(
                id="date-picker",
                placeholder="Loading Datasets...",
                display_format="YYYY-MM-DD",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                disabled=True
            ),
            html.Div("Granules"),
            html.Div([
                dcc.Dropdown(
                    id="granules",
                    placeholder="Select a granule",
                    disabled=True,
                    style={"flex": "1"}
                ),
                html.Button("+", id="add-granule-btn", className="button", n_clicks=0, disabled=True, style={
                    "marginLeft": "10px",
                    "flex": "0.15"
                })
            ], style={"display": "flex", "justifyContent": "spaceBetween", "width": "100%", "alignItems": "center", "marginBottom": "10px"}),
            html.Div("Selected Granules"),
            html.Div(id="selected-granules-list", children=[
                # TODO: remove testing views
                create_granule_view("01/12/24 18:42:31"),
                # create_granule_view("05/30/24 03:33:13"),
                # create_granule_view("02/05/24 02:27:18"),
                # create_granule_view("12/03/23 09:01:53"),
            ], style={
                "border": "1px solid #ccc",
                "padding": "10px",
                "borderRadius": "5px",
                "maxHeight": "100px",
                "overflowY": "auto"
            }),
            html.Div(style={"marginTop": "10px", "marginBottom": "10px", "width": "100%",
                            "height": "2px", "backgroundColor": "rgba(0, 0, 0, 0.15)"}),
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
                options=[{"value": GEO_LAYERS[display_name], "label": display_name}
                         for display_name in GEO_LAYERS.keys()],
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
