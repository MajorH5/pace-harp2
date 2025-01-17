import datetime
from dash import html

DUMMY_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
DUMMY_TIME = datetime.datetime.now().strftime("%H:%M:%S")
DUMMY_AEROSOL_VALUE = 42.3
DUMMY_TEMPERATURE = 22.5
DUMMY_HUMIDITY = 65


def create_granule_data_view():
    return html.Div(
        style={"min-width": "200px", "right": "240px"},
        children=[
            html.Div(
                style={"width": "200px", "font-family": "Arial",
                       "font-size": "12px"},
                children=[
                    html.H4("PACE HARPV2 Measurement Data", style={
                        "margin-bottom": "10px", "text-align": "center"}),
                    html.P(f"Date: {DUMMY_DATE}"),
                    html.P(f"Time: {DUMMY_TIME}"),
                    html.P(f"Lat: 0.000, Lon: 0.000"),
                    html.P(f"Aerosol Value: {DUMMY_AEROSOL_VALUE} µg/m³"),
                    html.P(f"Temperature: {DUMMY_TEMPERATURE} °C"),
                    html.P(f"Humidity: {DUMMY_HUMIDITY} %"),
                    html.Img(
                        src="/assets/images/image.png",
                        alt="Map Data",
                        style={"width": "100%", "margin-top": "10px"}
                    ),
                    html.A(
                        "→ View image",
                        target="_blank",
                        href="https://aether.esi-nyx-mobile.cloud/pace-pax/Polarimeter/quicklook-l1c/v0-31-DEC-2024-selected/20240915/PACEPAX-AH2MAP_ER2_20240915T173319_R0_L1C_quicklook.png",
                        style={"fontSize": "1rem"}
                    )
                ]
            )
        ],
        className="info"
    )
