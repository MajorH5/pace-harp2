import dash_leaflet as dl
from dash import html

from .branding import create_branding
from .data_controller import create_data_controller
from .granule_data_view import create_granule_data_view


def create_root():
    """
    Returns the root layout for the application
    """

    return html.Div(
        children=[
            dl.Map(id="map", center=[56, 10], zoom=7, children=[
                dl.TileLayer(),
                dl.TileLayer(id="tc", opacity=0.5),
                dl.Colorbar(id="cbar", width=150, height=20, style={
                    "margin-left": "40px"}, position="bottomleft"),
                dl.LayerGroup(id="layer-group")
            ], style={"width": "100%", "height": "100%"}),
            # create_granule_data_view(),
            create_data_controller(),
            create_branding()
        ], style={"display": "grid", "width": "100%", "height": "100vh"})